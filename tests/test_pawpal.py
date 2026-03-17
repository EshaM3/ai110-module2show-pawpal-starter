from pathlib import Path
import sys
from datetime import time

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


def test_schedule_time_strings_use_hh_mm_format() -> None:
	pet = pawpal_system.Pet("Rufus")
	owner = pawpal_system.Owner("Sam")
	task = pawpal_system.Task(
		containedPets=[pet],
		priority=1,
		category=pawpal_system.TaskCategory.WALKS,
		maxDurationMinutes=45,
		routineTask=False,
	)
	task.setFrequency(pawpal_system.FrequencyType.WEEKLY, times_per_day=1)
	time_range = pawpal_system.TimeRange(time(9, 5), time(9, 50))
	scheduled = pawpal_system.ScheduledTask(
		containedTask=task,
		containedOwner=owner,
		day=pawpal_system.DayOfWeek.MON,
		timeRange=time_range,
	)

	assert str(time_range) == "09:05-09:50"
	assert str(scheduled) == "mon: walks 09:05-09:50"


def test_schedule_sorting_and_filtering_methods() -> None:
	rufus = pawpal_system.Pet("Rufus")
	jerry = pawpal_system.Pet("Jerry")
	schedule = pawpal_system.Schedule()

	t1 = pawpal_system.Task([rufus], 3, pawpal_system.TaskCategory.FEEDING, 20, True)
	t2 = pawpal_system.Task([jerry], 1, pawpal_system.TaskCategory.GROOMING, 25, True)
	t3 = pawpal_system.Task([rufus, jerry], 2, pawpal_system.TaskCategory.MEDS, 10, True)
	schedule.loadTasks([t1, t2, t3])

	t2.mark_complete()

	sorted_tasks = schedule.getTasksSortedByPriority()
	assert [task.category for task in sorted_tasks] == [
		pawpal_system.TaskCategory.GROOMING,
		pawpal_system.TaskCategory.MEDS,
		pawpal_system.TaskCategory.FEEDING,
	]

	completed_tasks = schedule.filterTasks(completion_status=True)
	assert [task.category for task in completed_tasks] == [pawpal_system.TaskCategory.GROOMING]

	rufus_tasks = schedule.filterTasks(pet_name="rufus")
	assert [task.category for task in rufus_tasks] == [
		pawpal_system.TaskCategory.MEDS,
		pawpal_system.TaskCategory.FEEDING,
	]
