from pathlib import Path
import sys
from datetime import time

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
import pawpal_system


def _build_sample_schedule() -> tuple[pawpal_system.Schedule, pawpal_system.Pet, pawpal_system.Pet]:
    rufus = pawpal_system.Pet("Rufus")
    jerry = pawpal_system.Pet("Jerry")
    schedule = pawpal_system.Schedule()

    t1 = pawpal_system.Task([rufus], 3, pawpal_system.TaskCategory.FEEDING, 20, True)
    t2 = pawpal_system.Task([jerry], 1, pawpal_system.TaskCategory.GROOMING, 25, True)
    t3 = pawpal_system.Task([rufus, jerry], 2, pawpal_system.TaskCategory.MEDS, 10, True)

    schedule.loadTasks([t1, t2, t3])
    return schedule, rufus, jerry


def _owner_with_ranges(day_to_ranges: dict[pawpal_system.DayOfWeek, list[pawpal_system.TimeRange]]) -> pawpal_system.Owner:
    owner = pawpal_system.Owner("Alex")
    for day, ranges in day_to_ranges.items():
        owner.setAvailabilityForDay(day, ranges)
    return owner


def test_filter_incomplete_tasks_returns_only_unfinished() -> None:
    schedule, _, _ = _build_sample_schedule()
    grooming_task = schedule.getTasksSortedByPriority()[0]
    grooming_task.mark_complete()

    incomplete = schedule.filterTasks(completion_status=False)

    assert [task.category for task in incomplete] == [
        pawpal_system.TaskCategory.MEDS,
        pawpal_system.TaskCategory.FEEDING,
    ]


def test_filter_tasks_by_pet_name_is_case_insensitive() -> None:
    schedule, _, _ = _build_sample_schedule()

    rufus_tasks = schedule.filterTasks(pet_name="RuFuS")

    assert [task.category for task in rufus_tasks] == [
        pawpal_system.TaskCategory.MEDS,
        pawpal_system.TaskCategory.FEEDING,
    ]


def test_filter_tasks_by_unknown_pet_returns_empty_list() -> None:
    schedule, _, _ = _build_sample_schedule()

    missing_pet_tasks = schedule.filterTasks(pet_name="NoSuchPet")

    assert missing_pet_tasks == []


def test_mark_complete_is_idempotent() -> None:
    pet = pawpal_system.Pet("Rufus")
    task = pawpal_system.Task(
        containedPets=[pet],
        priority=1,
        category=pawpal_system.TaskCategory.OTHER,
        maxDurationMinutes=20,
        routineTask=False,
    )

    task.mark_complete()
    task.mark_complete()

    assert task.completed is True


def test_empty_schedule_sort_and_filter_return_empty_lists() -> None:
    schedule = pawpal_system.Schedule()

    assert schedule.getTasksSortedByPriority() == []
    assert schedule.filterTasks(completion_status=True) == []
    assert schedule.filterTasks(completion_status=False) == []


def test_owner_rejects_zero_length_window() -> None:
    owner = pawpal_system.Owner("Sam")
    with pytest.raises(ValueError):
        owner.setAvailabilityForDay(
            pawpal_system.DayOfWeek.MON,
            [pawpal_system.TimeRange(time(9, 0), time(9, 0))],
        )


def test_owner_rejects_end_before_start_window() -> None:
    owner = pawpal_system.Owner("Sam")
    with pytest.raises(ValueError):
        owner.setAvailabilityForDay(
            pawpal_system.DayOfWeek.MON,
            [pawpal_system.TimeRange(time(10, 0), time(9, 59))],
        )


def test_sorting_is_normalized_to_contiguous_priorities() -> None:
    pet = pawpal_system.Pet("Rufus")
    t_low = pawpal_system.Task([pet], 99, pawpal_system.TaskCategory.OTHER, 15, True)
    t_high = pawpal_system.Task([pet], 1, pawpal_system.TaskCategory.MEDS, 15, True)
    t_mid = pawpal_system.Task([pet], 50, pawpal_system.TaskCategory.FEEDING, 15, True)

    schedule = pawpal_system.Schedule()
    schedule.loadTasks([t_low, t_high, t_mid])

    sorted_tasks = schedule.getTasksSortedByPriority()
    assert [t.priority for t in sorted_tasks] == [1, 2, 3]
    assert [t.category for t in sorted_tasks] == [
        pawpal_system.TaskCategory.MEDS,
        pawpal_system.TaskCategory.FEEDING,
        pawpal_system.TaskCategory.OTHER,
    ]


def test_generate_schedule_requires_owner() -> None:
    pet = pawpal_system.Pet("Rufus")
    task = pawpal_system.Task([pet], 1, pawpal_system.TaskCategory.FEEDING, 10, True)
    schedule = pawpal_system.Schedule()
    schedule.loadTasks([task])

    with pytest.raises(ValueError):
        schedule.generateSchedule()


def test_recurrence_custom_days_schedules_only_on_selected_days() -> None:
    pet = pawpal_system.Pet("Rufus")
    owner = _owner_with_ranges(
        {
            pawpal_system.DayOfWeek.MON: [pawpal_system.TimeRange(time(9, 0), time(10, 0))],
            pawpal_system.DayOfWeek.WED: [pawpal_system.TimeRange(time(9, 0), time(10, 0))],
        }
    )

    task = pawpal_system.Task([pet], 1, pawpal_system.TaskCategory.MEDS, 20, False)
    task.setFrequency(
        pawpal_system.FrequencyType.CUSTOM_DAYS,
        custom_days=[pawpal_system.DayOfWeek.WED, pawpal_system.DayOfWeek.MON],
    )

    schedule = pawpal_system.Schedule(owner=owner)
    schedule.loadTasks([task])
    explanation = schedule.generateSchedule()

    assert explanation.startswith("All tasks were scheduled successfully")
    assert len(schedule.generatedScheduledTasks) == 2
    assert {st.day for st in schedule.generatedScheduledTasks} == {
        pawpal_system.DayOfWeek.MON,
        pawpal_system.DayOfWeek.WED,
    }


def test_recurrence_number_of_days_uses_first_n_days() -> None:
    pet = pawpal_system.Pet("Rufus")
    owner = _owner_with_ranges(
        {
            pawpal_system.DayOfWeek.MON: [pawpal_system.TimeRange(time(8, 0), time(9, 0))],
            pawpal_system.DayOfWeek.TUE: [pawpal_system.TimeRange(time(8, 0), time(9, 0))],
            pawpal_system.DayOfWeek.WED: [pawpal_system.TimeRange(time(8, 0), time(9, 0))],
        }
    )

    task = pawpal_system.Task([pet], 1, pawpal_system.TaskCategory.WALKS, 30, False)
    task.setFrequency(
        pawpal_system.FrequencyType.NUMBER_OF_DAYS,
        days_per_week=2,
    )

    schedule = pawpal_system.Schedule(owner=owner)
    schedule.loadTasks([task])
    schedule.generateSchedule()

    assert [st.day for st in schedule.generatedScheduledTasks] == [
        pawpal_system.DayOfWeek.MON,
        pawpal_system.DayOfWeek.TUE,
    ]


def test_conflict_detection_reports_unscheduled_task() -> None:
    pet = pawpal_system.Pet("Rufus")
    owner = _owner_with_ranges(
        {
            pawpal_system.DayOfWeek.MON: [pawpal_system.TimeRange(time(9, 0), time(9, 30))],
        }
    )

    t1 = pawpal_system.Task([pet], 1, pawpal_system.TaskCategory.FEEDING, 20, False)
    t1.setFrequency(pawpal_system.FrequencyType.WEEKLY)

    t2 = pawpal_system.Task([pet], 2, pawpal_system.TaskCategory.GROOMING, 20, False)
    t2.setFrequency(pawpal_system.FrequencyType.WEEKLY)

    schedule = pawpal_system.Schedule(owner=owner)
    schedule.loadTasks([t1, t2])

    explanation = schedule.generateSchedule()

    assert len(schedule.generatedScheduledTasks) == 1
    assert "could not place grooming (priority 2) on mon." in explanation.lower()
    only_slot = schedule.generatedScheduledTasks[0].timeRange
    assert str(only_slot) == "09:00-09:20"


def test_recurrence_validation_rejects_invalid_custom_days_and_day_count() -> None:
    pet = pawpal_system.Pet("Rufus")
    task = pawpal_system.Task([pet], 1, pawpal_system.TaskCategory.OTHER, 10, False)

    with pytest.raises(ValueError):
        task.setFrequency(pawpal_system.FrequencyType.CUSTOM_DAYS, custom_days=[])

    with pytest.raises(ValueError):
        task.setFrequency(pawpal_system.FrequencyType.NUMBER_OF_DAYS, days_per_week=0)