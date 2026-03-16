from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TaskCategory(Enum):
	FEEDING = "feeding"
	MEDS = "meds"
	WALKS = "walks"
	GROOMING = "grooming"
	ENRICHMENT = "enrichment"
	VET_APPOINTMENTS = "vet_appointments"
	GROCERY_VISITS = "grocery_visits"
	OTHER = "other"


class FrequencyType(Enum):
	DAILY = "daily"
	WEEKLY = "weekly"
	CUSTOM_DAYS = "custom_days"
	NUMBER_OF_DAYS = "number_of_days"


class DayOfWeek(Enum):
	MON = "mon"
	TUE = "tue"
	WED = "wed"
	THU = "thu"
	FRI = "fri"
	SAT = "sat"
	SUN = "sun"


@dataclass
class TimeRange:
	startTime: str
	endTime: str


@dataclass
class Owner:
	name: str
	availabilityByDay: list[list[TimeRange]] = field(default_factory=lambda: [[] for _ in range(7)])

	def addAvailability(self, day: DayOfWeek, time_range: TimeRange) -> None:
		pass

	def setAvailabilityForDay(self, day: DayOfWeek, ranges: list[TimeRange]) -> None:
		pass


@dataclass
class Pet:
	name: str


@dataclass
class Task:
	priority: int
	category: TaskCategory
	maxDurationMinutes: int
	frequencyType: FrequencyType
	customDays: list[DayOfWeek] = field(default_factory=list)
	daysPerWeek: int = 0
	timeRangesByDay: list[list[TimeRange]] = field(default_factory=lambda: [[] for _ in range(7)])

	def setCategory(self, category: TaskCategory) -> None:
		pass

	def setMaxDuration(self, minutes: int) -> None:
		pass

	def setFrequency(
		self,
		frequency_type: FrequencyType,
		custom_days: list[DayOfWeek] | None = None,
		days_per_week: int = 0,
	) -> None:
		pass

	def movePriority(self, newPriority: int, allTasks: list[Task]) -> None:
		pass


@dataclass
class Schedule:
	owners: list[Owner] = field(default_factory=list)
	pets: list[Pet] = field(default_factory=list)
	tasks: list[Task] = field(default_factory=list)
	generatedTaskBlocks: list[Task] = field(default_factory=list)
	explanation: str = ""

	def addOwner(self, name: str, availabilityByDay: list[list[TimeRange]]) -> None:
		pass

	def addPet(self, name: str) -> None:
		pass

	def addTask(
		self,
		category: TaskCategory,
		maxDurationMinutes: int,
		frequencyType: FrequencyType,
		customDays: list[DayOfWeek] | None = None,
		daysPerWeek: int = 0,
	) -> None:
		pass

	def generateSchedule(self) -> None:
		pass
