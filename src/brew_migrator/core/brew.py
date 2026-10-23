import os
import json
import subprocess
from ..ui.console import retro_print, RED, ProgressBar


def parse_installed_cask_apps(casks):
    """Map .app names (without extension) to cask tokens from `brew info --json=v2` cask entries."""
    apps = {}
    for cask in casks:
        token = cask.get("token")
        for artifact in cask.get("artifacts", []):
            if not isinstance(artifact, dict) or "app" not in artifact:
                continue
            for entry in artifact["app"]:
                # Entries are either "Foo.app" or {"target": "Bar.app"} for renamed installs
                name = entry.get("target") if isinstance(entry, dict) else entry
                if isinstance(name, str) and name.endswith(".app"):
                    apps[os.path.splitext(os.path.basename(name))[0]] = token
    return apps


def get_installed_cask_apps():
    """Return {app_name: cask_token} for every app installed via a Homebrew cask."""
    try:
        result = subprocess.run(
            ["brew", "info", "--cask", "--json=v2", "--installed"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return parse_installed_cask_apps(json.loads(result.stdout).get("casks", []))
    except (OSError, subprocess.CalledProcessError, ValueError) as e:
        retro_print(f"WARNING: Could not read installed casks: {e}", RED)
        return {}


def find_matches(app_name, search_type):
    """Find matches for a given app name using Homebrew."""
    try:
        cmd = (
            ["brew", "search", "--cask", app_name]
            if search_type == "cask"
            else ["brew", "search", app_name]
        )
        with ProgressBar():
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return [
            match.strip()
            for match in result.stdout.decode("utf-8").strip().split("\n")
            if match.strip()
        ]
    except Exception as e:
        retro_print(f"ERROR: {str(e)}", RED)
        return []


def is_already_installed(package_name, is_cask):
    """Check if a package is already installed."""
    try:
        cmd = [
            "brew",
            "list",
            "--cask" if is_cask else "--formula",
            package_name,
        ]
        return (
            subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ).returncode
            == 0
        )
    except:
        return False


def install_homebrew_package(package_name, is_cask, app_name, history_manager, dry_run=False):
    """Install a Homebrew package with conflict resolution."""
    cmd = (
        ["brew", "install", "--cask", package_name, "--force"]
        if is_cask
        else ["brew", "install", package_name, "--overwrite"]
    )

    if dry_run:
        from ..ui.console import YELLOW, RESET
        retro_print(f"DRY RUN: Would run >> {' '.join(cmd)}", YELLOW)
        history_manager.update(app_name, "migrated (dry-run)", package_name)
        return True

    try:
        with ProgressBar(f"INSTALLING {package_name}"):
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        history_manager.update(app_name, "migrated", package_name)
        return True

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8").strip()
        history_manager.update(app_name, "failed", error_message)
        return False

    except Exception as e:
        error_message = str(e)
        history_manager.update(app_name, "failed", error_message)
        return False


def check_brew_installed():
    """Verify if Homebrew is installed."""
    try:
        return subprocess.run(["brew", "--version"], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False
