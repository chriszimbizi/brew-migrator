import os
import re
import json
import subprocess
from ..ui.console import retro_print, RED, YELLOW, ProgressBar


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


def normalize_app_name(app_name):
    """Turn an app name into its likely cask token, e.g. "Visual Studio Code" -> "visual-studio-code"."""
    token = re.sub(r"\s+", "-", app_name.strip().lower())
    token = re.sub(r"[^a-z0-9\-+.@]", "", token)
    return re.sub(r"-{2,}", "-", token).strip("-")


def _simplify(text):
    """Strip separators so "Visual Studio Code" and "visual-studio-code" compare equal."""
    return re.sub(r"[\s\-_.]", "", text.lower())


def rank_matches(app_name, cask_tokens):
    """Return cask tokens matching app_name, best first: exact token, then prefix, then shortest."""
    query = _simplify(app_name)
    if not query:
        return []
    exact = normalize_app_name(app_name)
    matches = [token for token in cask_tokens if query in _simplify(token)]
    return sorted(
        matches,
        key=lambda token: (token != exact, not _simplify(token).startswith(query), len(token), token),
    )


def exact_match(app_name, matches):
    """Return the match whose token is exactly the normalized app name, or None."""
    exact = normalize_app_name(app_name)
    return exact if exact in matches else None


def list_all_casks():
    """Return every available cask token (one brew call, reused for every app)."""
    try:
        with ProgressBar("LOADING CASK INDEX"):
            result = subprocess.run(
                ["brew", "casks"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )
        return [line.strip() for line in result.stdout.decode("utf-8").splitlines() if line.strip()]
    except (OSError, subprocess.CalledProcessError) as e:
        retro_print(f"WARNING: Could not load cask index: {e}", RED)
        return []


def find_matches(app_name, cask_tokens=None):
    """Find cask matches for an app, using the preloaded index when available."""
    if cask_tokens:
        return rank_matches(app_name, cask_tokens)

    # Fall back to a per-app search when the index couldn't be loaded
    try:
        with ProgressBar():
            result = subprocess.run(
                ["brew", "search", "--cask", app_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        found = [m.strip() for m in result.stdout.decode("utf-8").splitlines() if m.strip()]
        exact = normalize_app_name(app_name)
        return sorted(found, key=lambda token: (token != exact, len(token), token))
    except OSError as e:
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
    except OSError:
        return False


def install_homebrew_package(package_name, is_cask, app_name, history_manager, dry_run=False, appdir=None):
    """Install a Homebrew package with conflict resolution."""
    cmd = (
        ["brew", "install", "--cask", package_name, "--force"]
        if is_cask
        else ["brew", "install", package_name, "--overwrite"]
    )
    # Keep apps from ~/Applications in place instead of duplicating them into /Applications
    if is_cask and appdir:
        cmd.append(f"--appdir={appdir}")

    if dry_run:
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
