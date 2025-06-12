import sys
import os


def overwrite_line(*args):
	clear_line()
	print(*args)


def clear_line():
	"""
	Clears the current line in the terminal.
	"""
	# ANSI escape code to clear the line from cursor to end (2J clears entire screen, 2K clears line)
	# \x1b[2K clears the current line
	print("\x1b[2K", end="\r")


def move_cursor_up(lines: int):
	"""
	Moves the cursor up by the specified number of lines.
	"""
	# ANSI escape code to move cursor up N lines
	print(f"\x1b[{lines}A", end="")


def read_single_char() -> str:
	if os.name == "nt":  # Windows
		import msvcrt

		return msvcrt.getch().decode("utf-8", "ignore")

	else:  # Unix
		import termios
		import tty

		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setcbreak(fd)
			char = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return char
