import pytest

from recoverops.cli import build_parser


def test_parser_requires_a_command() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit) as error:
        parser.parse_args([])

    assert error.value.code == 2


def test_parser_accepts_foundation_commands() -> None:
    parser = build_parser()

    for command in (
        "doctor",
        "up",
        "status",
        "down",
        "seed",
        "backup",
        "restore",
        "verify",
        "report",
        "test",
    ):
        assert parser.parse_args([command]).command == command


def test_disaster_requires_explicit_apply(capsys) -> None:
    from recoverops.cli import main

    assert main(["disaster"]) == 2
    assert "without --apply" in capsys.readouterr().err


def test_rehearsal_requires_explicit_apply(capsys) -> None:
    from recoverops.cli import main

    assert main(["rehearse"]) == 2
    assert "without --apply" in capsys.readouterr().err
