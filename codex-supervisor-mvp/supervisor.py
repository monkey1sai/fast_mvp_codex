from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Rule:
    name: str
    pattern: re.Pattern[str]
    reply: str
    once: bool = False


class Policy:
    def __init__(self, rules: list[Rule]) -> None:
        self.rules = rules
        self._used_once: set[str] = set()

    @classmethod
    def load(cls, path: Path | str) -> "Policy":
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        base_dir = path.parent
        rules: list[Rule] = []
        for item in raw["rules"]:
            reply = item.get("reply")
            reply_file = item.get("reply_file")
            if reply and reply_file:
                raise ValueError(f"rule {item['name']} cannot define both reply and reply_file")
            if reply_file:
                reply_path = base_dir / reply_file
                reply = reply_path.read_text(encoding="utf-8")
            if not reply:
                raise ValueError(f"rule {item['name']} must define reply or reply_file")
            rules.append(
                Rule(
                    name=item["name"],
                    pattern=re.compile(item["match"], re.IGNORECASE),
                    reply=reply,
                    once=item.get("once", False),
                )
            )
        return cls(rules)

    def match(self, text: str) -> Rule | None:
        for rule in self.rules:
            if rule.once and rule.name in self._used_once:
                continue
            if rule.pattern.search(text):
                if rule.once:
                    self._used_once.add(rule.name)
                return rule
        return None


class Supervisor:
    def __init__(
        self,
        command: list[str],
        policy: Policy,
        state_dir: Path,
        idle_seconds: float = 1.0,
        echo: bool = True,
    ) -> None:
        self.command = command
        self.policy = policy
        self.state_dir = state_dir
        self.idle_seconds = idle_seconds
        self.echo = echo
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.session_log = self.state_dir / "session.log"
        self.audit_log = self.state_dir / "audit.jsonl"

    def _append_audit(self, payload: dict[str, Any]) -> None:
        line = json.dumps(payload, ensure_ascii=False)
        with self.audit_log.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def _resolve_command(self) -> list[str]:
        if not self.command:
            return self.command
        resolved = list(self.command)
        executable = resolved[0]
        if os.name == "nt" and executable.lower() == "codex":
            resolved_path = shutil.which("codex.cmd") or shutil.which("codex")
            if resolved_path:
                resolved[0] = resolved_path
        return resolved

    def run(self) -> int:
        proc = subprocess.Popen(
            self._resolve_command(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        assert proc.stdout is not None
        assert proc.stdin is not None

        line_queue: queue.Queue[str | None] = queue.Queue()

        def reader() -> None:
            try:
                for line in proc.stdout:
                    line_queue.put(line)
            finally:
                line_queue.put(None)

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()

        with self.session_log.open("a", encoding="utf-8") as session_fh:
            while True:
                try:
                    item = line_queue.get(timeout=self.idle_seconds)
                except queue.Empty:
                    if proc.poll() is not None:
                        break
                    continue

                if item is None:
                    break

                session_fh.write(item)
                session_fh.flush()

                if self.echo:
                    sys.stdout.write(item)
                    sys.stdout.flush()

                rule = self.policy.match(item)
                if not rule:
                    continue

                reply = rule.reply.strip() + "\n"
                proc.stdin.write(reply)
                proc.stdin.flush()
                self._append_audit(
                    {
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "event": "auto_reply",
                        "rule": rule.name,
                        "matched_line": item.rstrip("\n"),
                        "reply": rule.reply,
                    }
                )

        return proc.wait()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor a Codex-like session and auto-reply to allowlisted prompts.")
    parser.add_argument("--policy", required=True, type=Path, help="Path to policy.json")
    parser.add_argument("--state-dir", type=Path, default=Path("state"), help="Directory for logs and audit output")
    parser.add_argument(
        "--idle-seconds",
        type=float,
        default=1.0,
        help="Polling window while waiting for child output",
    )
    parser.add_argument(
        "--no-echo",
        action="store_true",
        help="Do not mirror child output to supervisor stdout",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to execute after --")
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("command is required after --")
    return args


def main() -> int:
    args = parse_args()
    policy = Policy.load(args.policy)
    supervisor = Supervisor(
        command=args.command,
        policy=policy,
        state_dir=args.state_dir,
        idle_seconds=args.idle_seconds,
        echo=not args.no_echo,
    )
    return supervisor.run()


if __name__ == "__main__":
    raise SystemExit(main())
