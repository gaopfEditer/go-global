from __future__ import annotations


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


_load_dotenv()

import argparse  # noqa: E402
from pathlib import Path  # noqa: E402

from job_radar.config import DEFAULT_DB_PATH, DEFAULT_INTERVAL_MINUTES, DEFAULT_SUMMARY_DIR  # noqa: E402
from job_radar.runner import run_loop, run_once  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal freelance job radar")
    sub = parser.add_subparsers(dest="command", required=True)

    once = sub.add_parser("once", help="Fetch once and exit")
    once.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    once.add_argument("--summary-dir", type=Path, default=DEFAULT_SUMMARY_DIR)

    loop = sub.add_parser("loop", help="Fetch every N minutes until stopped")
    loop.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    loop.add_argument("--summary-dir", type=Path, default=DEFAULT_SUMMARY_DIR)
    loop.add_argument(
        "--interval-minutes",
        type=int,
        default=DEFAULT_INTERVAL_MINUTES,
        help="Fetch interval (default: 30)",
    )

    args = parser.parse_args()
    if args.command == "once":
        raise SystemExit(run_once(db_path=args.db, summary_dir=args.summary_dir))
    if args.command == "loop":
        run_loop(
            db_path=args.db,
            summary_dir=args.summary_dir,
            interval_minutes=args.interval_minutes,
        )


if __name__ == "__main__":
    main()
