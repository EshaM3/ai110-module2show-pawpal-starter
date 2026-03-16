from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import time


def _minutes_since_midnight(t: time) -> int:
	"""Return the number of minutes elapsed since midnight for a given time."""
	return t.hour * 60 + t.minute


def _time_from_minutes(total_minutes: int) -> time:
	"""Convert a total-minutes-since-midnight integer back into a time object.

	Raises ValueError if the value is outside the range 0–1440.
	Caps at 23:59 if total_minutes equals exactly 1440.
	"""
	if total_minutes < 0 or total_minutes > 24 * 60:
		raise ValueError("Time is out of supported daily bounds.")
	if total_minutes == 24 * 60:
		return time(23, 59)
	return time(total_minutes // 60, total_minutes % 60)


def _add_minutes(t: time, minutes: int) -> time:
	"""Return a new time that is *minutes* after *t*."""
	return _time_from_minutes(_minutes_since_midnight(t) + minutes)


def _validate_name(name: str, field_name: str = "name") -> str:
	"""Strip whitespace from *name* and raise ValueError if the result is empty."""
	cleaned = name.strip()
	if not cleaned:
		raise ValueError(f"{field_name} cannot be empty.")
	return cleaned


def _validate_time_range(tr: TimeRange) -> None:
	"""Raise ValueError if *tr*.endTime is not strictly after *tr*.startTime."""
	if _minutes_since_midnight(tr.endTime) <= _minutes_since_midnight(tr.startTime):
		raise ValueError("TimeRange endTime must be after startTime.")


def _validate_non_overlapping_ranges(ranges: list[TimeRange]) -> list[TimeRange]:
	"""Validate and sort a list of TimeRange objects.

	Raises ValueError if any range is invalid or if any two ranges overlap.
	Returns the same ranges sorted by start time.
	"""
	for tr in ranges:
		_validate_time_range(tr)
	sorted_ranges = sorted(ranges, key=lambda r: _minutes_since_midnight(r.startTime))
	for i in range(1, len(sorted_ranges)):
		prev = sorted_ranges[i - 1]
		cur = sorted_ranges[i]
		if _minutes_since_midnight(cur.startTime) < _minutes_since_midnight(prev.endTime):
			raise ValueError("Time ranges cannot overlap.")
	return sorted_ranges


def _canonical_day_list(days: list[DayOfWeek] | None) -> list[DayOfWeek]:
	"""Deduplicate and sort a list of DayOfWeek values in calendar order (Mon–Sun)."""
	if not days:
		return []
	ordered = list(DayOfWeek)
	unique_days = sorted(set(days), key=lambda d: ordered.index(d))
	return unique_days


def _resolve_days(
	frequency_type: FrequencyType,
	custom_days: list[DayOfWeek] | None,
	days_per_week: int,
) -> list[DayOfWeek]:
	"""Return the concrete list of DayOfWeek values implied by a frequency setting.

	- DAILY          → all seven days
	- WEEKLY         → Monday only (once per week)
	- CUSTOM_DAYS    → the caller-supplied *custom_days* list (required)
	- NUMBER_OF_DAYS → the first *days_per_week* days of the week (Mon onwards)

	Raises ValueError for missing custom_days or an out-of-range days_per_week.
	"""
	if frequency_type == FrequencyType.DAILY:
		return list(DayOfWeek)
	if frequency_type == FrequencyType.WEEKLY:
		return [DayOfWeek.MON]
	if frequency_type == FrequencyType.CUSTOM_DAYS:
		days = _canonical_day_list(custom_days)
		if not days:
			raise ValueError("custom_days is required for CUSTOM_DAYS frequency.")
		return days
	if frequency_type == FrequencyType.NUMBER_OF_DAYS:
		if days_per_week < 1 or days_per_week > 7:
			raise ValueError("days_per_week must be between 1 and 7.")
		return list(DayOfWeek)[:days_per_week]
	raise ValueError("Unsupported frequency type.")


class TaskCategory(Enum):
	"""Fixed set of categories a Task can belong to."""

	FEEDING = "feeding"
	MEDS = "meds"
	WALKS = "walks"
	GROOMING = "grooming"
	ENRICHMENT = "enrichment"
	VET_APPOINTMENTS = "vet_appointments"
	GROCERY_VISITS = "grocery_visits"
	OTHER = "other"


class FrequencyType(Enum):
	"""Describes how often a Task or Medication recurs within a week."""

	DAILY = "daily"
	WEEKLY = "weekly"
	CUSTOM_DAYS = "custom_days"
	NUMBER_OF_DAYS = "number_of_days"


class DayOfWeek(Enum):
	"""Days of the week, ordered Monday through Sunday."""

	MON = "mon"
	TUE = "tue"
	WED = "wed"
	THU = "thu"
	FRI = "fri"
	SAT = "sat"
	SUN = "sun"


@dataclass
class TimeRange:
	"""A contiguous block of time within a single day.

	Attributes:
		startTime: Inclusive start of the block.
		endTime:   Exclusive end of the block (must be after startTime).
	"""

	startTime: time
	endTime: time


@dataclass
class Owner:
	"""A household member who can be assigned to care for pets.

	Attributes:
		name:         Display name of the owner.
		availability: Mapping from each day of the week to their free time blocks.
	"""

	name: str
	availability: dict[DayOfWeek, list[TimeRange]] = field(
					default_factory=lambda: 
					{d: [] for d in DayOfWeek})
	
	def setName(self, n: str) -> None:
		"""Set and validate the owner's display name."""
		self.name = _validate_name(n, "Owner name")

	def addAvailability(self, day: DayOfWeek, time_range: TimeRange) -> None:
		"""Append a single free time block to a specific day, preserving non-overlap order."""
		if day not in self.availability:
			self.availability[day] = []
		_validate_time_range(time_range)
		candidate = self.availability[day] + [time_range]
		self.availability[day] = _validate_non_overlapping_ranges(candidate)

	def setAvailabilityForDay(self, day: DayOfWeek, ranges: list[TimeRange]) -> None:
		"""Replace all free time blocks for *day* with the provided validated list."""
		self.availability[day] = _validate_non_overlapping_ranges(list(ranges))


@dataclass
class Medication:
	"""A prescription or supplement administered to a pet on a recurring schedule.

	Attributes:
		name:               Display name of the medication.
		medFrequencyType:   How often it is given across the week.
		medTimesPerDay:     Number of doses per day (0 = unset).
		medCustomDays:      Populated when frequencyType is CUSTOM_DAYS.
		medDaysPerWeek:     Populated when frequencyType is NUMBER_OF_DAYS.
		timeRangesInADay:   Preferred administration windows within a day.
	"""

	name: str
	medFrequencyType: FrequencyType
	medTimesPerDay: int = 0
	medCustomDays: list[DayOfWeek] = field(default_factory=list)
	medDaysPerWeek: int = 0
	timeRangesInADay: list[TimeRange] = field(default_factory=list)

	def setName(self, n: str) -> None:
		"""Set and validate the medication's display name."""
		self.name = _validate_name(n, "Medication name")

	def setMedicationFrequency(
		self,
		frequency_type: FrequencyType,
		custom_days: list[DayOfWeek] | None = None,
		days_per_week: int = 0,
		times_per_day: int = 0
	) -> None:
		"""Configure when this medication is administered.

		Args:
			frequency_type: The recurrence pattern (DAILY, WEEKLY, etc.).
			custom_days:    Required when frequency_type is CUSTOM_DAYS.
			days_per_week:  Required when frequency_type is NUMBER_OF_DAYS.
			times_per_day:  How many doses are given on each scheduled day.
		"""
		if times_per_day < 0:
			raise ValueError("times_per_day cannot be negative.")
		resolved_days = _resolve_days(frequency_type, custom_days, days_per_week)
		self.medFrequencyType = frequency_type
		self.medCustomDays = resolved_days if frequency_type == FrequencyType.CUSTOM_DAYS else []
		self.medDaysPerWeek = days_per_week if frequency_type == FrequencyType.NUMBER_OF_DAYS else 0
		self.medTimesPerDay = times_per_day

	def setTimeRanges(self, timeRanges: list[TimeRange]) -> None:
		"""Set preferred administration windows within a day. Ranges must not overlap."""
		self.timeRangesInADay = _validate_non_overlapping_ranges(list(timeRanges))


@dataclass
class Pet:
	"""An animal in the household whose care needs are tracked.

	Attributes:
		name:                    Display name of the pet.
		meds:                    Medications the pet takes.
		tasks:                   Tasks manually associated with this pet.
		food_pref:               Preferred food items.
		avg_daily_walking_time:  Average walk duration per day in minutes (0 = no walks).
		eating_times_per_day:    Number of feeding sessions per day (0 = not set).
		grooming_times_per_day:  Number of grooming sessions per day (0 = not set).
		groomingFrequencyType:   How often grooming recurs across the week.
		groomingCustomDays:      Populated when groomingFrequencyType is CUSTOM_DAYS.
		groomingDaysPerWeek:     Populated when groomingFrequencyType is NUMBER_OF_DAYS.
		enrichmentFrequencyType: How often enrichment recurs across the week.
		enrichmentCustomDays:    Populated when enrichmentFrequencyType is CUSTOM_DAYS.
		enrichmentDaysPerWeek:   Populated when enrichmentFrequencyType is NUMBER_OF_DAYS.
	"""

	name: str
	meds: list[Medication] = field(default_factory=list)
	tasks: list[Task] = field(default_factory=list)
	food_pref: list[str] = field(default_factory=list)
	avg_daily_walking_time: int = 0
	eating_times_per_day: int = 0
	grooming_times_per_day: int = 0

	groomingFrequencyType: FrequencyType | None = None
	groomingCustomDays: list[DayOfWeek] = field(default_factory=list)
	groomingDaysPerWeek: int = 0

	enrichmentFrequencyType: FrequencyType | None = None
	enrichmentCustomDays: list[DayOfWeek] = field(default_factory=list)
	enrichmentDaysPerWeek: int = 0

	def setName(self, n: str) -> None:
		"""Set and validate the pet's display name."""
		self.name = _validate_name(n, "Pet name")

	def addMed(self, m: Medication) -> None:
		"""Append a Medication to this pet's medication list."""
		if not isinstance(m, Medication):
			raise TypeError("m must be a Medication.")
		self.meds.append(m)

	def addTask(self, task: Task) -> None:
		"""Append a Task to this pet's personal task list."""
		if not isinstance(task, Task):
			raise TypeError("task must be a Task.")
		self.tasks.append(task)

	def addFoods(self, foods: list[str]) -> None:
		"""Extend the pet's food preference list with validated non-empty food names."""
		cleaned = [_validate_name(food, "Food item") for food in foods]
		self.food_pref.extend(cleaned)

	def setAvgWalkingTime(self, walkTimes: int) -> None:
		"""Set the average daily walking duration in minutes. Must be non-negative."""
		if walkTimes < 0:
			raise ValueError("walkTimes cannot be negative.")
		self.avg_daily_walking_time = walkTimes

	def setDailyEatingTimes(self, eatTimes: int) -> None:
		"""Set how many feeding sessions the pet needs per day. Must be non-negative."""
		if eatTimes < 0:
			raise ValueError("eatTimes cannot be negative.")
		self.eating_times_per_day = eatTimes

	def setDailyGroomingTimes(self, groomTimes: int) -> None:
		"""Set how many grooming sessions the pet needs per day. Must be non-negative."""
		if groomTimes < 0:
			raise ValueError("groomTimes cannot be negative.")
		self.grooming_times_per_day = groomTimes

	def setGroomingFrequency(
		self,
		g_frequency_type: FrequencyType,
		g_custom_days: list[DayOfWeek] | None = None,
		g_days_per_week: int = 0,
	) -> None:
		"""Configure how often this pet is groomed across the week.

		Args:
			g_frequency_type: The recurrence pattern.
			g_custom_days:    Required when g_frequency_type is CUSTOM_DAYS.
			g_days_per_week:  Required when g_frequency_type is NUMBER_OF_DAYS.
		"""
		resolved_days = _resolve_days(g_frequency_type, g_custom_days, g_days_per_week)
		self.groomingFrequencyType = g_frequency_type
		self.groomingCustomDays = resolved_days if g_frequency_type == FrequencyType.CUSTOM_DAYS else []
		self.groomingDaysPerWeek = g_days_per_week if g_frequency_type == FrequencyType.NUMBER_OF_DAYS else 0

	def setEnrichmentFrequency(
		self,
		e_frequency_type: FrequencyType,
		e_custom_days: list[DayOfWeek] | None = None,
		e_days_per_week: int = 0,
	) -> None:
		"""Configure how often this pet receives enrichment activities across the week.

		Args:
			e_frequency_type: The recurrence pattern.
			e_custom_days:    Required when e_frequency_type is CUSTOM_DAYS.
			e_days_per_week:  Required when e_frequency_type is NUMBER_OF_DAYS.
		"""
		resolved_days = _resolve_days(e_frequency_type, e_custom_days, e_days_per_week)
		self.enrichmentFrequencyType = e_frequency_type
		self.enrichmentCustomDays = resolved_days if e_frequency_type == FrequencyType.CUSTOM_DAYS else []
		self.enrichmentDaysPerWeek = e_days_per_week if e_frequency_type == FrequencyType.NUMBER_OF_DAYS else 0


@dataclass
class Task:
	"""A single care activity to be placed into the weekly schedule.

	Attributes:
		containedPets:      The pets this task is for.
		priority:           Scheduling priority (1 = highest). Managed by setPriority.
		category:           The type of care activity.
		maxDurationMinutes: Maximum time the task may occupy in minutes.
		routineTask:        If True, the task recurs every day without explicit frequency.
		frequencyType:      How often the task recurs (ignored when routineTask is True).
		customDays:         Populated when frequencyType is CUSTOM_DAYS.
		daysPerWeek:        Populated when frequencyType is NUMBER_OF_DAYS.
		timesPerDay:        How many occurrences are needed each scheduled day.
		completed:          True once mark_complete() has been called.
	"""

	containedPets: list[Pet]
	priority: int
	category: TaskCategory
	maxDurationMinutes: int
	routineTask: bool
	frequencyType: FrequencyType | None = None
	customDays: list[DayOfWeek] = field(default_factory=list)
	daysPerWeek: int = 0
	timesPerDay: int = 0
	completed: bool = False

	def setPets(self, pets: list[Pet]) -> None:
		"""Replace the pet list for this task. At least one pet is required."""
		if not pets:
			raise ValueError("A task must reference at least one pet.")
		self.containedPets = list(pets)

	def setCategory(self, category: TaskCategory) -> None:
		"""Set the care category for this task."""
		self.category = category

	def setMaxDuration(self, minutes: int) -> None:
		"""Set the maximum duration this task may occupy in the schedule. Must be > 0."""
		if minutes <= 0:
			raise ValueError("Task duration must be greater than zero.")
		self.maxDurationMinutes = minutes

	def setPriority(self, newPriority: int, tasks: list[Task]) -> None:
		"""Move this task to *newPriority* and shift all affected sibling tasks.

		Moving a task to a higher priority (lower number) pushes tasks at or below
		the target number down by one. Moving to a lower priority (higher number)
		pulls tasks above the target number up by one.

		Args:
			newPriority: Target priority (1-indexed, bounded by len(tasks)).
			tasks:       The full ordered task list this task belongs to.
		"""
		if self not in tasks:
			raise ValueError("Task must be in tasks list before reprioritizing.")
		max_priority = len(tasks)
		if max_priority == 0:
			return
		if newPriority < 1 or newPriority > max_priority:
			raise ValueError(f"newPriority must be between 1 and {max_priority}.")
		old_priority = self.priority
		if newPriority == old_priority:
			return

		if newPriority < old_priority:
			for task in tasks:
				if task is self:
					continue
				if newPriority <= task.priority < old_priority:
					task.priority += 1
		else:
			for task in tasks:
				if task is self:
					continue
				if old_priority < task.priority <= newPriority:
					task.priority -= 1

		self.priority = newPriority

	def setFrequency(
		self,
		frequency_type: FrequencyType,
		custom_days: list[DayOfWeek] | None = None,
		days_per_week: int = 0,
		times_per_day: int = 0
	) -> None:
		"""Configure the recurrence pattern for a non-routine task.

		Only valid when routineTask is False; raises ValueError otherwise.

		Args:
			frequency_type: The recurrence pattern.
			custom_days:    Required when frequency_type is CUSTOM_DAYS.
			days_per_week:  Required when frequency_type is NUMBER_OF_DAYS.
			times_per_day:  Number of occurrences needed on each scheduled day.
		"""
		if self.routineTask:
			raise ValueError("Routine tasks should not override explicit frequency.")
		if times_per_day < 0:
			raise ValueError("times_per_day cannot be negative.")
		resolved_days = _resolve_days(frequency_type, custom_days, days_per_week)
		self.frequencyType = frequency_type
		self.customDays = resolved_days if frequency_type == FrequencyType.CUSTOM_DAYS else []
		self.daysPerWeek = days_per_week if frequency_type == FrequencyType.NUMBER_OF_DAYS else 0
		self.timesPerDay = times_per_day

	def mark_complete(self) -> None:
		"""Mark this task as completed. Sets completed to True."""
		self.completed = True


@dataclass
class ScheduledTask:
	"""A concrete placement of a Task into the weekly schedule.

	Produced by Schedule.generateSchedule(). Represents a single occurrence of a
	task assigned to an owner on a specific day within a specific time window.

	Attributes:
		containedTask:  The Task being scheduled.
		containedOwner: The Owner responsible for carrying out this occurrence.
		day:            The day of the week this occurrence falls on.
		timeRange:      The exact start/end window allocated for this occurrence.
	"""

	containedTask: Task
	containedOwner: Owner
	day: DayOfWeek
	timeRange: TimeRange

	def setOwner(self, o: Owner) -> None:
		"""Replace the owner responsible for this scheduled occurrence."""
		self.containedOwner = o

	def setTask(self, t: Task) -> None:
		"""Replace the task this scheduled occurrence represents."""
		self.containedTask = t

	def setDay(self, d: DayOfWeek) -> None:
		"""Update the day of the week for this scheduled occurrence."""
		self.day = d

	def setTimeRange(self, tr: TimeRange) -> None:
		"""Set the time window for this occurrence after validating the range."""
		_validate_time_range(tr)
		self.timeRange = tr
	

@dataclass
class Schedule:
	"""The top-level container that holds all configuration and produces a weekly plan.

	Workflow:
		1. Create a Schedule instance.
		2. Call setOwner() with the household owner.
		3. Call addPet() for each pet.
		4. Create Task objects and call loadTasks() to register them.
		5. Call generateSchedule() to produce time-blocked ScheduledTask entries.

	Attributes:
		owner:                   The single household owner whose availability is used.
		pets:                    All pets in the household.
		tasks:                   User-defined tasks to be scheduled.
		generatedScheduledTasks: Output of generateSchedule(): one entry per placed occurrence.
		explanation:             Human-readable summary of scheduling results or conflicts.
	"""

	owner: Owner | None = None
	pets: list[Pet] = field(default_factory=list)
	tasks: list[Task] = field(default_factory=list)
	generatedScheduledTasks: list[ScheduledTask] = field(default_factory=list)
	explanation: str = ""

	def setOwner(self, o: Owner) -> None:
		"""Set the single household owner whose availability governs scheduling."""
		self.owner = o

	def addPet(self, p: Pet) -> None:
		"""Add a pet to the household roster."""
		if not isinstance(p, Pet):
			raise TypeError("p must be a Pet.")
		self.pets.append(p)

	def loadTasks(self, tasks: list[Task]) -> None:
		"""Store the task list and re-normalise priority values to a contiguous 1-based sequence."""
		self.tasks = list(tasks)
		for i, task in enumerate(sorted(self.tasks, key=lambda t: t.priority), start=1):
			task.priority = i

	def _resolve_task_days(self, task: Task) -> list[DayOfWeek]:
		"""Return the concrete days this task must be placed on, derived from its frequency settings."""
		if task.frequencyType is None:
			if task.routineTask:
				return list(DayOfWeek)
			raise ValueError(f"Task '{task.category.value}' is missing frequencyType.")
		return _resolve_days(task.frequencyType, task.customDays, task.daysPerWeek)

	def _find_first_fit(
		self,
		available_ranges: list[TimeRange],
		occupied_ranges: list[TimeRange],
		duration_minutes: int,
	) -> TimeRange | None:
		"""Find the earliest contiguous free slot of *duration_minutes* within *available_ranges*.

		Slots already used by *occupied_ranges* are skipped. Returns None if no
		sufficiently large gap exists.
		"""
		available_sorted = _validate_non_overlapping_ranges(list(available_ranges))
		occupied_sorted = _validate_non_overlapping_ranges(list(occupied_ranges))

		for available in available_sorted:
			cursor = _minutes_since_midnight(available.startTime)
			window_end = _minutes_since_midnight(available.endTime)

			for busy in occupied_sorted:
				busy_start = _minutes_since_midnight(busy.startTime)
				busy_end = _minutes_since_midnight(busy.endTime)

				if busy_end <= cursor:
					continue
				if busy_start >= window_end:
					break

				if busy_start - cursor >= duration_minutes:
					return TimeRange(_time_from_minutes(cursor), _time_from_minutes(cursor + duration_minutes))

				cursor = max(cursor, busy_end)
				if cursor >= window_end:
					break

			if window_end - cursor >= duration_minutes:
				return TimeRange(_time_from_minutes(cursor), _time_from_minutes(cursor + duration_minutes))

		return None

	def generateSchedule(self) -> str:
		"""Generate the weekly schedule from all loaded tasks and owner availability.

		Tasks are placed in priority order (lowest number first). For each task,
		every required day and occurrence is attempted using a first-fit strategy
		against the owner's availability, avoiding previously occupied slots.

		Returns:
			A human-readable explanation string. Lists any tasks that could not be
			placed due to insufficient availability, or confirms full success.

		Raises:
			ValueError: If no owner has been set before calling this method.
		"""
		if self.owner is None:
			raise ValueError("Schedule owner must be set before generating schedule.")

		self.generatedScheduledTasks = []
		occupied: dict[DayOfWeek, list[TimeRange]] = {day: [] for day in DayOfWeek}
		unscheduled_notes: list[str] = []

		sorted_tasks = sorted(self.tasks, key=lambda t: t.priority)

		for task in sorted_tasks:
			days = self._resolve_task_days(task)
			times_each_day = task.timesPerDay if task.timesPerDay > 0 else 1

			for day in days:
				for _ in range(times_each_day):
					owner_ranges = self.owner.availability.get(day, [])
					slot = self._find_first_fit(owner_ranges, occupied[day], task.maxDurationMinutes)
					if slot is None:
						unscheduled_notes.append(
							f"Could not place {task.category.value} (priority {task.priority}) on {day.value}."
						)
						continue

					scheduled = ScheduledTask(
						containedTask=task,
						containedOwner=self.owner,
						day=day,
						timeRange=slot,
					)
					self.generatedScheduledTasks.append(scheduled)
					occupied[day] = _validate_non_overlapping_ranges(occupied[day] + [slot])

		if unscheduled_notes:
			self.explanation = "\n".join(unscheduled_notes)
		else:
			self.explanation = "All tasks were scheduled successfully based on availability, duration, frequency, and priority."

		return self.explanation