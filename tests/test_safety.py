import pytest

from recoverops.safety import SafetyError, validate_container_scope


def metadata(project: str = "recoverops", service: str = "primary-db") -> dict:
    return {
        "Name": "/recoverops-primary-db",
        "Config": {
            "Labels": {
                "com.docker.compose.project": project,
                "com.docker.compose.service": service,
            }
        },
        "State": {"Running": True},
    }


def test_container_scope_accepts_exact_project_and_service() -> None:
    validate_container_scope(metadata(), "recoverops-primary-db", "primary-db")


def test_container_scope_rejects_other_compose_project() -> None:
    with pytest.raises(SafetyError, match="outside Compose project"):
        validate_container_scope(
            metadata(project="kubedrift"),
            "recoverops-primary-db",
            "primary-db",
        )


def test_container_scope_rejects_other_service() -> None:
    with pytest.raises(SafetyError, match="service mismatch"):
        validate_container_scope(
            metadata(service="recovery-db"), "recoverops-primary-db", "primary-db"
        )
