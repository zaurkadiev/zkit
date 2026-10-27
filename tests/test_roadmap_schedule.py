"""Run check_roadmap.py's scheduler on a tiny roadmap: parallel workers, external waits, gate barriers."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "skills" / "roadmap" / "scripts" / "check_roadmap.py"
ROADMAP = """# Roadmap
> 2 PH · 1 G · 3 TK · 1 EP

| Scenario | Hours per week | Deadline (weeks) | Workers |
|---|---|---|---|
| best | 10 | | {w} |
| expected | 10 | | {w} |
| worst | 10 | | {w} |

| ID | Phase | Goal |
|---|---|---|
| PH-0 | Prove | spikes |
| PH-1 | Build | slice |

| ID | Gate | Phase | Criteria | If fail |
|---|---|---|---|---|
| G-0 | Go | PH-0 | measured | stop |

| ID | Task | Epic | Phase | Best | Expected | Worst | Depends | Wait (weeks) | Source | Acceptance |
|---|---|---|---|---|---|---|---|---|---|---|
| TK-1 | Spike A | EP-1 | PH-0 | 10 | 10 | 10 | — | 0 | spike | done |
| TK-2 | Spike B | EP-1 | PH-0 | 10 | 10 | 10 | — | {wait} | spike | done |
| TK-3 | Build | EP-1 | PH-1 | 10 | 10 | 10 | — | 0 | FR-1 | done |

| ID | Epic | Phase | Best | Expected | Worst |
|---|---|---|---|---|---|
| EP-1 | All | PH-0 | 0 | 0 | 0 |

<!-- schedule:begin -->
<!-- schedule:end -->
"""


def weeks(workers, wait=0, depends=False):
    text = ROADMAP.format(w=workers, wait=wait)
    if depends: text = text.replace("| TK-2 | Spike B | EP-1 | PH-0 | 10 | 10 | 10 | — |", "| TK-2 | Spike B | EP-1 | PH-0 | 10 | 10 | 10 | TK-1 |")
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "roadmap.md").write_text(text, encoding="utf-8")
        out = subprocess.run([sys.executable, str(CHECK), d, "--update"], capture_output=True, text=True).stdout
        block = (Path(d) / "roadmap.md").read_text(encoding="utf-8")
    return float(re.search(r"weeks [\d.]+ / ([\d.]+)", out).group(1)), block


class ScheduleTest(unittest.TestCase):
    def test_one_worker_runs_in_sequence(self):
        self.assertEqual(weeks(1)[0], 3.0)

    def test_two_workers_run_independent_tasks_in_parallel(self):
        total, block = weeks(2)
        self.assertEqual(total, 2.0)   # TK-1 and TK-2 together, TK-3 after the gate
        self.assertIn("- Worker 2:", block)

    def test_gate_holds_back_the_next_phase(self):
        self.assertEqual(weeks(3)[0], 2.0)   # a third worker cannot start TK-3 before G-0 closes PH-0

    def test_dependency_serialises(self):
        self.assertEqual(weeks(2, depends=True)[0], 3.0)

    def test_external_wait_delays_the_dependent_task(self):
        self.assertEqual(weeks(1, wait=1, depends=True)[0], 3.0 + 1.0)   # TK-2 waits 1 week after TK-1; the gate keeps TK-3 from filling it

    def test_old_format_block_is_a_warning(self):
        text = ROADMAP.format(w=1, wait=0).replace("<!-- schedule:begin -->", "<!-- schedule:begin -->\n**Schedule** (one developer; weeks from the start)")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "roadmap.md").write_text(text, encoding="utf-8")
            out = subprocess.run([sys.executable, str(CHECK), d], capture_output=True, text=True).stdout
        self.assertIn("format before parallel workers", out)
        self.assertNotIn("schedule block is stale", out)


if __name__ == "__main__":
    unittest.main()
