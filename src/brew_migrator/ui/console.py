import os
import sys
import time
import threading

# ANSI color codes
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

PAGE_SIZE = 5


import shutil


def display_retro_list(title, items, color=CYAN):
    """Display a beautifully formatted retro list with multi-column support."""
    retro_print(f"\n┌─{'─' * len(title)}─┐", color)
    retro_print(f"│ {title.upper()} │", color)
    retro_print(f"└─{'─' * len(title)}─┘", color)

    if not items:
        retro_print("  (None found)", YELLOW)
        return

    sorted_items = sorted(items)

    # Calculate column widths
    term_width = shutil.get_terminal_size((80, 20)).columns
    # Add 4 for "  ▸ " bullet
    max_len = max(len(item) for item in sorted_items) + 4
    # Ensure there's at least one col and some padding
    col_width = max_len + 2
    num_cols = max(1, term_width // col_width)

    # Calculate rows needed
    num_items = len(sorted_items)
    num_rows = (num_items + num_cols - 1) // num_cols

    for r in range(num_rows):
        row_str = ""
        for c in range(num_cols):
            idx = r + c * num_rows
            if idx < num_items:
                item = sorted_items[idx]
                col_item = f"  {color}▸{RESET} {item}"
                # Add padding unless it's the last column
                if c < num_cols - 1:
                    row_str += col_item.ljust(col_width + (len(color) + len(RESET)))
                else:
                    row_str += col_item
        retro_print(row_str)
    print()

TITLE_ART = """
╔═════════════════════════════════╗
║    HOMEBREW APP MIGRATOR v0.0.2 ║
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
    options.append(("[I] IGNORE", RED))
    options.append(("[Q] QUIT", RED))

    retro_print("  " + "  ".join([f"{color}{text}{RESET}" for text, color in options]))


class ProgressBar:
    """A retro-style indeterminate progress bar."""

    def __init__(self, message=None):
        self.message = message
        self.running = False
        self._thread = None
        self.width = 20

    def _animate(self):
        pos = 0
        direction = 1

        while self.running:
            # Create a pulsing block that moves back and forth
            bar = [" "] * self.width
            # Draw a 4-block wide pulse
            for i in range(4):
                idx = (pos + i) % self.width
                bar[idx] = "█"

            bar_str = "".join(bar)
            msg = f" {YELLOW}{self.message}...{RESET}" if self.message else ""
            sys.stdout.write(f"\r{CYAN}[{bar_str}]{RESET}{msg}")
            sys.stdout.flush()

            pos += direction
            if pos >= self.width - 4 or pos <= 0:
                direction *= -1

            time.sleep(0.08)

    def __enter__(self):
        self.running = True
        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        self._thread = threading.Thread(target=self._animate)
        self._thread.daemon = True
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self._thread:
            self._thread.join()

        # Show cursor
        sys.stdout.write("\033[?25h")
        # Clean up the line thoroughly
        msg_len = len(self.message) + 4 if self.message else 0
        sys.stdout.write("\r" + " " * (self.width + msg_len + 5) + "\r")
        sys.stdout.flush()
