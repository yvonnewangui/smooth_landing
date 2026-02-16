from crewai import Task
from agents.core_agents import (
    destination_researcher,
    accommodation_planner,
    activities_planner,
    transport_planner,
    itinerary_coordinator,
    trip_verifier,
    local_insider,
)


def build_profile_task(traveller_type: str, raw_preferences: str):
    """
    traveller_type: 'solo female', 'solo', 'family', etc.
    raw_preferences: free text from user, e.g. 'hate hostels, love food tours, mid-range budget'
    """
    description = f"Profile: {traveller_type}. Preferences: {raw_preferences}"

    return Task(
        description=description,
        agent=destination_researcher,
        expected_output="Profile bullet list."
    )


def build_core_tasks(
    destination: str,
    budget: float,
    days: int,
    interests: str,
    traveller_type: str,
    raw_preferences: str,
    start_date,
    will_fly: bool = False,
):
    # 1) Profile
    profile_task = build_profile_task(traveller_type, raw_preferences)

    # 2) Research (uses profile)
    fly_note = "(Will fly in/out)" if will_fly else ""
    research_task = Task(
        description=(
            f"Research {destination} {fly_note}: safety, neighborhoods, costs, transport, weather."
        ),
        agent=destination_researcher,
        context=[profile_task],
        expected_output="Brief: safety notes, areas, costs, transport options."
    )

    # 3) Accommodation
    budget_for_stay = budget * 0.35
    accommodation_task = Task(
        description=(
            f"Suggest 3-5 stays in {destination} (~${budget_for_stay/days:.0f}/night). Safe, walkable, good transport. All costs in USD."
        ),
        agent=accommodation_planner,
        context=[research_task],
        expected_output="3-5 options: area, rate in USD, brief reason."
    )

    # 4) Activities (day-by-day)
    activities_task = Task(
        description=(
            f"Plan {days} days in {destination} around {interests}. 2-3 activities/day, cluster nearby, balance active/light."
        ),
        agent=activities_planner,
        context=[research_task],
        expected_output="Day-by-day activities with timing and energy level."
    )

    # 5) Transport
    transport_note = "(airport transfers + " if will_fly else "("
    transport_task = Task(
        description=(
            f"Transport plan for {destination} {days}d: accommodations, area-to-area, evening/late-night options (no long walks after 22:00). All costs in USD."
        ),
        agent=transport_planner,
        context=[research_task],
        expected_output="Transport modes, costs in USD, safety notes, late-night options."
    )

    # 6) Coordination (whole-trip shaping)
    coordination_task = Task(
        description=(
            "Organize into Day 1, Day 2... format. Include: stay, activities, transport, times, safety. Cluster nearby activities. Keep realistic pace (no >12hr days, no late returns). All costs in USD. Output markdown only."
        ),
        agent=itinerary_coordinator,
        context=[research_task, accommodation_task, activities_task, transport_task],
        expected_output="Day-by-day itinerary in markdown. Each day: stay | activities | transport | times | safety notes. All costs in USD."
    )

    # 7) Verification (scores + light edits)
    verification_task = Task(
        description=(
            f"Verify itinerary: realistic pacing? Safe areas/no risky patterns? Budget-aligned (${budget} USD total)? Add scores (Feasibility, Safety, Budget, Confidence). All costs in USD. Output markdown."
        ),
        agent=trip_verifier,
        context=[coordination_task],
        expected_output="Verified itinerary, scores (0-10), key risks. All costs in USD. Markdown text."
    )

    # 8) Local insights & final client format
    local_insights_task = Task(
        description=(
            f"Polish itinerary for {destination} ({days}d, ${budget} USD). Add: trip snapshot, safety tips, budget breakdown in USD, local hacks. All costs must be in USD. Markdown only."
        ),
        agent=local_insider,
        context=[verification_task],
        expected_output="Final polished itinerary: snapshot, safety, daily plan, budget breakdown in USD, tips. Markdown."
    )

    return [
        profile_task,
        research_task,
        accommodation_task,
        activities_task,
        transport_task,
        coordination_task,
        verification_task,
        local_insights_task,
    ]