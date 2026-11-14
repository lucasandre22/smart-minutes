"""Publish the prepared review using an authenticated GitHub CLI (no Python dependencies)."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
TOPICS = sorted((ROOT / "docs" / "backend-review").glob("[0-9][0-9]-*.md"))
BRANCH = "chore/backend-review-issue-tracking"
PR_TITLE = "Add issue reporting templates and backend review trackers"


def find_gh():
    executable = shutil.which("gh")
    if not executable and os.name == "nt":
        candidate = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "GitHub CLI" / "gh.exe"
        if candidate.is_file():
            executable = str(candidate)
    if not executable:
        raise RuntimeError("GitHub CLI is unavailable. Install gh and authenticate with gh auth login.")
    return executable


def run_gh(executable, *arguments):
    result = subprocess.run(
        [executable, *arguments], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", timeout=120,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "GitHub CLI command failed.")
    return result.stdout.strip()


def api(executable, endpoint, payload=None, paginate=False):
    arguments = ["api", endpoint]
    if paginate:
        arguments.extend(["--paginate", "--slurp"])
    if payload is None:
        return json.loads(run_gh(executable, *arguments))
    with tempfile.TemporaryDirectory(prefix="smart-minutes-github-") as directory:
        path = Path(directory) / "request.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        arguments.extend(["--method", "POST", "--input", str(path)])
        return json.loads(run_gh(executable, *arguments))


def validate():
    if len(TOPICS) != 6:
        raise RuntimeError("Expected exactly six prepared topic bodies.")
    findings = []
    for path in TOPICS:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("# [Backend review]: "):
            raise RuntimeError(f"Invalid topic title: {path.name}")
        ids = re.findall(r"^- \[ \] \*\*F(\d{3}) - ", content, re.MULTILINE)
        findings.extend(map(int, ids))
        print(f"{path.name}: {len(ids)} findings", flush=True)
    if sorted(findings) != list(range(1, 75)):
        raise RuntimeError("Finding coverage must be exactly F001-F074 without duplicates.")
    print("Validated six topics and all 74 findings.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="lucasandre22/smart-minutes")
    parser.add_argument("--dry-run", action="store_true", help="Validate local bodies without network access.")
    args = parser.parse_args()
    validate()
    if args.dry_run:
        return

    gh = find_gh()
    repository = json.loads(run_gh(
        gh, "repo", "view", args.repo, "--json", "nameWithOwner,defaultBranchRef,hasIssuesEnabled",
    ))
    if not repository["hasIssuesEnabled"]:
        raise RuntimeError("Repository issues are disabled. No changes made.")
    repo = repository["nameWithOwner"]
    base = repository["defaultBranchRef"]["name"]
    pages = api(gh, f"repos/{repo}/issues?state=all&per_page=100", paginate=True)
    issues = [issue for page in pages for issue in page if "pull_request" not in issue]
    label_pages = api(gh, f"repos/{repo}/labels?per_page=100", paginate=True)
    if not any(label["name"] == "backend-review" for page in label_pages for label in page):
        api(gh, f"repos/{repo}/labels", {
            "name": "backend-review", "color": "1D76DB",
            "description": "Findings and topic trackers from the Python backend review",
        })

    published = []
    for path in TOPICS:
        content = path.read_text(encoding="utf-8")
        title = content.splitlines()[0][2:]
        matches = [issue for issue in issues if issue["title"] == title]
        if len(matches) > 1:
            raise RuntimeError(f"Multiple existing issues match {title}; resolve duplicates before retrying.")
        if matches:
            issue = matches[0]
            print(f"Reusing existing topic: {issue['html_url']}", flush=True)
        else:
            issue = api(gh, f"repos/{repo}/issues", {
                "title": title, "body": content.split("\n", 1)[1].lstrip(),
                "labels": ["backend-review"],
            })
            print(f"Created topic: {issue['html_url']}", flush=True)
        published.append((path, issue))

    # Do not overwrite existing issue checklists/comments when retrying publication.
    index_path = ROOT / "docs" / "backend-review" / "README.md"
    index = index_path.read_text(encoding="utf-8")
    guide_path = ROOT / ".github" / "ISSUE_REPORTING.md"
    guide = guide_path.read_text(encoding="utf-8")
    for path, issue in published:
        topic_name = issue["title"].removeprefix("[Backend review]: ")
        index = index.replace(f"]({path.name})", f"]({issue['html_url']})")
        guide = guide.replace(f"| {topic_name} |", f"| [{topic_name}]({issue['html_url']}) |")
    start = index.index("## Publication status")
    end = index.index("## Validation", start)
    index = index[:start] + (
        "## Publication status\n\n"
        "The six topic issues are published; the table above links to their live checklists. "
        "The numbered Markdown files preserve the original issue bodies. "
        "Use GitHub issue checklists as the working source of completion status.\n\n"
        "Issue reporting forms and the [reporting guide](../../.github/ISSUE_REPORTING.md) "
        "become available in GitHub's new-issue chooser after the setup pull request is merged "
        "into the default branch.\n\n"
    ) + index[end:]
    index_path.write_text(index, encoding="utf-8")
    guide_path.write_text(guide, encoding="utf-8")

    matching_refs = api(gh, f"repos/{repo}/git/matching-refs/heads/{BRANCH}")
    existing = next((ref for ref in matching_refs if ref["ref"] == f"refs/heads/{BRANCH}"), None)
    if existing:
        parent_sha = existing["object"]["sha"]
    else:
        parent_sha = api(gh, f"repos/{repo}/git/ref/heads/{base}")["object"]["sha"]
    parent = api(gh, f"repos/{repo}/git/commits/{parent_sha}")
    files = sorted((ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml"))
    files += [guide_path, Path(__file__).resolve(), index_path, *TOPICS]
    tree = api(gh, f"repos/{repo}/git/trees", {
        "base_tree": parent["tree"]["sha"],
        "tree": [{"path": path.relative_to(ROOT).as_posix(), "mode": "100644",
                  "type": "blob", "content": path.read_text(encoding="utf-8")} for path in files],
    })
    if tree["sha"] != parent["tree"]["sha"]:
        commit = api(gh, f"repos/{repo}/git/commits", {
            "message": PR_TITLE, "tree": tree["sha"], "parents": [parent_sha],
        })
        if existing:
            # Updating an existing ref requires PATCH, and never forces history.
            with tempfile.TemporaryDirectory(prefix="smart-minutes-ref-") as directory:
                payload = Path(directory) / "ref.json"
                payload.write_text(json.dumps({"sha": commit["sha"], "force": False}), encoding="utf-8")
                run_gh(gh, "api", f"repos/{repo}/git/refs/heads/{BRANCH}",
                       "--method", "PATCH", "--input", str(payload))
        else:
            api(gh, f"repos/{repo}/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": commit["sha"]})

    pull_requests = json.loads(run_gh(
        gh, "pr", "list", "--repo", repo, "--head", BRANCH,
        "--state", "open", "--json", "number,title,url",
    ))
    if pull_requests:
        print(f"Setup pull request: {pull_requests[0]['url']}", flush=True)
    else:
        body = (
            "Add required-field issue forms for bugs, improvements, and topic trackers, "
            "plus a reporting and triage guide. Disable blank reports so new issues follow a consistent structure.\n\n"
            "Preserve all 74 backend review findings in six topic bodies and link the published issues "
            "from the backlog index and reporting guide. No backend runtime behavior changes.\n\n"
            "Validation: six topic files cover F001-F074 exactly once; source file/line references "
            "and all four YAML files were validated locally. Templates activate when this PR is merged.\n\n"
            "Published topics:\n" + "\n".join(f"- {issue['html_url']}" for _, issue in published)
        )
        with tempfile.TemporaryDirectory(prefix="smart-minutes-pr-") as directory:
            path = Path(directory) / "body.md"
            path.write_text(body, encoding="utf-8")
            url = run_gh(gh, "pr", "create", "--repo", repo, "--base", base,
                         "--head", BRANCH, "--title", PR_TITLE, "--body-file", str(path))
            print(f"Setup pull request: {url}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired, OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
