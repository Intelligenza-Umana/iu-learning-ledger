# Changelog

Project attribution: identified as an Intelligenza Umana project in the README.

Documentation update: corrected repository links and clarified the working directory for CLI examples.

Publication readiness: switched repository links to the `Intelligenza-Umana` organization and validated the plugin and marketplace manifests with `claude plugin validate` (Claude Code 2.1.332), including the plugin directory profile with `--strict`.

## 1.0.0
- `explain` skill: explains existing or generated code decision by decision, critiques weak choices and asks for a teach-back.
- `pair` skill: the learner writes, Claude asks reasoning questions, reviews each piece and challenges choices.
- Spring Security topic pack (10 topics).
- `study-today`, `practice` and `log-session` know about the new skills.
- Skill structure tests. Ledger file formats and `ledger.py` JSON output are stable from this version.

## 0.2.2
- README: note about installing Python 3 on Windows.

## 0.2.1
- Skills find a working Python 3 (`python3`, `python` or `py`) instead of assuming `python3`, which on Windows is often a non-working Store stub. They stop with a clear message if none is found.

## 0.2.0
- `report` command and `weekly-report` skill.
- Sessions now store the level before each result (`from`) so reports can show movement.
- Topic packs: Python, SQL/databases, system design, DevOps basics (plus Java/Spring).
- CI, contributing guide, issue templates.

## 0.1.0
- Initial release: `ledger.py`, skills `study-today`, `quiz`, `practice`, `log-session`.
