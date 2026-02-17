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
            f"Research {destination} {fly_note}: safety, neighborhoods, costs, transport, weather. "
            "Use the 'Search the internet' tool for web searches. "
            "Do NOT call brave_search or any tool not in your tools list."
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
            "Organize the trip into a clear day-by-day plan. Cluster nearby activities. Keep realistic pace (no >12hr days). All costs in USD. "
            "Output as SEPARATE MARKDOWN TABLES for each day. Example:\n\n"
            "## Day 1\n"
            "| Time | Activity | Location | Transport | Notes |\n"
            "|------|----------|----------|-----------|-------|\n"
            "| 9:00 AM | Visit Museum | Downtown | Taxi | History |\n"
            "| 12:00 PM | Lunch | Old Town | Walk | Local food |\n"
            "| 3:00 PM | Beach | Coast | Uber | Relax |\n\n"
            "## Day 2\n"
            "| Time | Activity | Location | Transport | Notes |\n"
            "|------|----------|----------|-----------|-------|\n"
            "| 10:00 AM | Market | City center | Metro | Shopping |\n\n"
            "Create one heading (## Day X) and one table per day. Every row must have an activity."
        ),
        agent=itinerary_coordinator,
        context=[research_task, accommodation_task, activities_task, transport_task],
        expected_output="Separate markdown table for each day with heading. Columns: Time | Activity | Location | Transport | Notes."
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
            f"Polish itinerary for {destination} ({days}d, ${budget} USD). "
            "Add: trip snapshot at top, safety tips, budget breakdown in USD, local hacks. "
            "Keep daily plan as SEPARATE TABLES per day (## Day X heading, then table with Time | Activity | Location | Transport | Notes). "
            "All costs in USD."
        ),
        agent=local_insider,
        context=[verification_task],
        expected_output="Final itinerary with: snapshot, safety, separate table per day, budget, tips."
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