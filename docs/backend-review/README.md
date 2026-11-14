# Backend review issue backlog

Review baseline: [`c4808c01d8b08b800fbddcc02547afb2701554eb`](https://github.com/lucasandre22/smart-minutes/commit/c4808c01d8b08b800fbddcc02547afb2701554eb). The review covers Python backend code only.

The following files are the complete bodies for six GitHub topic issues. Their first heading is the intended issue title. Finding IDs map directly to the original numbered review and appear exactly once across the six bodies.

| Topic issue body | Finding IDs | Count |
| --- | --- | --- |
| [Critical and high-impact defects](https://github.com/lucasandre22/smart-minutes/issues/2) | F001-F010 | 10 |
| [API, validation, and operational gaps](https://github.com/lucasandre22/smart-minutes/issues/3) | F011-F020 | 10 |
| [Generation behavior and output quality](https://github.com/lucasandre22/smart-minutes/issues/4) | F021-F034 | 14 |
| [Documents, retrieval, and storage](https://github.com/lucasandre22/smart-minutes/issues/5) | F035-F047 | 13 |
| [Parsing and evaluation defects](https://github.com/lucasandre22/smart-minutes/issues/6) | F048-F060 | 13 |
| [Maintainability, configuration, and test gaps](https://github.com/lucasandre22/smart-minutes/issues/7) | F061-F074 | 14 |
| **Total** | **F001-F074** | **74** |

## Publication status

The six topic issues are published; the table above links to their live checklists. The numbered Markdown files preserve the original issue bodies. Use GitHub issue checklists as the working source of completion status.

Issue reporting forms and the [reporting guide](../../.github/ISSUE_REPORTING.md) become available in GitHub's new-issue chooser after the setup pull request is merged into the default branch.

## Validation

- The six bodies contain all 74 findings exactly once, with stable IDs.
- Source links are pinned to the review baseline; each referenced local file and line exists.
- The three issue forms and their chooser configuration parse as YAML.
- Backend runtime behavior was not changed by preparing this backlog.

Each topic records its own evidence, limitations, dependencies, and completion criteria. A checked finding requires a linked fix and validation, or an explicit evidence-based disposition. The GitHub issue checklist should become the working source of completion status after publication.
