# learning-ledger 1.0.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `explain` and `pair` skills, a Spring Security topic pack and the 1.0.0 release material, without changing the ledger rules.

**Architecture:** The ledger script stays as it is. The new behavior is two markdown skills that follow the same conventions as the existing ones (Python lookup snippet, evidence reporting, no ledger writes outside `log-session`). Structure tests guard the skills; one ledger test pins how an `explain` session is capped.

**Tech Stack:** Markdown skills, Python 3 standard library (`unittest`), JSON topic packs.

**Spec:** `docs/superpowers/specs/2026-11-16-learning-ledger-1.0-design.md`

## Global Constraints

- Python 3 standard library only. No dependencies, no network.
- `ledger.py` logic (levels, caps, intervals) is not modified. File formats of `topics.json`, `sessions.jsonl`, `config.json` are unchanged.
- Skills are written in English like the existing ones, and tell Claude to answer in the user's language.
- `explain` sessions are logged with `support: full_solution` and `evidence: observed_answers`, and only when a teach-back happened.
- `pair` sessions are logged with `type: exercise`, `evidence: observed_exercise` or `reviewed_code`, and `support` equal to the strongest help actually given.
- No secrets in summaries; skills never commit or push.
- Work on branch `ccr-8058e74e-hy0f34`, never on `main`. Commit after each task (Fabio's stop hook requires committed and pushed work).
- `README.md` at the repo root and `plugins/learning-ledger/README.md` are identical today; keep them identical.

## Review Focus

- A skill folder without `SKILL.md`, or with a `name` that differs from its folder: pinned by the structure test (Task 1).
- `explain` called with no ledger and no Python: it must still work (explanation does not need the ledger). Pinned by a content test on the "no Python" wording (Task 1).
- `explain` asked to explain code in a directory that is not a git repo: it must not fail on `git diff`; pinned by a wording test (Task 1).
- A learner claiming `autonomous` after an `explain` session: capped to `with_support` (Task 3).
- The new pack imported twice or together with `java-spring`: no id collisions, second import skips everything (Task 4).

---

### Task 1: Skill structure tests and the `explain` skill

**Files:**
- Create: `tests/test_skills.py`
- Create: `plugins/learning-ledger/skills/explain/SKILL.md`

**Interfaces:**
- Produces: `tests/test_skills.py` helpers `read_skill(name) -> (frontmatter: dict[str, str], body: str)`; later tasks add assertions to this file. Constant `SKILLS_DIR` (Path to `plugins/learning-ledger/skills`).

- [ ] **Step 1: Write the failing tests in `tests/test_skills.py`**
  - `test_every_skill_folder_has_matching_frontmatter`: for each dir in `SKILLS_DIR`, `SKILL.md` exists, frontmatter has `name == folder name` and a non-empty `description` of at most 1024 characters.
  - `test_expected_skill_set`: folder names equal `{"explain","log-session","pair","practice","quiz","study-today","weekly-report"}`.
  - `test_explain_contract`: body of `explain` contains each of: `full_solution`, `observed_answers`, `teach-back`, `git diff`, `unverified`, `bug`, `risk`, `how would you tell it` (case-insensitive), `${CLAUDE_PLUGIN_ROOT}`; and the phrase `answer in the user's language`; and a sentence saying that without a git repository it reads the files directly (assert the substring `not a git repository`).
- [ ] **Step 2: Run** `python3 -m unittest tests.test_skills -v`. Expected: FAIL (`pair` and `explain` missing).
- [ ] **Step 3: Write `skills/explain/SKILL.md`.** Frontmatter `name: explain`, a `description` that says: explains existing or newly generated code decision by decision with reasons, alternatives and checks, then asks the learner to teach it back; triggers: "explain this", "why did it do this", "walk me through", "write X and explain it". Body sections, in this order:
  1. Role and the Python lookup snippet (same snippet and "if `$PY` is empty, skip the ledger" wording as `practice`).
  2. **Pick the entry point**: (a) explain existing code (use `git diff` / `git status` when asked about what was just written, and say it is not a git repository and read the files directly when `git` fails); (b) generate with explanation (list decisions with alternatives and a recommendation first, wait for the learner's pick when the choice is real, then write and explain each piece, then say how to verify).
  3. **For each decision, in runtime order**: what it does; why it exists; how it works at runtime on a real request; alternatives and trade-offs; what breaks if removed; how to verify. Anchor to `file:line` of the project.
  4. **Honest critique**: classify weak choices as bug / risk / optional improvement / style; say plainly when the code is correct; verify library facts with a docs tool (for example Context7) when available and mark anything not checked as **unverified**.
  5. **Ending**: a 4-5 sentence "how would you tell it" version, then ask the learner to redo 1-3 points in their own words (teach-back), grade with the 30-point rubric from `quiz`, then offer `/learning-ledger:log-session` with `support: full_solution`, `evidence: observed_answers`, only if the teach-back happened. State that a level above `with_support` needs a later unaided `quiz` or `pair`.
  6. **Rules**: read-only except code the learner asked to generate; answer in the user's language; no praise filler; no secrets; no ledger writes, no commits.
- [ ] **Step 4: Run** `python3 -m unittest tests.test_skills -v`. Expected: `test_explain_contract` passes; `test_expected_skill_set` still fails until Task 2.
- [ ] **Step 5: Commit** `git add tests/test_skills.py plugins/learning-ledger/skills/explain && git commit -m "feat: explain skill and skill structure tests"`.

---

### Task 2: The `pair` skill

**Files:**
- Create: `plugins/learning-ledger/skills/pair/SKILL.md`
- Modify: `tests/test_skills.py`

**Interfaces:**
- Consumes: `read_skill(name)` from Task 1.

- [ ] **Step 1: Add `test_pair_contract` to `tests/test_skills.py`:** body of `pair` contains `one question at a time` (case-insensitive), `exercise`, `observed_exercise`, `reviewed_code`, `full_solution`, `guiding question`, `defend`, `bug`, `risk`, `${CLAUDE_PLUGIN_ROOT}`, and `answer in the user's language`; and does **not** contain the word `commit` outside a sentence that forbids it (assert the string `never commit` is present).
- [ ] **Step 2: Run** `python3 -m unittest tests.test_skills -v`. Expected: FAIL (`pair` missing).
- [ ] **Step 3: Write `skills/pair/SKILL.md`.** Frontmatter `name: pair`; `description`: the learner writes the code while Claude asks reasoning questions, reviews each piece and challenges weak choices; triggers: "let me write it", "guide me", "pair with me", "don't give me the code". Body: role; Python lookup snippet (as `practice`); the loop of the spec in this order: (1) goal and success criterion, one question; (2) ask the learner for the next step and why, one question at a time (give two example question shapes: "what happens if the token is expired here?", "what happens with two concurrent requests?"); (3) review each piece they write, classify as bug / risk / optional improvement / style with where and why; challenge discussable choices with an alternative and a trade-off and ask them to defend theirs; (4) help ladder, smallest first: guiding question, hint, minimal example, partial solution, full solution; remember the strongest help; (5) at each milestone the learner summarizes what they did and why in two lines. Rules: never write into the learner's files unless asked (then the session is `full_solution`); never decide the architecture for them; run tests when the environment allows and report what actually ran; never commit; answer in the user's language. Ending: summary of unaided vs supported work, main gaps, offer `/learning-ledger:log-session` with the values from Global Constraints. Add one line: "Unlike `practice`, which gives a brief and reviews at the end, `pair` accompanies the work step by step."
- [ ] **Step 4: Run** `python3 -m unittest discover -s tests -v`. Expected: all pass.
- [ ] **Step 5: Commit** `git commit -m "feat: pair skill"` (add the two files).

---

### Task 3: Pin the `explain` cap in the ledger

**Files:**
- Modify: `tests/test_ledger.py` (new test class `ExplainSessionCap`)

**Interfaces:**
- Consumes: `payload(...)`, `rec(topics, p)` and `topic(...)` helpers already in `tests/test_ledger.py`.

- [ ] **Step 1: Write `ExplainSessionCap.test_explain_session_cannot_exceed_with_support`:** a topic at level `fragile`; payload with `support="full_solution"`, `evidence="observed_answers"`, `outcome="autonomous"`; assert the report's `after["level"] == "with_support"`, `capped` is true, and one reason mentions `full_solution`. Second test `test_explain_without_teach_back_is_self_assessed`: `evidence="self_assessed"` with outcome above the stored level keeps the stored level.
- [ ] **Step 2: Run** `python3 -m unittest tests.test_ledger.ExplainSessionCap -v`. Expected: PASS immediately (the rule exists). If it fails, the spec assumption is wrong: stop and report; do not change `ledger.py`.
- [ ] **Step 3: Commit** `git commit -am "test: pin that an explain session caps at with_support"`.

---

### Task 4: Spring Security topic pack

**Files:**
- Create: `plugins/learning-ledger/examples/spring-security-topics.json`
- Modify: `tests/test_ledger.py` (new class `TopicPacks`)

**Interfaces:**
- Produces: pack `spring-security-topics.json`, format `{"topics":[{"id","name","area"}]}`, area `"security"`.

- [ ] **Step 1: Write `TopicPacks` tests:** `test_every_pack_is_valid` iterates all `examples/*-topics.json`: ids match `^[a-z0-9]+(-[a-z0-9]+)*$`, are unique inside the pack and across all packs, names non-empty. `test_security_pack_size` asserts 10 to 12 topics and that every id starts with `sec-`. `test_import_twice_is_idempotent_with_java_spring`: using the CLI helper of the existing flow class, import `java-spring-topics.json` then `spring-security-topics.json`, then import the security pack again and assert `added == []`.
- [ ] **Step 2: Run** `python3 -m unittest tests.test_ledger.TopicPacks -v`. Expected: FAIL (file missing).
- [ ] **Step 3: Create the pack** with exactly these ten topics (area `security`): `sec-jwt-validation-filter` (JWT validation in a filter), `sec-refresh-token-rotation` (Refresh token rotation and reuse detection), `sec-refresh-race-conditions` (Atomic refresh and race conditions), `sec-token-revocation-logout` (Logout and token revocation), `sec-password-encoding` (Password encoding and upgrades), `sec-method-security` (Method security and where to enforce it), `sec-csrf-cors-sessions` (CSRF, CORS and session policy), `sec-rate-limiting` (Rate limiting and login throttling), `sec-secrets-config` (Secrets and configuration), `sec-mass-assignment` (DTOs and mass assignment).
- [ ] **Step 4: Run** the full suite `python3 -m unittest discover -s tests -v`. Expected: pass.
- [ ] **Step 5: Commit** `git add -A tests plugins && git commit -m "feat: spring security topic pack"`.

---

### Task 5: Wire the new skills into the existing ones

**Files:**
- Modify: `plugins/learning-ledger/skills/study-today/SKILL.md`, `skills/practice/SKILL.md`, `skills/log-session/SKILL.md`
- Modify: `tests/test_skills.py`

- [ ] **Step 1: Add `test_existing_skills_point_to_new_ones`:** `study-today` contains `/learning-ledger:explain` and `/learning-ledger:pair`; `practice` contains `/learning-ledger:pair`; `log-session` contains `explain` and `pair` and `full_solution`; `study-today` also lists `spring-security` among the packs offered.
- [ ] **Step 2: Run** the test. Expected: FAIL.
- [ ] **Step 3: Edit** `study-today`: in step 4 add "`/learning-ledger:explain` to understand code that already exists, `/learning-ledger:pair` to build with guidance"; add `spring-security` to the pack list. `practice`: one line after the intro pointing to `pair`. `log-session`: two bullets under Rules: how `explain` sessions are recorded (support `full_solution`, evidence `observed_answers`, only after a teach-back) and how `pair` sessions are recorded (type `exercise`, evidence per what Claude saw, support = strongest help).
- [ ] **Step 4: Run** the full suite. Expected: pass.
- [ ] **Step 5: Commit** `git commit -am "feat: skills point to explain and pair"`.

---

### Task 6: 1.0.0 release material

**Files:**
- Modify: `plugins/learning-ledger/.claude-plugin/plugin.json` (`"version": "1.0.0"`, description mentions guided learning)
- Modify: `CHANGELOG.md`, `README.md`, `plugins/learning-ledger/README.md`, `CONTRIBUTING.md`, `.claude-plugin/marketplace.json` (description only)
- Modify: `tests/test_skills.py`

- [ ] **Step 1: Add `test_release_metadata_consistent`:** `plugin.json` version is `1.0.0`; the first `## ` heading in `CHANGELOG.md` is `## 1.0.0`; the two README files are byte-identical; the README skills table contains `explain` and `pair`; README says `78 topics` (68 plus 10).
- [ ] **Step 2: Run.** Expected: FAIL.
- [ ] **Step 3: Update files.** README: skills table gets `explain` and `pair` rows; a short section "Three ways to learn" (quiz/practice test you; `explain` helps you understand code that exists; `pair` guides you while you write) with one example prompt each; pack list gets Spring Security; topic count 78; a "Stability" line: from 1.0 the file formats of the ledger and the `ledger.py` JSON output follow semantic versioning. CHANGELOG `## 1.0.0`: explain, pair, Spring Security pack, structure tests, stable formats. CONTRIBUTING: mention structure tests. Copy README into the plugin folder.
- [ ] **Step 4: Run** full suite, then `python3 -m unittest discover -s tests` once more. If `claude` CLI is available run `claude plugin validate .`; otherwise say it was not run.
- [ ] **Step 5: Commit** `git commit -am "release: learning-ledger 1.0.0"`, then `git push -u origin ccr-8058e74e-hy0f34`.

---

## Self-review

- **Spec coverage:** `explain` (Task 1), `pair` (Task 2), ledger registration without script change (Task 3), skill edits (Task 5), security pack (Task 4), 1.0.0 docs and stable formats (Task 6), structure tests (Tasks 1, 2, 5, 6). Conventions (user language, no secrets, no commits) are asserted in Tasks 1 and 2.
- **Type consistency:** only `read_skill` and the existing ledger helpers cross tasks.
- **Proportion:** skill text is described by required content, not written out; the implementer writes the prose.
