#!/usr/bin/env python3

import os
import subprocess
import time
import sys
import argparse

# ANSI color codes
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

# Configuration
HISTORY_PATH = os.path.expanduser("~/.brew_migrator_history")
APPLICATIONS_FOLDER = "/Applications"
PAGE_SIZE = 5

TITLE_ART = """
╔═════════════════════════════════╗
║     HOMEBREW APP MIGRATOR v0.1  ║
╚═════════════════════════════════╝
"""


def load_migration_history():
    """Load migration history from file with status tracking."""
    history = {}
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.count(":") >= 2:
                        app, status, detail = line.split(":", 2)
                        history[app] = (status.strip(), detail.strip())
        except Exception as e:
            retro_print(f"Error loading history: {e}", RED)
    return history


def save_migration_history(history):
    """Save entire history dictionary to file"""
    try:
        with open(HISTORY_PATH, "w") as f:
            for app, (status, detail) in history.items():
                f.write(f"{app}:{status}:{detail}\n")
    except Exception as e:
        retro_print(f"Error saving history: {e}", RED)


def type_text(text, delay=0.03):
    """Simulate typewriter effect for retro feel."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def retro_input(prompt):
    """Display a retro-style prompt for user input."""
    type_text(prompt, delay=0.02)
    return input(CYAN + "> " + RESET).strip().upper()


def retro_print(text, color=RESET, newline=True):
    """Print text with retro styling."""
    print(f"{color}{text}{RESET}", end="\n" if newline else "")


def find_matches(app_name, search_type):
    """Find matches for a given app name using Homebrew."""
    try:
        cmd = (
            ["brew", "search", "--cask", app_name]
            if search_type == "cask"
            else ["brew", "search", app_name]
        )
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


def install_homebrew_package(package_name, is_cask, app_name, history):
    """Install a Homebrew package with conflict resolution."""
    cmd = (
        ["brew", "install", "--cask", package_name, "--force"]
        if is_cask
        else ["brew", "install", package_name, "--overwrite"]
    )

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,  # Raise exception on non-zero exit code
        )
        history[app_name] = ("migrated", package_name)
        return True

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8").strip()
        retro_print("\nINSTALLATION FAILED", RED)
        if error_message:
            retro_print(f"REASON: {error_message}", RED)
        history[app_name] = ("failed", error_message)
        return False

    except Exception as e:
        error_message = str(e)
        retro_print(f"\nUNEXPECTED ERROR: {error_message}", RED)
        history[app_name] = ("failed", error_message)
        return False


def display_paginated_matches(matches, start_idx, total):
    """Display matches in paginated format."""
    end_idx = start_idx + PAGE_SIZE
    current_matches = matches[start_idx:end_idx]

    retro_print(f"MATCHES {start_idx + 1}-{min(end_idx, total)} of {total}:", GREEN)
    for i, match in enumerate(current_matches, 1):
        retro_print(f"  [{start_idx + i}] {match}")

    options = []
    if start_idx > 0:
        options.append(("[P] PREVIOUS PAGE", YELLOW))
    if end_idx < total:
        options.append(("[N] NEXT PAGE", YELLOW))
    options.append(("[S] SKIP", YELLOW))
    options.append(("[Q] QUIT", RED))

    retro_print("  " + "  ".join([f"{color}{text}{RESET}" for text, color in options]))


def process_app(app_name, history):
    """Process a single application with paginated matches and conflict resolution."""
    retro_print(f"\n{'=' * 50}", YELLOW)
    type_text(f"SCANNING: {app_name}")

    cask_matches = find_matches(app_name, "cask")
    if not cask_matches:
        retro_print(f"NO MATCHES FOUND FOR {app_name}. SKIPPING...", YELLOW)
        history[app_name] = ("skipped", "no_cask_found")
        return

    total_matches = len(cask_matches)
    start_idx = 0

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(CYAN + TITLE_ART + RESET)
        retro_print(f"Processing: {app_name}", CYAN)
        display_paginated_matches(cask_matches, start_idx, total_matches)

        choice = retro_input("\nSELECT OPTION:")

        if choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < total_matches:
                selected_cask = cask_matches[choice_idx]

                if is_already_installed(selected_cask, True):
                    retro_print(f"ALREADY INSTALLED: {selected_cask}", GREEN)
                    history[app_name] = ("migrated", selected_cask)
                    return

                type_text(f"ATTEMPTING TO INSTALL: {selected_cask}")
                if install_homebrew_package(selected_cask, True, app_name, history):
                    retro_print("INSTALLATION SUCCESSFUL", GREEN)
                    history[app_name] = ("migrated", selected_cask)
                    return
                return None
        elif choice == "N" and (start_idx + PAGE_SIZE) < total_matches:
            start_idx += PAGE_SIZE
        elif choice == "P" and start_idx > 0:
            start_idx -= PAGE_SIZE
        elif choice == "S":
            retro_print("SKIPPED", YELLOW)
            history[app_name] = ("skipped", "user_skipped")
            return
        elif choice == "Q":
            retro_print("QUITTING...", RED)
            sys.exit(0)
        else:
            retro_print("INVALID CHOICE. PLEASE TRY AGAIN.", RED)


def main():
    """Main function to execute the script with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Migrate applications in /Applications to Homebrew Casks."
    )
    parser.add_argument(
        "--list-apps",
        action="store_true",
        help="List all applications found in /Applications.",
    )
    parser.add_argument(
        "--app", type=str, help="Process a specific application by name."
    )
    parser.add_argument(
        "--reset-history", action="store_true", help="Clear the migration history file."
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run in batch mode, automatically install top match.",
    )
    parser.add_argument(
        "--retry-skipped",
        action="store_true",
        help="Retry apps previously skipped due to no cask found.",
    )
    args = parser.parse_args()

    print(CYAN + TITLE_ART + RESET)
    type_text("INITIALIZING HOMEBREW APP MIGRATOR...\n")

    if args.reset_history:
        try:
            os.remove(HISTORY_PATH)
            retro_print(f"Migration history file '{HISTORY_PATH}' cleared.", GREEN)
            return
        except Exception as e:
            retro_print(f"Error clearing history: {e}", RED)
            return

    if subprocess.run(["brew", "--version"], capture_output=True).returncode != 0:
        retro_print("ERROR: HOMEBREW NOT FOUND. ABORT MISSION.", RED)
        return

    # Load history once and maintain in memory
    migration_history = load_migration_history()
    type_text(f"Loaded migration history with {len(migration_history)} entries\n")

    # Get all applications
    app_names = sorted(
        [
            os.path.splitext(app)[0]
            for app in os.listdir(APPLICATIONS_FOLDER)
            if app.endswith(".app")
        ]
    )

    if args.list_apps:
        retro_print("Applications found in /Applications:", CYAN)
        for app in app_names:
            retro_print(f"  - {app}")
        return

    # Determine apps to process
    apps_to_process = []
    initial_state = migration_history.copy()

    for app_name in app_names:
        # Handle specific app flag
        if args.app and app_name != args.app:
            continue

        # Check history status
        if app_name in migration_history:
            status, _ = migration_history[app_name]

            # Skip migrated unless retrying
            if status == "migrated" and not args.retry_skipped:
                continue

            # Handle skipped apps
            if status == "skipped" and not args.retry_skipped:
                continue

        apps_to_process.append(app_name)

    # Process applications
    for app_name in apps_to_process:
        process_app(app_name, migration_history)

    # Save updated history
    save_migration_history(migration_history)

    # Generate report
    retro_print("\n" + "=" * 50, YELLOW)
    type_text("MIGRATION COMPLETE. GENERATING REPORT...")

    # Calculate changes from initial state
    newly_migrated = []
    failed = []
    skipped = []

    for app, (status, detail) in migration_history.items():
        initial_status = initial_state.get(app, ("", ""))[0]

        if status == "migrated" and initial_status != "migrated":
            newly_migrated.append(f"{app} -> {detail}")
        elif status == "failed":
            failed.append(f"{app}: {detail}")
        elif status == "skipped" and initial_status != "skipped":
            skipped.append(f"{app}: {detail}")

    # Show report
    retro_print("\nNEWLY MIGRATED APPLICATIONS:", GREEN)
    for entry in newly_migrated:
        retro_print(f"  - {entry}")

    if failed:
        retro_print("\nFAILED APPLICATIONS:", RED)
        for entry in failed:
            retro_print(f"  - {entry}")

    if skipped:
        retro_print("\nSKIPPED APPLICATIONS:", YELLOW)
        for entry in skipped:
            retro_print(f"  - {entry}")

    retro_print("\nOperation complete. History file updated.", CYAN)


if __name__ == "__main__":
    main()
