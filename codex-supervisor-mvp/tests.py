from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from supervisor import Policy


ROOT = Path(__file__).resolve().parent
DEFAULT_POLICY = ROOT / "scripts" / "default-policy.json"


class PolicyTests(unittest.TestCase):
    def test_policy_matches_regex(self) -> None:
        policy = Policy.load(DEFAULT_POLICY)
        rule = policy.match("是否要執行測試？")
        self.assertIsNotNone(rule)
        self.assertEqual(rule.name, "allow_repo_tests")

    def test_policy_supports_reply_file(self) -> None:
        repo_policy = Policy.load(
            Path(r"C:\.codex_code_project\repos\jacks_happy_bots\.codex-supervisor\policy.json")
        )
        rule = repo_policy.match("我需要先問使用者")
        self.assertIsNotNone(rule)
        assert rule is not None
        self.assertIn("先反思", rule.reply)
        self.assertIn("更優方案", rule.reply)


class SupervisorFlowTests(unittest.TestCase):
    def test_supervisor_replies_to_fake_agent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            command = [
                sys.executable,
                str(ROOT / "supervisor.py"),
                "--policy",
                str(DEFAULT_POLICY),
                "--state-dir",
                str(state_dir),
                "--no-echo",
                "--",
                sys.executable,
                str(ROOT / "scripts" / "fake_agent.py"),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, msg=result.stderr)

            audit_lines = (state_dir / "audit.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertGreaterEqual(len(audit_lines), 2)
            first = json.loads(audit_lines[0])
            self.assertEqual(first["event"], "auto_reply")
            self.assertEqual(first["rule"], "allow_repo_tests")

            session_log = (state_dir / "session.log").read_text(encoding="utf-8")
            self.assertIn("收到回覆", session_log)


if __name__ == "__main__":
    unittest.main()
