classDiagram
direction TB

class Owner {
  +String name
  +List~TimeRange~[7] availabilityByDay
  +addAvailability(day: DayOfWeek, range: TimeRange) void
  +setAvailabilityForDay(day: DayOfWeek, ranges: List~TimeRange~) void
}

class Pet {
  +String name
}

class Task {
  +int priority
  +TaskCategory category
  +int maxDurationMinutes
  +FrequencyType frequencyType
  +List~DayOfWeek~ customDays
  +int daysPerWeek
  +List~TimeRange~[7] timeRangesByDay
  +setCategory(category: TaskCategory) void
  +setMaxDuration(minutes: int) void
  +setFrequency(type: FrequencyType, customDays: List~DayOfWeek~, daysPerWeek: int) void
  +movePriority(newPriority: int, allTasks: List~Task~) void
}

class Schedule {
  +List~Owner~ owners
  +List~Pet~ pets
  +List~Task~ tasks
  +List~Task~ generatedTaskBlocks
  +String explanation
  +addOwner(name: String, availabilityByDay: List~TimeRange~[7]) void
  +addPet(name: String) void
  +addTask(category: TaskCategory, maxDurationMinutes: int, frequencyType: FrequencyType, customDays: List~DayOfWeek~, daysPerWeek: int) void
  +generateSchedule() void
}

class TimeRange {
  +String startTime
  +String endTime
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

Schedule "1" *-- "0..*" Owner : holds
Schedule "1" *-- "0..*" Pet : holds
Schedule "1" *-- "0..*" Task : holds
Schedule "1" o-- "0..*" Task : generatedTaskBlocks
Owner "1" o-- "7" List~TimeRange~ : weekly availability
Task "1" o-- "7" List~TimeRange~ : scheduled windows