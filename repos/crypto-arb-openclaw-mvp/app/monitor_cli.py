from __future__ import annotations

import argparse
import os
from pathlib import Path

from app.monitor import watch_monitor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Watch OpenClaw 24h runner logs in real time.")
    parser.add_argument(
        "--telemetry-path",
        default=str(Path("..") / ".." / "log" / "openclaw-runner.jsonl"),
        help="Path to runner JSONL summary log.",
    )
    parser.add_argument(
        "--event-log-path",
        default=str(Path("..") / ".." / "log" / "openclaw-events.jsonl"),
        help="Path to runner event JSONL log.",
    )
    parser.add_argument(
        "--refresh-seconds",
        type=float,
        default=2.0,
        help="Refresh interval for follow mode.",
    )
    parser.add_argument(
        "--recent-events",
        type=int,
        default=12,
        help="How many recent events to display.",
    )
    parser.add_argument(
        "--follow",
        action="store_true",
        help="Continuously watch the logs until interrupted.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="How many refresh iterations to print when not running forever.",
    )
    parser.add_argument(
        "--clear-screen",
        action="store_true",
        help="Clear screen between refreshes in follow mode.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    def clear_screen() -> None:
        os.system("cls" if os.name == "nt" else "clear")

    watch_monitor(
        telemetry_path=args.telemetry_path,
        event_log_path=args.event_log_path,
        refresh_seconds=args.refresh_seconds,
        recent_event_limit=args.recent_events,
        iterations=0 if args.follow and args.iterations <= 0 else max(args.iterations, 1),
        clear_fn=clear_screen if args.clear_screen else None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
