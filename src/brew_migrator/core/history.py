import os
import json
import shutil
from datetime import datetime
from ..ui.console import retro_print, RED


HISTORY_PATH = os.path.expanduser("~/.brew_migrator_history")


class HistoryManager:
    def __init__(self, filepath=HISTORY_PATH):
        self.filepath = filepath
        self.history = self._load()

    def _load(self):
        """Load history safely from JSON."""
        if not os.path.exists(self.filepath):
            return {}

        try:
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            retro_print(f"WARNING: History file issue: {e}. Starting fresh.", RED)
            return {}

    def get(self, app_name):
        """Get the status of an app."""
        return self.history.get(app_name, {})

    def update(self, app_name, status, detail):
        """Update an app's status and save immediately."""
        self.history[app_name] = {
            "status": status,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        }
        self._save()

    def _save(self):
        """Atomic save: write to temp file, then rename."""
        temp_path = self.filepath + ".tmp"
        try:
            with open(temp_path, "w") as f:
                json.dump(self.history, f, indent=2)
            shutil.move(temp_path, self.filepath)
        except Exception as e:
            retro_print(f"FAILED TO SAVE HISTORY: {e}", RED)

    def clear(self):
        """Clear the migration history file."""
        self.history = {}
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
            return True
        return False

    def get_summary(self, initial_state_history=None):
        """Return counts for the final report."""
        newly_migrated = []
        failed = []
        skipped = []

        for app, data in self.history.items():
            status = data.get("status", "")
            detail = data.get("detail", "")

            # Check if it was newly migrated in this session
            is_new = True
            if initial_state_history and app in initial_state_history:
                initial_status = initial_state_history[app].get("status", "")
                if status == initial_status:
                    is_new = False

            if status.startswith("migrated") and is_new:
                newly_migrated.append(f"{app} -> {detail}")
            elif status == "failed":
                failed.append(f"{app}: {detail}")
            elif status == "skipped" and is_new:
                skipped.append(f"{app}: {detail}")

        return newly_migrated, failed, skipped

    def copy_history(self):
        """Return a deep copy of the current history dictionary."""
        return json.loads(json.dumps(self.history))
