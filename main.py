from datetime import time

import pawpal_system


o = pawpal_system.Owner("Javier")

tr1 = pawpal_system.TimeRange(time(2, 30), time(5, 30))
tr2 = pawpal_system.TimeRange(time(14, 30), time(15, 30))
tr3 = pawpal_system.TimeRange(time(20, 30), time(21, 30))

o.setAvailabilityForDay(pawpal_system.DayOfWeek.MON, [tr1, tr2, tr3])
o.setAvailabilityForDay(pawpal_system.DayOfWeek.TUE, [tr1, tr2, tr3])
o.setAvailabilityForDay(pawpal_system.DayOfWeek.WED, [tr1, tr2, tr3])
o.setAvailabilityForDay(pawpal_system.DayOfWeek.THU, [tr1, tr2, tr3])

p1 = pawpal_system.Pet("Rufus")
p1.addFoods(["Dog food", "Steak"])

m = pawpal_system.Medication("IDK", pawpal_system.FrequencyType.DAILY)
m.setTimeRanges([tr1, tr3])

p1.addMed(m)
p1.setAvgWalkingTime(45)
p1.setDailyEatingTimes(1)
p1.setDailyGroomingTimes(1)
p1.setEnrichmentFrequency(pawpal_system.FrequencyType.DAILY)
p1.setGroomingFrequency(pawpal_system.FrequencyType.DAILY)

p2 = pawpal_system.Pet("Jerry")
p2.addFoods(["Fish food"])
p2.setAvgWalkingTime(0)
p2.setDailyEatingTimes(2)
p2.setEnrichmentFrequency(pawpal_system.FrequencyType.WEEKLY)
p2.setGroomingFrequency(
    pawpal_system.FrequencyType.CUSTOM_DAYS,
    [pawpal_system.DayOfWeek.WED, pawpal_system.DayOfWeek.THU],
)

t1 = pawpal_system.Task([p1], 1, pawpal_system.TaskCategory.VET_APPOINTMENTS, 90, False)
t1.setFrequency(
    pawpal_system.FrequencyType.CUSTOM_DAYS,
    [pawpal_system.DayOfWeek.TUE, pawpal_system.DayOfWeek.THU],
)

t2 = pawpal_system.Task([p1, p2], 2, pawpal_system.TaskCategory.GROCERY_VISITS, 35, False)
t2.setFrequency(pawpal_system.FrequencyType.WEEKLY)

t3 = pawpal_system.Task([p1, p2], 3, pawpal_system.TaskCategory.ENRICHMENT, 40, False)
t3.setFrequency(pawpal_system.FrequencyType.DAILY)

t4 = pawpal_system.Task([p1,p2], 2, pawpal_system.TaskCategory.FEEDING, 25, True)
t5 = pawpal_system.Task([p1], 1, pawpal_system.TaskCategory.MEDS, 10, True)
t6 = pawpal_system.Task([p1,p2], 3, pawpal_system.TaskCategory.GROOMING, 40, True)
s = pawpal_system.Schedule()
s.setOwner(o)
s.addPet(p1)
s.addPet(p2)
s.loadTasks([t1, t2, t3, t4, t5, t6])

print(s.generateSchedule())

for scheduled_task in s.generatedScheduledTasks:
    print(
        f"{scheduled_task.day.value}: "
        f"{scheduled_task.containedTask.category.value} "
        f"{scheduled_task.timeRange.startTime.strftime('%H:%M')}-"
        f"{scheduled_task.timeRange.endTime.strftime('%H:%M')}"
    )