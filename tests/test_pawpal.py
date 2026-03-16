from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pawpal_system


def test_task_completion_changes_status() -> None:
	pet = pawpal_system.Pet("Rufus")
	task = pawpal_system.Task(
		containedPets=[pet],
		priority=1,
		category=pawpal_system.TaskCategory.OTHER,
		maxDurationMinutes=20,
		routineTask=False,
	)

	assert task.completed is False
	task.mark_complete()
	assert task.completed is True


def test_adding_task_to_pet_increases_task_count() -> None:
	pet = pawpal_system.Pet("Rufus")
	task = pawpal_system.Task(
		containedPets=[pet],
		priority=1,
		category=pawpal_system.TaskCategory.OTHER,
		maxDurationMinutes=20,
		routineTask=False,
	)

	initial_count = len(pet.tasks)
	pet.addTask(task)

	assert len(pet.tasks) == initial_count + 1
