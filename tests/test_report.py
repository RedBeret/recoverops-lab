from recoverops.report import render_markdown, seconds_between


def test_seconds_between_uses_utc_timestamps() -> None:
    assert seconds_between("2026-07-19T01:00:00Z", "2026-07-19T01:00:04.250000Z") == 4.25


def test_markdown_report_contains_outcome_metrics_and_hashes() -> None:
    fingerprint = {
        "data_sha256": "data-hash",
        "schema_sha256": "schema-hash",
        "row_counts": {"owners": 4, "assets": 6, "maintenance_events": 12},
    }
    report = {
        "outcome": "PASS",
        "generated_at": "2026-07-19T01:00:00Z",
        "metrics": {
            "rto_seconds": 8.5,
            "restore_duration_seconds": 5.0,
            "backup_age_at_recovery_seconds": 10.0,
        },
        "comparisons": {"data_sha256": {"match": True}},
        "services": {"primary_api": 503, "recovery_api": 200},
        "source_fingerprint": fingerprint,
        "recovery_fingerprint": fingerprint,
    }

    markdown = render_markdown(report)

    assert "**Outcome:** PASS" in markdown
    assert "RTO" in markdown
    assert "data-hash" in markdown
