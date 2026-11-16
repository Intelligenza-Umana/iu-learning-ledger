import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "plugins" / "learning-ledger" / "skills"


def read_skill(name):
    text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    assert match, f"{name}: missing frontmatter"
    front = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        front[key.strip()] = value.strip()
    return front, match.group(2)


class SkillStructure(unittest.TestCase):
    def test_every_skill_folder_has_matching_frontmatter(self):
        folders = [p for p in SKILLS_DIR.iterdir() if p.is_dir()]
        self.assertTrue(folders)
        for folder in folders:
            front, _ = read_skill(folder.name)
            self.assertEqual(front.get("name"), folder.name)
            self.assertTrue(front.get("description"))
            self.assertLessEqual(len(front["description"]), 1024)

    def test_expected_skill_set(self):
        names = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
        self.assertEqual(
            names,
            {"explain", "log-session", "pair", "practice", "quiz", "study-today", "weekly-report"},
        )

    def test_explain_contract(self):
        _, body = read_skill("explain")
        low = body.lower()
        for needle in ["full_solution", "observed_answers", "teach-back", "git diff", "unverified",
                       "bug", "risk", "how would you tell it", "${claude_plugin_root}",
                       "answer in the user's language", "not a git repository"]:
            self.assertIn(needle, low, needle)

    def test_pair_contract(self):
        _, body = read_skill("pair")
        low = body.lower()
        for needle in ["one question at a time", "exercise", "observed_exercise", "reviewed_code",
                       "full_solution", "guiding question", "defend", "bug", "risk",
                       "${claude_plugin_root}", "answer in the user's language", "never commit"]:
            self.assertIn(needle, low, needle)

    def test_existing_skills_point_to_new_ones(self):
        _, today = read_skill("study-today")
        self.assertIn("/learning-ledger:explain", today)
        self.assertIn("/learning-ledger:pair", today)
        self.assertIn("spring-security", today)
        _, practice = read_skill("practice")
        self.assertIn("/learning-ledger:pair", practice)
        _, log = read_skill("log-session")
        for needle in ["explain", "pair", "full_solution"]:
            self.assertIn(needle, log)

    def test_review_fixes_keep_the_ledger_honest(self):
        _, explain = read_skill("explain")
        _, pair = read_skill("pair")
        _, quiz = read_skill("quiz")
        _, log = read_skill("log-session")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        # 1: no same-day quiz right after an explanation
        self.assertIn("same day", explain.lower())
        self.assertIn("explain", quiz)
        self.assertIn("full_solution", quiz)
        self.assertIn("same day", readme.lower())
        self.assertNotIn("Higher levels need a later unaided quiz or pair session", readme)
        # 2: do not demote a known topic silently
        for body in (explain, log):
            self.assertIn("consolidation progress", body)
            self.assertIn("autonomous", body)
        # 3: probing questions are not support, revealing ones are
        self.assertIn("probing", pair.lower())
        self.assertIn("reveal", pair.lower())
        # 4: one question per message, ask before telling
        self.assertIn("one question per message", pair.lower())
        self.assertIn("ask before you tell", pair.lower())
        # 5: pacing and mandatory teach-back
        self.assertIn("per turn", explain.lower())
        self.assertIn("mandatory", explain.lower())
        # 6: rubric inline, score to log
        self.assertIn("Correctness 12", explain)
        self.assertIn("score_30", explain)


class Release(unittest.TestCase):
    def test_release_metadata_consistent(self):
        import json
        plugin = json.loads((ROOT / "plugins/learning-ledger/.claude-plugin/plugin.json").read_text())
        self.assertEqual(plugin["version"], "1.0.0")
        changelog = (ROOT / "CHANGELOG.md").read_text()
        first = next(l for l in changelog.splitlines() if l.startswith("## "))
        self.assertEqual(first, "## 1.0.0")
        readme = (ROOT / "README.md").read_text()
        self.assertEqual(readme, (ROOT / "plugins/learning-ledger/README.md").read_text())
        self.assertIn("`/learning-ledger:explain`", readme)
        self.assertIn("`/learning-ledger:pair`", readme)
        self.assertIn("78 topics", readme)


if __name__ == "__main__":
    unittest.main()
