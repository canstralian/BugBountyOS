"""Command-line entry points for BugBountyOS."""
from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bbos",
        description="BugBountyOS workspace CLI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("tui", help="Launch the read-only workspace dashboard.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "tui":
        return tui_main()
    return 2


def tui_main(argv: list[str] | None = None) -> int:
    try:
        from bbos.tui.app import WorkspaceApp
    except ModuleNotFoundError as exc:
        sys.stderr.write(
            f"bbos: TUI requires the 'textual' package ({exc.name}). "
            "Install with: pip install 'bbos[tui]'  or  pip install textual\n"
        )
        return 1
    WorkspaceApp().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
