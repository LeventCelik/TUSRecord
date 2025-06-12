import json
import os
from tus_types import Quiz


QUIZ_RECORDS_DIR = "quiz_records"


def save_quiz_record(quiz_instance: Quiz):
	"""
	Serializes a Quiz instance to a JSON file in the quiz_records directory.
	"""
	os.makedirs(QUIZ_RECORDS_DIR, exist_ok=True)
	filename = f"quiz_{quiz_instance.created_at}.json"
	filepath = os.path.join(QUIZ_RECORDS_DIR, filename)

	quiz_data = quiz_instance.to_dict()

	try:
		with open(filepath, "w", encoding="utf-8") as f:
			json.dump(quiz_data, f, indent=4)
		print(f"Quiz record saved to {filepath}")
	except IOError as e:
		print(f"Error saving quiz record: {e}")
