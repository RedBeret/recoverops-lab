from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from collections.abc import Callable

from recoverops import __version__
from recoverops.config import ProjectPaths
from recoverops.runner import compose_base, compose_command, run


def _check(label: str, command: list[str]) -> bool:
    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    state = "ok" if result.returncode == 0 else "fail"
    print(f"{state} {label}")
    return result.returncode == 0


def command_doctor(_: argparse.Namespace) -> int:
    paths = ProjectPaths.discover()
    checks: list[bool] = []
    for command in ("python3", "docker", "git"):
        found = shutil.which(command) is not None
        print(f"{'ok' if found else 'fail'} command {command}")
        checks.append(found)
    checks.append(_check("docker daemon", ["docker", "info"]))
    try:
        compose = compose_command()
    except RuntimeError:
        print("fail docker compose")
        checks.append(False)
    else:
        print(f"ok docker compose ({' '.join(compose)})")
        checks.append(True)
        checks.append(
            _check(
                "compose configuration",
                [*compose_base(paths.root), "config", "--quiet"],
            )
        )
    for label, path in (
        ("environment file", paths.root / ".env"),
        ("restic password", paths.secrets / "restic-password"),
        ("compose file", paths.root / "compose.yml"),
    ):
        present = path.is_file()
        print(f"{'ok' if present else 'fail'} {label}")
        checks.append(present)
    return 0 if all(checks) else 1


def command_up(_: argparse.Namespace) -> int:
    paths = ProjectPaths.discover()
    paths.ensure_generated_directories()
    run([*compose_base(paths.root), "up", "-d", "--build"], cwd=paths.root)
    return 0


def command_status(_: argparse.Namespace) -> int:
    paths = ProjectPaths.discover()
    return run([*compose_base(paths.root), "ps"], cwd=paths.root, check=False).returncode


def command_down(_: argparse.Namespace) -> int:
    paths = ProjectPaths.discover()
    return run(
        [*compose_base(paths.root), "down", "--remove-orphans"],
        cwd=paths.root,
        check=False,
    ).returncode


def command_test(_: argparse.Namespace) -> int:
    paths = ProjectPaths.discover()
    commands = [
        [str(paths.root / ".venv/bin/python"), "-m", "pytest", "-q"],
        [str(paths.root / ".venv/bin/ruff"), "check", "src", "app", "tests"],
        ["bash", "-n", "scripts/bootstrap.sh", "scripts/lab.sh"],
        [*compose_base(paths.root), "config", "--quiet"],
    ]
    for command in commands:
        result = run(command, cwd=paths.root, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recoverctl",
        description="Operate the RecoverOps disaster-recovery rehearsal lab.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    handlers: dict[str, tuple[str, Callable[[argparse.Namespace], int]]] = {
        "doctor": ("Check local prerequisites and generated configuration.", command_doctor),
        "up": ("Build and start the lab services.", command_up),
        "status": ("Show lab service status.", command_status),
        "down": ("Stop and remove lab containers while preserving volumes.", command_down),
        "test": ("Run the local validation suite.", command_test),
    }
    for name, (help_text, handler) in handlers.items():
        command_parser = subparsers.add_parser(name, help=help_text)
        command_parser.set_defaults(handler=handler)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
