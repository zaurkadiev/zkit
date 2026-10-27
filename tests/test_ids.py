"""Run link_docs.py's id verification against a tiny project."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LINK = ROOT / "skills" / "requirements" / "scripts" / "link_docs.py"
REQUIREMENTS = """# Requirements
- **P-1.** Ten interviews. Criterion: three name the pain.

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | Read knowledge | Must |

## 10. Conflicts
1. **Q-1.** Cheap vs. verified.
"""
ARCHITECTURE = """# Architecture
| ID | Responsibility | Serves |
|---|---|---|
| B-1 | Read knowledge | FR-1, Q-1 |
"""


def run(files):
    with tempfile.TemporaryDirectory() as d:
        for name, text in files.items():
            (Path(d) / name).write_text(text, encoding="utf-8")
        return subprocess.run([sys.executable, str(LINK), d], capture_output=True, text=True)


class IdsTest(unittest.TestCase):
    def test_consistent_project_passes(self):
        r = run({"requirements.md": REQUIREMENTS, "architecture.md": ARCHITECTURE})
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_dangling_id_fails(self):
        r = run({"requirements.md": REQUIREMENTS, "architecture.md": ARCHITECTURE.replace("FR-1,", "FR-9,")})
        self.assertEqual(r.returncode, 1)
        self.assertIn("FR-9 (functional requirement) is cited in architecture.md but not defined in requirements.md", r.stdout)

    def test_local_label_fails(self):
        r = run({"requirements.md": REQUIREMENTS, "contracts.md": "# Contracts\n- **F-1.** A finding.\n"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("list label F-1 is not an id of the registry", r.stdout)

    def test_unplanned_precondition_warns(self):
        r = run({"requirements.md": REQUIREMENTS, "roadmap.md": "# Roadmap\n| TK-1 | Build | FR-1 |\n"})
        self.assertIn("WARN precondition P-1 is planned by no task", r.stdout)


if __name__ == "__main__":
    unittest.main()
