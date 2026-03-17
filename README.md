# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Smarter Scheduling

PawPal+ now has a full backend scheduling engine with practical, real-world features. You can model owners, pets, medications, and tasks; validate inputs (names, durations, non-overlapping time windows); and schedule tasks by priority against owner availability across the week. The planner supports routine and frequency-based tasks (daily, weekly, custom days, or number of days), tracks completion status, and outputs readable HH:MM time blocks. On top of that, tasks can be sorted by priority and filtered by completion or pet name, with tests covering key behaviors like task completion, time formatting, sorting, and filtering. The Streamlit UI also supports creating/updating owners and pets, defining frequencies, adding tasks, and preparing data for schedule generation.

### Testing PawPal+

pytest was used to test the system's logic.
command used: python -m pytest

These tests check that task sorting stays correct by priority, recurring tasks run on the right days, and schedule conflicts are detected and reported when time is limited.

Based on test results in addition to apprehension of possible edge cases that I may have not gotten to, my Confidence Level in the system's reliability is 4.5 stars.



