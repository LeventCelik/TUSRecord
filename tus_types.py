import datetime
from enum import StrEnum
from copy import deepcopy

from tui_utils import move_cursor_up, overwrite_line

NUM_QUESTIONS_PER_CATEGORY = 100


class Answer(StrEnum):
	CORRECT = "D"
	WRONG = "Y"
	EMPTY = "B"
	MISSING = " "


class Subject:
	def __init__(self, name: str, question_count: int):
		self.name = name
		self.answers: list[Answer] = [Answer.MISSING] * question_count

	@property
	def question_count(self):
		return len(self.answers)

	@property
	def num_correct(self):
		return self.answers.count(Answer.CORRECT)

	@property
	def num_wrong(self):
		return self.answers.count(Answer.WRONG)

	@property
	def num_empty(self):
		return self.answers.count(Answer.EMPTY)

	@property
	def num_net(self):
		return self.num_correct - self.num_wrong / 4

	def __len__(self) -> int:
		return self.question_count

	def __getitem__(self, index: int) -> Answer:
		return self.answers[index]

	def __setitem__(self, index: int, value: Answer):
		self.answers[index] = value

	def __str__(self):
		return (
			f"{self.name}:\t"
			+ f"{self.num_correct:3d}{Answer.CORRECT} "
			+ f"{self.num_wrong:3d}{Answer.WRONG} "
			+ f"{self.num_empty:3d}{Answer.EMPTY} "
			+ f"-> {self.num_net:5.2f} "
			+ "".join([f"[{answer}]" for answer in self.answers])
		)

	def __repr__(self):
		return f"Subject(name={self.name}, answers={self.answers})"

	def __copy__(self):
		cls = self.__class__
		result = cls.__new__(cls)
		result.__dict__.update(self.__dict__)
		return result

	def __deepcopy__(self, memo):
		cls = self.__class__
		result = cls.__new__(cls)
		memo[id(self)] = result
		for k, v in self.__dict__.items():
			setattr(result, k, deepcopy(v, memo))
		return result

	def to_dict(self) -> dict:
		"""To serialize"""
		return {"name": self.name, "answers": [answer.value for answer in self.answers]}


theoretical_blueprints = [
	Subject("Anatomi", 13),
	Subject("Fizyoloji", 15),
	Subject("Biyokimya", 18),
	Subject("Mikrobiyoloji", 18),
	Subject("Patoloji", 18),
	Subject("Farmakoloji", 18),
]


clinical_blueprints = [
	Subject("Dahiliye", 25),
	Subject("Dahili KS", 10),
	Subject("Pediatri", 25),
	Subject("Genel Cerrahi", 21),
	Subject("Cerrahi KS", 9),
	Subject("Kadın Doğum", 10),
]


class SubjectArrayMutableConcatenatedView:
	"""
	Provides a mutable, single-array-like view over a dictionary of subjects.
	Allows accessing and modifying elements using a single absolute index.
	"""

	def __init__(self, data: dict[str, Subject]):
		self._data = data
		# Segment information: (key, absolute_start_index, absolute_end_index, subject)
		self._segment_info: list[tuple[str, int, int, Subject]] = []

		absolute_index = 0
		for key, subject in self._data.items():
			start = absolute_index
			end = absolute_index + len(subject)
			self._segment_info.append((key, start, end, subject))
			absolute_index = end
		self._total_length = absolute_index
		self._index_to_update = 0

	def _get_internal_coords(self, absolute_index: int) -> tuple[str, int, Subject]:
		"""
		Translates an absolute index in the concatenated view to a (key, internal_index) pair.
		Also returns a reference to the actual Subject.
		Raises IndexError if absolute_index is out of bounds.
		"""

		if not 0 <= absolute_index < self._total_length:
			raise IndexError(
				f"Absolute index {absolute_index} out of bounds [0, {self._total_length})."
			)

		for key, start, end, subject in self._segment_info:
			if start <= absolute_index < end:
				internal_list_index = absolute_index - start
				return key, internal_list_index, subject

		raise RuntimeError(
			f"Internal error: Could not map absolute index {absolute_index} to any segment."
		)

	@property
	def current_index(self) -> int:
		return self._index_to_update

	def __len__(self) -> int:
		"""
		Allows using len()
		"""
		return self._total_length

	def __getitem__(self, absolute_index: int) -> Answer:
		"""
		Allows array-like get-access using bracket notation.
		"""
		_, internal_index, subject = self._get_internal_coords(absolute_index)
		return subject[internal_index]

	def __setitem__(self, absolute_index: int, value: Answer):
		"""
		Allows array-like set-access using bracket notation.
		"""
		_, internal_index, subject = self._get_internal_coords(absolute_index)
		subject[internal_index] = value

	def get_relative_position(self, absolute_index: int) -> tuple[str, int] | None:
		"""
		Returns the (key, internal_index) tuple for an absolute position.
		Returns None if the index is out of bounds.
		"""
		try:
			key, internal_index, _ = self._get_internal_coords(absolute_index)
			return key, internal_index
		except IndexError:
			return None

	def update_next(self, answer: Answer) -> bool:
		if self._index_to_update >= len(self):
			raise IndexError("Internal error: Could not update answer")
		self[self._index_to_update] = answer
		self._index_to_update += 1
		return self._index_to_update == len(self)

	def erase_last(self) -> bool:
		if self._index_to_update < 0:
			raise IndexError("Internal error: Could not erase answer")
		if self._index_to_update == 0:
			return False
		self._index_to_update -= 1
		self[self._index_to_update] = Answer.MISSING
		return True


class QuizCategory:
	def __init__(self, name: str, subject_blueprints: list[Subject]):
		self.name = name
		self._subjects_dict: dict[str, Subject] = {
			subject.name: deepcopy(subject) for subject in subject_blueprints
		}
		self._array_view = SubjectArrayMutableConcatenatedView(self._subjects_dict)
		assert (
			len(self.array_view) == NUM_QUESTIONS_PER_CATEGORY
		), f"{len(self.array_view)} questions in {name} instead of {NUM_QUESTIONS_PER_CATEGORY}"

	@property
	def map_view(self) -> dict[str, Subject]:
		return self._subjects_dict

	@property
	def array_view(self) -> SubjectArrayMutableConcatenatedView:
		return self._array_view

	@property
	def num_correct(self):
		return sum(subject.num_correct for subject in self.map_view.values())

	@property
	def num_wrong(self):
		return sum(subject.num_wrong for subject in self.map_view.values())

	@property
	def num_empty(self):
		return sum(subject.num_empty for subject in self.map_view.values())

	@property
	def num_net(self):
		return sum(subject.num_net for subject in self.map_view.values())

	def to_dict(self) -> dict:
		"""To serialize"""
		return {
			"name": self.name,
			"subjects": {
				name: subject.to_dict() for name, subject in self._subjects_dict.items()
			},
		}


class Quiz:
	def __init__(
		self,
		theoretical: list[Subject] | None = None,
		clinical: list[Subject] | None = None,
	):
		self.theoretical = QuizCategory(
			name="Temel",
			subject_blueprints=theoretical
			if theoretical is not None
			else theoretical_blueprints,
		)
		self.clinical = QuizCategory(
			name="Klinik",
			subject_blueprints=clinical
			if clinical is not None
			else clinical_blueprints,
		)

		self._length = len(self.theoretical.array_view) + len(self.clinical.array_view)
		self._current: QuizCategory = self.theoretical
		self._answers_painted = False
		self.created_at = datetime.datetime.now().strftime("%y_%m_%d")

	@property
	def subject_count(self):
		return len(self.theoretical.map_view) + len(self.clinical.map_view)

	@property
	def _num_painted_lines(self):
		return self.subject_count + 2

	def __len__(self):
		return self._length

	def _display_answers(self):
		overwrite_line(
			f"{self.theoretical.name}: ({self.theoretical.array_view.current_index:2d}/{NUM_QUESTIONS_PER_CATEGORY}) \t"
			+ f"{self.theoretical.num_correct:3d}{Answer.CORRECT} "
			+ f"{self.theoretical.num_wrong:3d}{Answer.WRONG} "
			+ f"{self.theoretical.num_empty:3d}{Answer.EMPTY} "
			+ f"-> {self.theoretical.num_net:5.2f}"
		)
		for subject in self.theoretical.map_view.values():
			overwrite_line(f"\t{subject}")
		overwrite_line(
			f"{self.clinical.name}: ({self.clinical.array_view.current_index:2d}/{NUM_QUESTIONS_PER_CATEGORY}) \t"
			+ f"{self.clinical.num_correct:3d}{Answer.CORRECT} "
			+ f"{self.clinical.num_wrong:3d}{Answer.WRONG} "
			+ f"{self.clinical.num_empty:3d}{Answer.EMPTY} "
			+ f"-> {self.clinical.num_net:5.2f}"
		)
		for subject in self.clinical.map_view.values():
			overwrite_line(f"\t{subject}")

	def paint_answers(self):
		if self._answers_painted:
			move_cursor_up(self._num_painted_lines)
		else:
			self._answers_painted = True
		self._display_answers()

	def update(self, answer: Answer) -> bool:
		if not self._current.array_view.update_next(answer):
			return False
		if self._current != self.clinical:
			self._current = self.clinical
			return False
		return True

	def erase(self) -> bool:
		return self._current.array_view.erase_last()

	def to_dict(self) -> dict:
		"""To serialize"""
		return {
			"created_at": self.created_at,
			"theoretical": self.theoretical.to_dict(),
			"clinical": self.clinical.to_dict(),
		}
