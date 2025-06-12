from db_utils import save_quiz_record
from tui_utils import read_single_char
from tus_types import Answer, Quiz


NUM_QUESTIONS = 200


def record_quiz():
	"""
	Record a new quiz into the database
	"""
	new_quiz = Quiz()

	print(
		(
			f"{Answer.CORRECT} -> Doğru\n"
			f"{Answer.WRONG} -> Yanlış\n"
			f"{Answer.EMPTY} -> Boş\n"
			"Backspace -> Sil\n"
			"CTRL+C -> İptal"
			"\n"
		)
	)

	new_quiz.paint_answers()
	quiz_complete = False

	try:
		while not quiz_complete:
			char_input = read_single_char().upper()
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

	print("Quiz entry successful.")
	save_quiz_record(new_quiz)


def main():
	record_quiz()


if __name__ == "__main__":
	main()
