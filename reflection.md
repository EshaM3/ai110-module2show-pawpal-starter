# PawPal+ Project Reflection

## 1. System Design

3 core user actions:
- Add pet and owner information (availability and needs)
- Add, edit, and remove daily pet care tasks with time length, priority, and category elements
- Generate a daily schedule/plan that allots tasks to different days and hours based on given constraints and current tasks' elements

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial UML design includes these classes: Owner, Pet, Task, and Schedule. The Owner will have their name and time availability blocks per day in a week. The Pet will only have their name to keep track of each pet. The Task will have a category (walking, feeding, etc.), maximum time duration, frequency, priority, and time ranges throughout the week. The last field cannot be seen or filled out by the user. The Schedule will populate the last field of the Tasks based on all other fields. It will have that list of Tasks as well as an explanation string for how and why the schedule was populated in such a way.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, it changed quite a bit. First of all, my pets just had a name attribute at first.I initially had others but removed it before generating the UML. AI reminded me that these attributes were important as each pet will have their own independent scheduled needs for meds, grooming time, etc. So I added those frequency attributes in the Pet class. This took off some load from the Task class which now only handles adding said tasks and their priorities. If you want to add non-routine tasks, that is also possible in the Task class.

There are two new Dataclasses: Medication and ScheduledTask.
Medication has its own days and times to take them. ScheduledTask is a task with updated times, assigned, owners, etc. when a schedule is generated.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Priority, task time duration, owner availability, frequency preferences for each pet, and frequency of non-routine tasks. The owner availability takes the highest precedence since the owner can't do anything outside of those time blocks. Next, priority is directly chosen by user, so this is a very important determinant of tradeoffs. After that, time durations and frequencies will fill based on the layout constructed by the first two constraints.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The time slots are first come first served based on priority. So if a bunch of smaller, low-priority tasks could have fit into one contiguous time range, that might not be possible if the highest priority task found the big time slot first and takes up the whole block. This is reasonable because the user decides on that priority, thereby forgoing any number of the lower ones if necessary.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used it throughout all parts of the process, but primarily for cleaning up, implementation, and testing.
I especially appreciate the shorthand tools like /doc and /test to generate doc notes and tests.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Through manual testing (seeing the app itself), refinement prompts, and reading through the code myself, I identified inconsistencies, errors, and bloated logic.

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Sorting correctness, recurrence logic, and conflict detection were the primary three areas to test for the most complex algorithms in the application (all mainly built for the schedule class).

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am quite confident after testing the app out myself. But I would definitely want to play around more with adding duplicate tasks with varying pets (one containing 1 pet, another containing both). Also with overlapping availability time blocks.

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The ability for each pet to have their own set needs (like meds) that don't need to constantly be re-entered with each new task that will include them.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The ordering and display of the schedule could be much more readable. Same with the explanations for the schedule being a bit more than just alerts of exclusions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned a lot about how many iterations it can take for a robust system design. And how mermaid diagrams can help a lot with this.