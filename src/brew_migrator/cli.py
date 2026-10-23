import os
import sys
import time
import argparse
from .ui.console import (
    TITLE_ART, type_text, retro_input, retro_print, clear_screen,
    press_enter_to_continue, display_paginated_matches,
    display_retro_list, GREEN, CYAN, YELLOW, RED, RESET, PAGE_SIZE
)
from .core.history import HistoryManager, HISTORY_PATH
from .core.brew import (
    find_matches, exact_match, list_all_casks, is_already_installed,
    install_homebrew_package, check_brew_installed, get_installed_cask_apps
)

SYSTEM_APPLICATIONS_FOLDER = "/Applications"
USER_APPLICATIONS_FOLDER = os.path.expanduser("~/Applications")
APPLICATIONS_FOLDERS = [SYSTEM_APPLICATIONS_FOLDER, USER_APPLICATIONS_FOLDER]


def scan_applications(folders=APPLICATIONS_FOLDERS):
    """Return {app_name: folder} for every .app found; earlier folders win on duplicates."""
    apps = {}
    for folder in folders:
        if not os.path.isdir(folder):
            continue
        for entry in os.listdir(folder):
            if entry.endswith(".app"):
                apps.setdefault(os.path.splitext(entry)[0], folder)
    return apps


def process_app(app_name, history_manager, cask_tokens=None, app_dir=None, batch_mode=False, dry_run=False):
    """Process a single application with one screen per app UI."""
    # Install user-folder apps back into ~/Applications rather than /Applications
    appdir = app_dir if app_dir and app_dir != SYSTEM_APPLICATIONS_FOLDER else None

    # For batch mode, we don't clear the screen to maintain a log of progress
    if batch_mode:
        retro_print(f"\nSCANNING: {app_name}", YELLOW)
    else:
        # In interactive mode, we clear BEFORE showing the "SCANNING" message
        # so that each app starts with its own header at the top of the screen.
        clear_screen()
        print(CYAN + TITLE_ART + RESET)
        retro_print(f"SCANNING: {app_name}...", YELLOW)

    cask_matches = find_matches(app_name, cask_tokens)

    if not cask_matches:
        retro_print(f"NO MATCHES FOUND FOR {app_name}. SKIPPING...", YELLOW)
        history_manager.update(app_name, "skipped", "no_cask_found")
        time.sleep(0.6)
        return

    if batch_mode:
        # Only auto-install when the cask token is exactly the app's name;
        # anything fuzzier is left for interactive review via --retry-skipped
        selected_cask = exact_match(app_name, cask_matches)
        if not selected_cask:
            retro_print(f"NO EXACT MATCH FOR {app_name}. SKIPPING (REVIEW WITH --retry-skipped)", YELLOW)
            history_manager.update(app_name, "skipped", "no_exact_match")
            return

        type_text(f"BATCH MODE: Installing exact match '{selected_cask}'...")

        if is_already_installed(selected_cask, True):
            retro_print(f"ALREADY INSTALLED: {selected_cask}", GREEN)
            history_manager.update(app_name, "migrated", selected_cask)
            return

        if install_homebrew_package(selected_cask, True, app_name, history_manager, dry_run=dry_run, appdir=appdir):
            if dry_run:
                retro_print("DRY RUN: Skip actual install", YELLOW)
            else:
                retro_print("INSTALLATION SUCCESSFUL", GREEN)
        else:
            retro_print("BATCH INSTALL FAILED - LOGGED IN HISTORY", RED)
        return

    total_matches = len(cask_matches)
    start_idx = 0

    while True:
        clear_screen()
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
                    history_manager.update(app_name, "migrated", selected_cask)
                    time.sleep(0.8)
                    return

                retro_print(f"WARNING: This will force install '{selected_cask}'", YELLOW)
                type_text(f"ATTEMPTING TO INSTALL: {selected_cask}")

                if install_homebrew_package(selected_cask, True, app_name, history_manager, dry_run=dry_run, appdir=appdir):
                    if dry_run:
                        retro_print("DRY RUN: Skip actual install", YELLOW)
                    else:
                        retro_print("INSTALLATION SUCCESSFUL", GREEN)
                    time.sleep(0.8)
                    return
                else:
                    retro_print("\nINSTALLATION FAILED", RED)
                    press_enter_to_continue()

        elif choice == "N" and (start_idx + PAGE_SIZE) < total_matches:
            start_idx += PAGE_SIZE
        elif choice == "P" and start_idx > 0:
            start_idx -= PAGE_SIZE
        elif choice == "S":
            retro_print("SKIPPED", YELLOW)
            history_manager.update(app_name, "skipped", "user_skipped")
            time.sleep(0.5)
            return
        elif choice == "I":
            retro_print("IGNORED", RED)
            history_manager.update(app_name, "ignored", "user_ignored")
            time.sleep(0.5)
            return
        elif choice == "Q":
            retro_print("QUITTING...", RED)
            sys.exit(0)
        else:
            retro_print("INVALID CHOICE.", RED)
            press_enter_to_continue()


def main():
    """Main function to execute the script with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Migrate applications in /Applications to Homebrew Casks."
    )
    parser.add_argument(
        "--list-apps",
        action="store_true",
        help="List all applications found in /Applications and ~/Applications.",
    )
    parser.add_argument(
        "--list-pending",
        action="store_true",
        help="List applications not yet managed by Homebrew.",
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
        help="Run in batch mode, automatically install exact cask matches.",
    )
    parser.add_argument(
        "--retry-skipped",
        action="store_true",
        help="Retry apps previously skipped due to no cask found.",
    )
    parser.add_argument(
        "--retry-ignored",
        action="store_true",
        help="Retry apps previously marked as ignored.",
    )
    parser.add_argument(
        "--list-skipped",
        action="store_true",
        help="List apps currently in the skipped history.",
    )
    parser.add_argument(
        "--list-ignored",
        action="store_true",
        help="List apps currently in the ignored history.",
    )
    parser.add_argument(
        "--list-installed",
        action="store_true",
        help="List all apps successfully migrated to Homebrew.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the migration without performing any destructive actions.",
    )
    args = parser.parse_args()

    # Detect listing commands to skip intro
    listing_requested = any([args.list_apps, args.list_pending, args.list_skipped, args.list_ignored, args.list_installed])

    if not listing_requested:
        # Initial screen setup
        clear_screen()
        print(CYAN + TITLE_ART + RESET)
        type_text("INITIALIZING HOMEBREW APP MIGRATOR...\n")
        if args.dry_run:
            retro_print("DRY RUN: Nothing will be installed and history will not be saved.\n", YELLOW)

    history_manager = HistoryManager(HISTORY_PATH, persist=not args.dry_run)

    if args.reset_history:
        if history_manager.clear():
            retro_print(f"Migration history file '{HISTORY_PATH}' cleared.", GREEN)
        else:
            retro_print("No history file found to clear.", YELLOW)
        return

    if not check_brew_installed():
        retro_print("ERROR: HOMEBREW NOT FOUND. ABORT MISSION.", RED)
        return

    if not listing_requested:
        type_text(f"Loaded migration history with {len(history_manager.history)} entries\n")

    app_dirs = scan_applications()
    if not app_dirs:
        retro_print(f"ERROR: NO APPLICATIONS FOUND IN {' OR '.join(APPLICATIONS_FOLDERS)}.", RED)
        return
    app_names = sorted(app_dirs)

    if args.list_apps:
        display_retro_list("Applications found", app_names, CYAN)
        return

    if args.app and args.app not in app_dirs:
        retro_print(f"ERROR: '{args.app}' NOT FOUND. RUN --list-apps TO SEE EXACT NAMES.", RED)
        return

    # Apps already installed via a cask need no migration, whether or not this tool did it
    managed_apps = get_installed_cask_apps()

    if args.list_pending:
        pending_apps = [app for app in app_names if app not in managed_apps]
        display_retro_list("Applications not managed by Homebrew", pending_apps, CYAN)
        return

    if args.list_skipped:
        skipped_apps = history_manager.get_skipped()
        display_retro_list("Applications in SKIPPED history", skipped_apps, YELLOW)
        return

    if args.list_ignored:
        ignored_apps = history_manager.get_ignored()
        display_retro_list("Applications in IGNORED history", ignored_apps, RED)
        return

    if args.list_installed:
        installed_apps = history_manager.get_installed()
        display_retro_list("Successfully Migrated Applications", installed_apps, GREEN)
        return

    apps_to_process = []
    initial_state_history = history_manager.copy_history()

    already_managed = 0

    for app_name in app_names:
        if args.app and app_name != args.app:
            continue

        if app_name in managed_apps:
            already_managed += 1
            if args.app:
                retro_print(f"{app_name} IS ALREADY MANAGED BY HOMEBREW ({managed_apps[app_name]}).", GREEN)
            continue

        entry = history_manager.get(app_name)
        if entry:
            status = entry.get("status")
            # Migrated is a permanent lock (dry-run results never lock)
            if history_manager.is_migrated(app_name):
                continue

            # Others depend on flags
            if status == "skipped" and not args.retry_skipped:
                continue
            if status == "ignored" and not args.retry_ignored:
                continue

        apps_to_process.append(app_name)

    if already_managed and not args.app:
        type_text(f"Skipping {already_managed} apps already managed by Homebrew\n")

    cask_tokens = list_all_casks() if apps_to_process else []

    try:
        for app_name in apps_to_process:
            process_app(
                app_name,
                history_manager,
                cask_tokens=cask_tokens,
                app_dir=app_dirs[app_name],
                batch_mode=args.batch,
                dry_run=args.dry_run,
            )

    except KeyboardInterrupt:
        retro_print("\n\n!!! INTERRUPT SIGNAL RECEIVED !!!", RED)
        retro_print("SAVING PROGRESS BEFORE EXIT...", YELLOW)

    finally:
        # History is saved automatically on update, but we call get_summary for the report
        retro_print("\n" + "=" * 50, YELLOW)
        type_text("MIGRATION SESSION ENDED. GENERATING REPORT...")

        newly_migrated, failed, skipped, ignored = history_manager.get_summary(initial_state_history)

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

        if ignored:
            retro_print("\nNEWLY IGNORED APPLICATIONS:", RED)
            for entry in ignored:
                retro_print(f"  - {entry}")

        if args.dry_run:
            retro_print("\nDry run complete. History file untouched. Goodbye.", CYAN)
        else:
            retro_print("\nHistory file updated. Goodbye.", CYAN)


if __name__ == "__main__":
    main()
