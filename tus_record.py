from tui_utils import read_single_char
from tus_types import Answer, Quiz


NUM_QUESTIONS = 200


def record_quiz() -> Quiz | None:
	"""
	Record a new quiz into the database
	"""

	print("Entering new quiz...\n")

	new_quiz = Quiz()

	print(
		(
			f"Press {Answer.CORRECT} for a correct answer, "
			f"{Answer.WRONG} for a wrong answer, "
			f"{Answer.EMPTY} for an empty answer, "
			"Backspace to delete last answer"
		)
	)
	print("Press CTRL+C to abort.")
	new_quiz.paint_answers()

	quiz_complete = False

	try:
		while not quiz_complete:
			char_input = read_single_char()
			if char_input == "\x03":
				raise KeyboardInterrupt
			if char_input in ["\x08", "\x7f"]:
				new_quiz.erase()
				new_quiz.paint_answers()
				continue
			if char_input not in Answer:
				continue
			quiz_complete = new_quiz.update(Answer(char_input))
			new_quiz.paint_answers()
	except KeyboardInterrupt:
		print("Quiz aborted by user.\n")
		return None

	print("Quiz entry successful.")
	return new_quiz


def main():
	record_quiz()


if __name__ == "__main__":
	main()
