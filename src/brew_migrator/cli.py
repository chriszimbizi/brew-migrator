import os
import sys
import time
import argparse
from .ui.console import (
    TITLE_ART, type_text, retro_input, retro_print,
    press_enter_to_continue, display_paginated_matches,
    display_retro_list, GREEN, CYAN, YELLOW, RED, RESET, PAGE_SIZE
)
from .core.history import HistoryManager, HISTORY_PATH
from .core.brew import (
    find_matches, is_already_installed, install_homebrew_package, check_brew_installed
)

APPLICATIONS_FOLDER = "/Applications"


def process_app(app_name, history_manager, batch_mode=False, dry_run=False):
    """Process a single application with one screen per app UI."""
    # For batch mode, we don't clear the screen to maintain a log of progress
    if batch_mode:
        retro_print(f"\nSCANNING: {app_name}", YELLOW)
    else:
        # In interactive mode, we clear BEFORE showing the "SCANNING" message
        # so that each app starts with its own header at the top of the screen.
        from .ui.console import clear_screen
        clear_screen()
        print(CYAN + TITLE_ART + RESET)
        retro_print(f"SCANNING: {app_name}...", YELLOW)

    cask_matches = find_matches(app_name, "cask")

    if not cask_matches:
        retro_print(f"NO MATCHES FOUND FOR {app_name}. SKIPPING...", YELLOW)
        history_manager.update(app_name, "skipped", "no_cask_found")
        time.sleep(0.6)
        return

    if batch_mode:
        selected_cask = cask_matches[0]
        type_text(f"BATCH MODE: Installing top match '{selected_cask}'...")

        if is_already_installed(selected_cask, True):
            retro_print(f"ALREADY INSTALLED: {selected_cask}", GREEN)
            history_manager.update(app_name, "migrated", selected_cask)
            return

        if install_homebrew_package(selected_cask, True, app_name, history_manager, dry_run=dry_run):
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
        from .ui.console import clear_screen
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

                if install_homebrew_package(selected_cask, True, app_name, history_manager, dry_run=dry_run):
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
    listing_requested = any([args.list_apps, args.list_skipped, args.list_ignored, getattr(args, 'list_installed', False)])

    if not listing_requested:
        # Initial screen setup
        from .ui.console import clear_screen
        clear_screen()
        print(CYAN + TITLE_ART + RESET)
        type_text("INITIALIZING HOMEBREW APP MIGRATOR...\n")

    history_manager = HistoryManager(HISTORY_PATH)

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

    if not os.path.exists(APPLICATIONS_FOLDER):
        retro_print(f"ERROR: {APPLICATIONS_FOLDER} NOT FOUND.", RED)
        return

    app_names = sorted(
        [
            os.path.splitext(app)[0]
            for app in os.listdir(APPLICATIONS_FOLDER)
            if app.endswith(".app")
        ]
    )

    if args.list_apps:
        display_retro_list("Applications in /Applications", app_names, CYAN)
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

    for app_name in app_names:
        if args.app and app_name != args.app:
            continue

        entry = history_manager.get(app_name)
        if entry:
            status = entry.get("status")
            # Migrated is a permanent lock
            if status.startswith("migrated"):
                continue

            # Others depend on flags
            if status == "skipped" and not args.retry_skipped:
                continue
            if status == "ignored" and not args.retry_ignored:
                continue

        apps_to_process.append(app_name)

    try:
        for app_name in apps_to_process:
            process_app(app_name, history_manager, batch_mode=args.batch, dry_run=args.dry_run)

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

        retro_print("\nHistory file updated. Goodbye.", CYAN)


if __name__ == "__main__":
    main()
