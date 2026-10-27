"""Run the real checkers against reports and adjacent research artifacts."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = """# Fixture requirements
> **Counts:** 1 FR · 0 NFR · 0 C · Must 0 · Should 1 · Could 0

| ID | Requirement | Priority | Acceptance | Source | Basis |
|---|---|---|---|---|---|
| FR-1 | Read knowledge | Should | Returns a reference | fixture | confirmed |

## Traceability
| Requirement | Source |
|---|---|
| FR-1 | fixture |
"""
ARCHITECTURE = """# Fixture architecture
> **Status:** draft · **Counts:** 1 B · 0 I · 1 S

## Parts
| ID | Responsibility | Serves |
|---|---|---|
| B-1 | Read knowledge | FR-1 |

## Scenarios
| ID | Steps | Outcome |
|---|---|---|
| S-1 | B-1 | Reference returned |

## C4 level 1 context
```mermaid
flowchart LR
  User --> B1
```

## C4 level 2 containers
```mermaid
flowchart LR
  User --> B1
```

## C4 level 3 components
```mermaid
flowchart LR
  B1 --> Reader
```

## Traceability
| Requirement | Parts |
|---|---|
| FR-1 | B-1 |
"""


class ResearchReportTests(unittest.TestCase):
    def project(self, directory, checker, *, cited=False, invalid=False):
        root = Path(directory)
        text = REQUIREMENTS if checker == "requirements" else ARCHITECTURE
        if invalid:
            prefix = "| FR-1 | Read knowledge" if checker == "requirements" else "| B-1 | Read knowledge"
            row = next(line for line in text.splitlines() if line.startswith(prefix))
            text = text.replace(row, row + "\n" + row)
        if cited:
            text += "\nSee [R-1](research/R-1-probe.md).\n"
        (root / (checker + ".md")).write_text(text, encoding="utf-8")
        (root / "research").mkdir()
        return root

    def run_checker(self, checker, project):
        script = ROOT / "skills" / checker / "scripts" / ("check_" + checker + ".py")
        return subprocess.run(
            [sys.executable, "-B", str(script), str(project)],
            capture_output=True, text=True, timeout=10,
        )

    def test_checks_report_beside_artifact_directories_and_auxiliary_files(self):
        # Removing the report filter must reproduce the crash; skipping every
        # entry must lose the observable warning for the real report.
        for checker in ("requirements", "architecture"):
            with self.subTest(checker=checker), tempfile.TemporaryDirectory() as directory:
                project = self.project(directory, checker)
                research = project / "research"
                (research / "R-1-probe").mkdir()
                (research / "R-2-artifacts.md").mkdir()
                (research / "README.md").write_text("Auxiliary documentation", encoding="utf-8")
                (research / "metadata.bin").write_bytes(b"\xff")
                requested_by = "requirements" if checker == "requirements" else "hld"
                (research / "R-1-probe.md").write_text(
                    "# R-1\nRequested by " + requested_by + "\n", encoding="utf-8",
                )
                result = self.run_checker(checker, project)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertIn("was asked by " + checker, result.stdout)

    def test_artifact_directory_cannot_replace_a_cited_report(self):
        # Filtering only inside the reading loop would still let a directory
        # satisfy the earlier existence check for a cited report.
        for checker in ("requirements", "architecture"):
            with self.subTest(checker=checker), tempfile.TemporaryDirectory() as directory:
                project = self.project(directory, checker, cited=True)
                (project / "research/R-1-probe.md").mkdir()
                result = self.run_checker(checker, project)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, "")
                self.assertIn("cites R-1, no such report in research/", result.stdout)

    def test_finds_a_cited_report(self):
        for checker in ("requirements", "architecture"):
            with self.subTest(checker=checker), tempfile.TemporaryDirectory() as directory:
                project = self.project(directory, checker, cited=True)
                (project / "research/R-1-probe.md").write_text("# R-1\nFindings\n", encoding="utf-8")
                result = self.run_checker(checker, project)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stderr, "")

    def test_document_errors_are_still_reported(self):
        for checker in ("requirements", "architecture"):
            with self.subTest(checker=checker), tempfile.TemporaryDirectory() as directory:
                project = self.project(directory, checker, invalid=True)
                (project / "research/R-1-probe").mkdir()
                result = self.run_checker(checker, project)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, "")
                self.assertIn("duplicate", result.stdout)


if __name__ == "__main__":
    unittest.main()
