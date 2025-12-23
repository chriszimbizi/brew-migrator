import os
import sys
import time

# ANSI color codes
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

PAGE_SIZE = 5

TITLE_ART = """
╔═════════════════════════════════╗
║    HOMEBREW APP MIGRATOR v0.0.1 ║
╚═════════════════════════════════╝
"""


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


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


def press_enter_to_continue():
    """Pauses execution until user presses Enter."""
    print()
    input(f"{YELLOW}[PRESS ENTER TO CONTINUE]{RESET}")


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
