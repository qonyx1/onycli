import curses
import subprocess
import json
import os
import time

BATCH_SIZE = 5

def load_programs():
    with open("programs.json", "r") as f:
        return json.load(f)

def install_batch(programs, selected_names, stdscr):
    for i in range(0, len(selected_names), BATCH_SIZE):
        batch = selected_names[i:i + BATCH_SIZE]
        stdscr.addstr(f"\nInstalling batch {i//BATCH_SIZE + 1} of {((len(selected_names) - 1)//BATCH_SIZE) + 1}:\n")
        stdscr.refresh()
        for name in batch:
            winget_id = programs[name]
            stdscr.addstr(f"  Installing {name}...\n")
            stdscr.refresh()
            subprocess.run([
                "winget", "install", "--id", winget_id,
                "-e", "--accept-package-agreements", "--accept-source-agreements"
            ])
        stdscr.addstr("  Batch complete. Waiting 2 seconds...\n")
        stdscr.refresh()
        time.sleep(2)

def main(stdscr):
    curses.curs_set(0)
    programs = load_programs()
    selected = set()
    keys = list(programs.keys())
    index = 0
    install_button_index = len(keys)

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select programs to install (↑/↓ to move, Enter to toggle/select):\n")

        for i, name in enumerate(keys):
            prefix = "[x] " if name in selected else "[ ] "
            if i == index:
                stdscr.addstr(i + 2, 0, prefix + name, curses.A_REVERSE)
            else:
                stdscr.addstr(i + 2, 0, prefix + name)

        # Draw install button
        y_pos = len(keys) + 3
        button_text = f"[ Install {len(selected)} Selected Program{'s' if len(selected) != 1 else ''} ]"
        if index == install_button_index:
            stdscr.addstr(y_pos, 0, button_text, curses.A_REVERSE)
        else:
            stdscr.addstr(y_pos, 0, button_text)

        stdscr.refresh()
        key = stdscr.getch()

        if key in [curses.KEY_UP, ord('k')]:
            index = (index - 1) % (len(keys) + 1)
        elif key in [curses.KEY_DOWN, ord('j')]:
            index = (index + 1) % (len(keys) + 1)
        elif key == 10:  # Enter
            if index == install_button_index:
                if not selected:
                    continue
                # Confirm installation
                stdscr.clear()
                stdscr.addstr(0, 0, f"You are about to install {len(selected)} program(s). Continue? (y/n): ")
                stdscr.refresh()
                while True:
                    key = stdscr.getch()
                    if key in [ord('y'), ord('Y')]:
                        stdscr.clear()
                        stdscr.addstr(0, 0, "Beginning installation...\n")
                        stdscr.refresh()
                        install_batch(programs, list(selected), stdscr)
                        stdscr.addstr("\nAll installations complete. Press any key to exit.")
                        stdscr.getch()
                        return
                    elif key in [ord('n'), ord('N')]:
                        break
            else:
                name = keys[index]
                if name in selected:
                    selected.remove(name)
                else:
                    selected.add(name)

if __name__ == "__main__":
    if not os.path.exists("programs.json"):
        print("Error: programs.json file not found.")
    else:
        curses.wrapper(main)
