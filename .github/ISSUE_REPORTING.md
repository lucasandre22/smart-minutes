# Reporting issues

1. Search open and closed issues for the same problem. Add evidence to an existing issue instead of duplicating it.
2. Choose **Bug report** for incorrect behavior, **Improvement or gap** for a proposed change, or **Topic tracker** for a group of related findings.
3. Use a concrete title describing the affected behavior. Complete the required fields with minimal, sanitized evidence; explain when a failure is inferred from code rather than reproduced.
4. Include the reviewed commit, environment, expected and actual behavior, reproduction steps or code path, impact, and observable completion criteria. Include model and generation settings when relevant.
5. Keep bug reports and improvements independently reviewable. Link their parent topic and finding ID when they implement part of a topic tracker.
6. Never include credentials, private meeting documents, or identifying transcript content. Use synthetic fixtures and sanitized logs.

## Backend review tracking

The initial backend review has 74 findings across six topic trackers. IDs F001 through F074 map directly to the numbered review findings and must remain stable.

| Topic | Findings |
| --- | --- |
| [Critical and high-impact defects](https://github.com/lucasandre22/smart-minutes/issues/2) | F001-F010 |
| [API, validation, and operational gaps](https://github.com/lucasandre22/smart-minutes/issues/3) | F011-F020 |
| [Generation behavior and output quality](https://github.com/lucasandre22/smart-minutes/issues/4) | F021-F034 |
| [Documents, retrieval, and storage](https://github.com/lucasandre22/smart-minutes/issues/5) | F035-F047 |
| [Parsing and evaluation defects](https://github.com/lucasandre22/smart-minutes/issues/6) | F048-F060 |
| [Maintainability, configuration, and test gaps](https://github.com/lucasandre22/smart-minutes/issues/7) | F061-F074 |

Treat these as work queues, not claims that every concern has been reproduced. Each tracker records its validation limits. Before implementation, recheck its source references against the current code.

## Maintainer workflow

- Triage impact and dependencies before scheduling. Prioritize filesystem containment, broken workflows, task isolation, and storage consistency.
- Split a finding into a focused implementation issue only when useful; link it back to its topic rather than creating duplicate topic trackers.
- Require a linked fix and appropriate validation before checking a finding off. If a finding is invalid or intentionally deferred, document the evidence or rationale explicitly.
- Close a topic only when every finding has a recorded disposition and its completion criteria are satisfied.
- Issue forms and this guide become available from GitHub's new-issue chooser after they are merged into the repository's default branch.
