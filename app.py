import streamlit as st
import pawpal_system
from datetime import time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")

st.markdown("### Owner")
st.caption("Create or update owner details.")
owner_name = st.text_input("Owner name", value="Jordan")
if st.button("Create / Update Owner"):
    if st.session_state.owner is None:
        st.session_state.owner = pawpal_system.Owner(owner_name)
    else:
        st.session_state.owner.setName(owner_name)


if "pets" not in st.session_state:
    st.session_state.pets = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "schedule" not in st.session_state or not isinstance(st.session_state.schedule, pawpal_system.Schedule):
    st.session_state.schedule = None

if "owner" in st.session_state and isinstance(st.session_state.owner, pawpal_system.Owner):
    # already exists
    owner = st.session_state.owner
else:
    st.session_state.owner = None


if st.session_state.owner is not None:
    st.markdown("#### Availability")
    st.caption("Add free time blocks so the scheduler knows when the owner is available each day.")
    avail_col1, avail_col2, avail_col3 = st.columns(3)
    with avail_col1:
        avail_day = st.selectbox("Day", [d.value for d in pawpal_system.DayOfWeek], key="avail_day")
    with avail_col2:
        avail_start = st.time_input("Start", value=time(9, 0), key="avail_start")
    with avail_col3:
        avail_end = st.time_input("End", value=time(17, 0), key="avail_end")
    if st.button("Add availability block"):
        try:
            st.session_state.owner.addAvailability(
                pawpal_system.DayOfWeek(avail_day),
                pawpal_system.TimeRange(avail_start, avail_end),
            )
            st.success(f"Added {avail_start.strftime('%H:%M')}\u2013{avail_end.strftime('%H:%M')} on {avail_day}.")
        except ValueError as err:
            st.error(str(err))
    avail_summary = [
        {"Day": day.value, "Window": str(tr)}
        for day in pawpal_system.DayOfWeek
        for tr in st.session_state.owner.availability.get(day, [])
    ]
    if avail_summary:
        st.dataframe(avail_summary, use_container_width=True)
    else:
        st.info("No availability set yet. Add time blocks so tasks can be scheduled.")

st.markdown("### Pets")
st.caption("Create or update pets and their needs.")

st.markdown("### Pets")
st.caption("Create or update pets details.")
pet_name_input = st.text_input("Pet name", value="Mochi")

pet_col1, pet_col2, pet_col3 = st.columns(3)
with pet_col1:
    food_pref_input = st.text_input("Food preferences (comma-separated)", value="")
with pet_col2:
    avg_daily_walking_time = st.number_input("Avg daily walking time", min_value=0, max_value=600, value=0, step=1)
with pet_col3:
    eating_times_per_day = st.number_input("Eating times per day", min_value=0, max_value=20, value=0, step=1)

pet_col4, pet_col5 = st.columns(2)
with pet_col4:
    grooming_times_per_day = st.number_input("Grooming times per day", min_value=0, max_value=20, value=0, step=1)
with pet_col5:
    grooming_frequency = st.selectbox(
        "Grooming frequency",
        ["none"] + [f.value for f in pawpal_system.FrequencyType],
        index=0,
    )

grooming_days_per_week = 0
grooming_custom_days = []
if grooming_frequency == pawpal_system.FrequencyType.NUMBER_OF_DAYS.value:
    grooming_days_per_week = st.number_input("Grooming days per week", min_value=1, max_value=7, value=1, step=1)
elif grooming_frequency == pawpal_system.FrequencyType.CUSTOM_DAYS.value:
    grooming_custom_days = st.multiselect(
        "Grooming custom days",
        [d.value for d in pawpal_system.DayOfWeek],
        default=[],
    )

pet_col6, pet_col7 = st.columns(2)
with pet_col6:
    enrichment_frequency = st.selectbox(
        "Enrichment frequency",
        ["none"] + [f.value for f in pawpal_system.FrequencyType],
        index=0,
    )
with pet_col7:
    st.write("")

enrichment_days_per_week = 0
enrichment_custom_days = []
if enrichment_frequency == pawpal_system.FrequencyType.NUMBER_OF_DAYS.value:
    enrichment_days_per_week = st.number_input("Enrichment days per week", min_value=1, max_value=7, value=1, step=1)
elif enrichment_frequency == pawpal_system.FrequencyType.CUSTOM_DAYS.value:
    enrichment_custom_days = st.multiselect(
        "Enrichment custom days",
        [d.value for d in pawpal_system.DayOfWeek],
        default=[],
    )

if st.button("Create / Update Pet"):
    pet_obj = next(
        (
            p
            for p in st.session_state.pets
            if isinstance(p, pawpal_system.Pet) and p.name == pet_name_input
        ),
        None,
    )
    try:
        if pet_obj is None:
            pet_obj = pawpal_system.Pet(pet_name_input)
            st.session_state.pets.append(pet_obj)
        else:
            pet_obj.setName(pet_name_input)

        pet_obj.food_pref = []
        parsed_foods = [item.strip() for item in food_pref_input.split(",") if item.strip()]
        if parsed_foods:
            pet_obj.addFoods(parsed_foods)

        pet_obj.setAvgWalkingTime(int(avg_daily_walking_time))
        pet_obj.setDailyEatingTimes(int(eating_times_per_day))
        pet_obj.setDailyGroomingTimes(int(grooming_times_per_day))

        pet_obj.groomingFrequencyType = None
        pet_obj.groomingCustomDays = []
        pet_obj.groomingDaysPerWeek = 0
        if grooming_frequency != "none":
            pet_obj.setGroomingFrequency(
                pawpal_system.FrequencyType(grooming_frequency),
                [pawpal_system.DayOfWeek(day) for day in grooming_custom_days],
                int(grooming_days_per_week),
            )

        pet_obj.enrichmentFrequencyType = None
        pet_obj.enrichmentCustomDays = []
        pet_obj.enrichmentDaysPerWeek = 0
        if enrichment_frequency != "none":
            pet_obj.setEnrichmentFrequency(
                pawpal_system.FrequencyType(enrichment_frequency),
                [pawpal_system.DayOfWeek(day) for day in enrichment_custom_days],
                int(enrichment_days_per_week),
            )
    except (TypeError, ValueError) as err:
        st.error(str(err))

existing_pet_names = [
    p.name for p in st.session_state.pets if isinstance(p, pawpal_system.Pet)
]
selected_pet_names = st.multiselect(
    "Select existing pets for task",
    existing_pet_names,
    default=[],
    disabled=len(existing_pet_names) == 0,
)

st.markdown("### Tasks")
st.caption("Add all the tasks you must complete. These should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    priority = st.number_input("Priority (1 = highest)", min_value=1, max_value=99, value=1, step=1)
with col2:
    category = st.selectbox("Category", [c.value for c in pawpal_system.TaskCategory], index=0)
with col3:
    routine_task = st.checkbox("Routine task", value=True)

if not routine_task:
    col4, col5, col6 = st.columns(3)
    with col4:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col5:
        frequency_type = st.selectbox("Frequency", [f.value for f in pawpal_system.FrequencyType], index=0)
    with col6:
        times_per_day = st.number_input("Times per day", min_value=0, max_value=10, value=1, step=1)
else:
    duration = 30
    frequency_type = None
    times_per_day = 0

completed = st.checkbox("Completed", value=False)

days_per_week = 0
custom_days = []
if not routine_task:
    if frequency_type == pawpal_system.FrequencyType.NUMBER_OF_DAYS.value:
        days_per_week = st.number_input("Days per week", min_value=1, max_value=7, value=1, step=1)
    elif frequency_type == pawpal_system.FrequencyType.CUSTOM_DAYS.value:
        custom_days = st.multiselect(
            "Custom days",
            [d.value for d in pawpal_system.DayOfWeek],
            default=[],
        )

if st.button("Add task"):
    pet_objects = [
        p
        for p in st.session_state.pets
        if isinstance(p, pawpal_system.Pet) and p.name in selected_pet_names
    ]
    if not pet_objects:
        st.warning("Add pet(s) first, then select one or more pets before adding a task.")
    else:
        st.session_state.tasks.append(
            {
                "containedPets": pet_objects,
                "priority": int(priority),
                "category": pawpal_system.TaskCategory(category),
                "maxDurationMinutes": int(duration),
                "routineTask": routine_task,
                "frequencyType": (
                    None
                    if frequency_type is None
                    else pawpal_system.FrequencyType(frequency_type)
                ),
                "customDays": [pawpal_system.DayOfWeek(day) for day in custom_days],
                "daysPerWeek": int(days_per_week),
                "timesPerDay": int(times_per_day),
                "completed": completed,
            }
        )

if st.session_state.tasks:
    _preview_tasks = [
        pawpal_system.Task(
            containedPets=td["containedPets"],
            priority=td["priority"],
            category=td["category"],
            maxDurationMinutes=td["maxDurationMinutes"],
            routineTask=td["routineTask"],
            frequencyType=td["frequencyType"],
            customDays=td["customDays"],
            daysPerWeek=td["daysPerWeek"],
            timesPerDay=td["timesPerDay"],
            completed=td["completed"],
        )
        for td in st.session_state.tasks
    ]
    _preview_sched = pawpal_system.Schedule()
    _preview_sched.loadTasks(_preview_tasks)
    task_rows = [
        {
            "Priority": t.priority,
            "Category": t.category.value,
            "Pets": ", ".join(p.name for p in t.containedPets),
            "Duration (min)": t.maxDurationMinutes,
            "Frequency": (
                t.frequencyType.value if t.frequencyType else ("routine (daily)" if t.routineTask else "\u2014")
            ),
            "Completed": "\u2713" if t.completed else "",
        }
        for t in _preview_sched.getTasksSortedByPriority()
    ]
    st.write("Current tasks (sorted by priority):")
    st.dataframe(task_rows, use_container_width=True)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a weekly plan based on owner availability, task priority, and recurrence.")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.error("Please create an owner before generating a schedule.")
    elif not st.session_state.tasks:
        st.warning("No tasks to schedule. Add at least one task first.")
    else:
        task_objects = [
            pawpal_system.Task(
                containedPets=td["containedPets"],
                priority=td["priority"],
                category=td["category"],
                maxDurationMinutes=td["maxDurationMinutes"],
                routineTask=td["routineTask"],
                frequencyType=td["frequencyType"],
                customDays=td["customDays"],
                daysPerWeek=td["daysPerWeek"],
                timesPerDay=td["timesPerDay"],
                completed=td["completed"],
            )
            for td in st.session_state.tasks
        ]
        schedule = pawpal_system.Schedule()
        schedule.setOwner(st.session_state.owner)
        for p in st.session_state.pets:
            if isinstance(p, pawpal_system.Pet):
                schedule.addPet(p)
        schedule.loadTasks(task_objects)

        try:
            explanation = schedule.generateSchedule()
        except ValueError as err:
            st.error(str(err))
        else:
            st.session_state.schedule = schedule
            conflict_lines = [
                ln for ln in explanation.splitlines() if ln.strip().lower().startswith("could not")
            ]
            if not conflict_lines:
                st.success(explanation)
            else:
                placed = len(schedule.generatedScheduledTasks)
                st.warning(
                    f"{placed} occurrence(s) scheduled. Some tasks could not be placed due to insufficient availability:"
                )
                for note in conflict_lines:
                    st.warning(f"\u26a0 {note}")
            if not schedule.generatedScheduledTasks:
                st.error(
                    "No tasks could be scheduled. Make sure the owner has availability set for the required days."
                )

# Always render the schedule table if one exists, so completion persists across reruns
if st.session_state.schedule is not None and st.session_state.schedule.generatedScheduledTasks:
    st.markdown("#### Weekly Schedule")
    st.caption("Check \u2713 Done to mark a task occurrence as completed.")

    entries = st.session_state.schedule.generatedScheduledTasks
    schedule_data = [
        {
            "Done": entry.containedTask.completed,
            "Day": entry.day.value.capitalize(),
            "Time": str(entry.timeRange),
            "Category": entry.containedTask.category.value,
            "Pets": ", ".join(p.name for p in entry.containedTask.containedPets),
            "Duration (min)": entry.containedTask.maxDurationMinutes,
            "Priority": entry.containedTask.priority,
        }
        for entry in entries
    ]

    edited = st.data_editor(
        schedule_data,
        column_config={
            "Done": st.column_config.CheckboxColumn(
                "Done",
                default=False,
                help="Check to mark this occurrence as completed",
            ),
        },
        disabled=["Day", "Time", "Category", "Pets", "Duration (min)", "Priority"],
        use_container_width=True,
        hide_index=True,
        key="schedule_editor",
    )

    # Sync checkbox state back to the persistent task objects in session state
    for i, row in enumerate(edited):
        if row["Done"]:
            entries[i].containedTask.mark_complete()

    incomplete = st.session_state.schedule.filterTasks(completion_status=False)
    if incomplete:
        st.markdown("#### Incomplete Tasks")
        incomplete_rows = [
            {
                "Priority": t.priority,
                "Category": t.category.value,
                "Pets": ", ".join(p.name for p in t.containedPets),
            }
            for t in incomplete
        ]
        st.dataframe(incomplete_rows, use_container_width=True)
    else:
        st.success("All scheduled tasks are marked complete! \U0001f389")
