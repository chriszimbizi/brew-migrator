import json

from brew_migrator.core.history import HistoryManager


def test_dry_run_history_is_not_saved(tmp_path):
    path = tmp_path / "history"
    history = HistoryManager(str(path), persist=False)
    history.update("Zoom", "migrated (dry-run)", "zoom")

    assert not path.exists()
    assert history.get("Zoom")["status"] == "migrated (dry-run)"


def test_legacy_dry_run_entries_do_not_lock(tmp_path):
    path = tmp_path / "history"
    path.write_text(json.dumps({
        "Zoom": {"status": "migrated (dry-run)", "detail": "zoom"},
        "Slack": {"status": "migrated", "detail": "slack"},
    }))
    history = HistoryManager(str(path))

    assert not history.is_migrated("Zoom")
    assert history.is_migrated("Slack")
    assert history.get_installed() == ["Slack"]
