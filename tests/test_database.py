import subprocess

from recoverops import database


def completed(stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")


def test_missing_database_is_created(monkeypatch) -> None:
    monkeypatch.setattr(database, "assert_container_scope", lambda *_: None)
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        return completed("")

    monkeypatch.setattr(database.subprocess, "run", fake_run)

    result = database.ensure_recoverops_database("recoverops-primary-db", "primary-db")

    assert result["created"] is True
    assert any("createdb" in command for command in calls)


def test_existing_database_is_not_created_again(monkeypatch) -> None:
    monkeypatch.setattr(database, "assert_container_scope", lambda *_: None)
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        return completed("1\n")

    monkeypatch.setattr(database.subprocess, "run", fake_run)

    result = database.ensure_recoverops_database("recoverops-primary-db", "primary-db")

    assert result["created"] is False
    assert not any("createdb" in command for command in calls)
