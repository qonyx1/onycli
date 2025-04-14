import curses
import subprocess
import json
import os
import time
import threading

BATCH_SIZE = 5

def load_programs():
    with open("programs.json", "r") as f:
        return json.load(f)

def install_batch_async(programs, selected_names, stdscr, status_lines):
    for i in range(0, len(selected_names), BATCH_SIZE):
        batch = selected_names[i:i + BATCH_SIZE]
        status_lines.append(f"Installing batch {i//BATCH_SIZE + 1} of {((len(selected_names) - 1)//BATCH_SIZE) + 1}:")
        for name in batch:
            winget_id = programs[name]
            status_lines.append(f"  Installing {name}...")
            subprocess.run([
                "winget", "install", "--id", winget_id,
                "-e", "--accept-package-agreements", "--accept-source-agreements"
            ])
        status_lines.append("  Batch complete. Waiting 2 seconds...")
        time.sleep(2)
    status_lines.append("All installations complete. Press any key to exit.")

def main(stdscr):
    curses.curs_set(0)
    programs = load_programs()
    selected = set()
    keys = list(programs.keys())
    index = 0
    install_button_index = len(keys)
    status_lines = []
    install_thread = None
    installing = False
    install_done = False

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        min_height = min(len(keys) + 6, 20)
        min_width = 40
        if height < min_height or width < min_width:
            stdscr.addstr(0, 0, "Terminal too small. Resize and try again.", curses.A_BOLD)
            stdscr.refresh()
            time.sleep(2)
            continue

        stdscr.addstr(0, 0, "Select programs to install (↑/↓ to move, Enter to toggle/select):\n")

        for i, name in enumerate(keys):
            y = i + 2
            if y >= height - 6:
                break
            prefix = "[x] " if name in selected else "[ ] "
            display_text = (prefix + name)[:width - 1]
            if i == index:
                stdscr.addstr(y, 0, display_text, curses.A_REVERSE)
            else:
                stdscr.addstr(y, 0, display_text)

        # Draw install button
        y_pos = len(keys) + 3
        if y_pos < height:
            button_text = "[ Install Programs ]"
            if len(selected):
                button_text += f" ({len(selected)})"
            display_text = button_text[:width - 1]
            if index == install_button_index:
                stdscr.addstr(y_pos, 0, display_text, curses.A_REVERSE)
            else:
                stdscr.addstr(y_pos, 0, display_text)

        # Show status messages
        for i, line in enumerate(status_lines[-(height - y_pos - 3):]):
            stdscr.addstr(y_pos + 2 + i, 0, line[:width - 1])

        stdscr.refresh()

        if installing and not install_thread.is_alive():
            installing = False
            install_done = True

        if install_done:
            stdscr.getch()
            return

        key = stdscr.getch()

        if installing:
            continue  # Lock UI input while installing

        if key in [curses.KEY_UP, ord('k')]:
            index = (index - 1) % (len(keys) + 1)
        elif key in [curses.KEY_DOWN, ord('j')]:
            index = (index + 1) % (len(keys) + 1)
        elif key == 10:  # Enter key
            if index == install_button_index:
                if not selected:
                    continue
                # Confirm install
                stdscr.clear()
                stdscr.addstr(0, 0, f"You are about to install {len(selected)} program(s). Continue? (y/n): ")
                stdscr.refresh()
                while True:
                    key = stdscr.getch()
                    if key in [ord('y'), ord('Y')]:
                        status_lines.clear()
                        status_lines.append("Starting installation...")
                        install_thread = threading.Thread(
                            target=install_batch_async,
                            args=(programs, list(selected), stdscr, status_lines),
                            daemon=True
                        )
                        install_thread.start()
                        installing = True
                        break
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
