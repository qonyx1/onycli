import curses
import subprocess
import json
import os

def load_programs():
    with open("programs.json", "r") as f:
        return json.load(f)

def main(stdscr):
    curses.curs_set(0)
    programs = load_programs()
    selected = set()
    keys = list(programs.keys())
    index = 0
    install_button_index = len(keys)  # "Install" is after the last item

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select programs to install (↑/↓ to move, Enter to toggle/select):\n")

        for i, name in enumerate(keys):
            prefix = "[x] " if name in selected else "[ ] "
            if i == index:
                stdscr.addstr(i + 2, 0, prefix + name, curses.A_REVERSE)
            else:
                stdscr.addstr(i + 2, 0, prefix + name)

        button_text = "[ Install Selected Programs ]"
        y_pos = len(keys) + 3
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
                break  # Begin installation
            else:
                name = keys[index]
                if name in selected:
                    selected.remove(name)
                else:
                    selected.add(name)

    stdscr.clear()
    stdscr.addstr(0, 0, "Installing selected programs...\n\n")
    stdscr.refresh()

    for name in selected:
        winget_id = programs[name]
        stdscr.addstr(f"Installing {name}...\n")
        stdscr.refresh()
        subprocess.run([
            "winget", "install", "--id", winget_id,
            "-e", "--accept-package-agreements", "--accept-source-agreements"
        ])
    stdscr.addstr("\nAll installations complete. Press any key to exit.")
    stdscr.getch()

if __name__ == "__main__":
    if not os.path.exists("programs.json"):
        print("Error: programs.json file not found.")
    else:
        curses.wrapper(main)
