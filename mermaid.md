classDiagram
direction TB

class Owner {
  +String name
  +Dict~DayOfWeek, List~TimeRange~~ availability
  +setName(n: String) void
  +addAvailability(day: DayOfWeek, time_range: TimeRange) void
  +setAvailabilityForDay(day: DayOfWeek, ranges: List~TimeRange~) void
}

class Pet {
  +String name
  +List~Medication~ meds
  +List~Task~ tasks
  +List~String~ food_pref
  +int avg_daily_walking_time
  +int eating_times_per_day
  +int grooming_times_per_day
  +FrequencyType groomingFrequencyType
  +List~DayOfWeek~ groomingCustomDays
  +int groomingDaysPerWeek
  +FrequencyType enrichmentFrequencyType
  +List~DayOfWeek~ enrichmentCustomDays
  +int enrichmentDaysPerWeek
  +setName(n: String) void
  +addMed(m: Medication) void
  +addTask(task: Task) void
  +addFoods(foods: List~String~) void
  +setAvgWalkingTime(walkTimes: int) void
  +setDailyEatingTimes(eatTimes: int) void
  +setDailyGroomingTimes(groomTimes: int) void
  +setGroomingFrequency(type: FrequencyType, customDays: List~DayOfWeek~, daysPerWeek: int) void
  +setEnrichmentFrequency(type: FrequencyType, customDays: List~DayOfWeek~, daysPerWeek: int) void
}

class Medication {
  +String name
  +FrequencyType medFrequencyType
  +int medTimesPerDay
  +List~DayOfWeek~ medCustomDays
  +int medDaysPerWeek
  +List~TimeRange~ timeRangesInADay
  +setName(n: String) void
  +setMedicationFrequency(type: FrequencyType, customDays: List~DayOfWeek~, daysPerWeek: int, timesPerDay: int) void
  +setTimeRanges(timeRanges: List~TimeRange~) void
}

class Task {
  +List~Pet~ containedPets
  +int priority
  +TaskCategory category
  +int maxDurationMinutes
  +bool routineTask
  +FrequencyType frequencyType
  +List~DayOfWeek~ customDays
  +int daysPerWeek
  +int timesPerDay
  +bool completed
  +setPets(pets: List~Pet~) void
  +setCategory(category: TaskCategory) void
  +setMaxDuration(minutes: int) void
  +setPriority(newPriority: int, tasks: List~Task~) void
  +setFrequency(type: FrequencyType, customDays: List~DayOfWeek~, daysPerWeek: int, timesPerDay: int) void
  +mark_complete() void
}

class ScheduledTask {
  +Task containedTask
  +Owner containedOwner
  +DayOfWeek day
  +TimeRange timeRange
  +setOwner(o: Owner) void
  +setTask(t: Task) void
  +setDay(d: DayOfWeek) void
  +setTimeRange(tr: TimeRange) void
}

class Schedule {
  +Owner owner
  +List~Pet~ pets
  +List~Task~ tasks
  +List~ScheduledTask~ generatedScheduledTasks
  +String explanation
  +setOwner(o: Owner) void
  +addPet(p: Pet) void
  +loadTasks(tasks: List~Task~) void
  +getTasksSortedByPriority() List~Task~
  +filterTasks(completion_status: bool, pet_name: String) List~Task~
  +generateSchedule() String
}

class TimeRange {
  +time startTime
  +time endTime
}

class TaskCategory {
  <<enumeration>>
  FEEDING
  MEDS
  WALKS
  GROOMING
  ENRICHMENT
  VET_APPOINTMENTS
  GROCERY_VISITS
  OTHER
}

class FrequencyType {
  <<enumeration>>
  DAILY
  WEEKLY
  CUSTOM_DAYS
  NUMBER_OF_DAYS
}

class DayOfWeek {
  <<enumeration>>
  MON
  TUE
  WED
  THU
  FRI
  SAT
  SUN
}

Schedule "1" *-- "1" Owner : owner
Schedule "1" *-- "0..*" Pet : pets
Schedule "1" *-- "0..*" Task : tasks
Schedule "1" *-- "0..*" ScheduledTask : generatedScheduledTasks
Pet "1" o-- "0..*" Medication : meds
Pet "1" o-- "0..*" Task : tasks
Task "1" --> "1..*" Pet : containedPets
ScheduledTask "*" --> "1" Task : containedTask
ScheduledTask "*" --> "1" Owner : containedOwner
ScheduledTask "*" --> "1" TimeRange : timeRange
Owner "1" --> "0..*" TimeRange : availability
