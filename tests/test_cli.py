import pytest

from recoverops.cli import build_parser


def test_parser_requires_a_command() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit) as error:
        parser.parse_args([])

    assert error.value.code == 2


def test_parser_accepts_foundation_commands() -> None:
    parser = build_parser()

    for command in ("doctor", "up", "status", "down", "seed", "backup", "test"):
        assert parser.parse_args([command]).command == command
