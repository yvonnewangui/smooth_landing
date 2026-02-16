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
    description = (
        f"Traveller: {traveller_type}. Preferences: {raw_preferences}\n\n"
        "Create 4–5 bullet profile covering:\n"
        "- Budget/style\n"
        "- Accommodation preference\n"
        "- Activity interests\n"
        "- Pace (relaxed/full)\n"
        "- Safety sensitivies"
    )

    return Task(
        description=description,
        agent=destination_researcher,
        expected_output="Short bullet list of traveller preferences."
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
    fly_note = "Note: traveller will fly in/out." if will_fly else ""
    research_task = Task(
        description=(
            f"Research {destination} ({days}d, ${budget}, {interests}). {fly_note}\n\n"
            "Cover:\n"
            "1. Safety: current hazards, unsafe neighborhoods/times\n"
            "2. Neighborhoods: safe/convenient areas\n"
            "3. Daily costs: food, activities, local transport\n"
            "4. Transport: taxis, apps, night safety\n"
            "5. Weather & season"
        ),
        agent=destination_researcher,
        context=[profile_task],
        expected_output="Bullet brief: safety, areas, costs, transport, seasonal notes."
    )

    # 3) Accommodation
    budget_for_stay = budget * 0.35  # ~35% for accommodation, leaving 65% for food/activities/transport
    accommodation_task = Task(
        description=(
            f"Propose 3–5 options in {destination} (~${budget_for_stay/days:.0f}/night, {days} nights).\n\n"
            "Priorities:\n"
            "- Safe, walkable evening areas\n"
            "- Match traveller style (budget/mid/upscale)\n"
            "- Good transport links\n"
            "- Flag 24/7 reception, female-friendly reviews if relevant"
        ),
        agent=accommodation_planner,
        context=[research_task],
        expected_output="3–5: area, nightly rate, why it fits."
    )

    # 4) Activities (day-by-day)
    activities_task = Task(
        description=(
            f"Create {days}-day plan for {destination} around {interests}.\n\n"
            "Rules:\n"
            "- Max 2–3 major activities/day\n"
            "- Cluster nearby areas (reduce transit)\n"
            "- Balance active + light days\n"
            "- Include social options for solo travellers"
        ),
        agent=activities_planner,
        context=[research_task],
        expected_output="Day-by-day: morning/afternoon/evening + energy/safety notes per day."
    )

    # 5) Transport
    transport_note = "Cover airport arrival/departure + " if will_fly else ""
    transport_task = Task(
        description=(
            f"Design transport plan for {days} days in {destination}. {transport_note}\n\n"
            "Cover:\n"
            "- Accommodation transfers\n"
            "- Area-to-area connections\n"
            "- Evening/late-night options (no long walks after 22:00; use apps/taxis)\n\n"
            "Output: modes, costs, safety notes, late-night alternatives."
        ),
        agent=transport_planner,
        context=[research_task],
        expected_output="Transport modes, costs, safety guidance, late-night alternatives."
    )

    # 6) Coordination (whole-trip shaping)
    coordination_task = Task(
        description=(
            "Synthesize all inputs into a complete day-by-day itinerary.\n\n"
            "Guidelines:\n"
            "- Cluster activities by location (minimize back-and-forth)\n"
            "- Prioritize safety (safe areas for evenings, simple night logistics)\n"
            "- Maintain realistic pace (no >12hr days, no 22:00+ returns)\n"
            "- Align with budget and preferences\n\n"
            "Output as a formatted day-by-day plan. If needed, reorganize activities for better flow. "
            "Include accommodations, activities, transport, and timing for each day."
        ),
        agent=itinerary_coordinator,
        context=[research_task, accommodation_task, activities_task, transport_task],
        expected_output="Formatted day-by-day itinerary with: Day 1-N, stay location, activities, transport, times, safety notes."
    )

    # 7) Verification (scores + light edits)
    verification_task = Task(
        description=(
            f"Verify {days}-day itinerary for {traveller_type}.\n\n"
            "Checklist:\n"
            "- Realistic pacing, not exhausting?\n"
            "- Safe areas, no risky late-night patterns?\n"
            "- Budget-aligned?\n\n"
            "Output:\n"
            "### VERIFIED ITINERARY\n"
            "[Adjusted itinerary]\n\n"
            "### SCORES: Feasibility | Safety | Budget | Confidence (0–10, 0–10, 0–10, 0–100)\n\n"
            "### RISKS: [Key concerns]"
        ),
        agent=trip_verifier,
        context=[coordination_task],
        expected_output="Adjusted itinerary + feasibility/safety/budget/confidence scores + risk notes."
    )

    # 8) Local insights & final client format
    local_insights_task = Task(
        description=(
            f"Format verified itinerary for {destination} ({days}d, ${budget}) as client-ready plan.\n\n"
            "## TRIP SNAPSHOT\n"
            "Destination | Days | Budget | Style\n\n"
            "## SAFETY & HABITS\n"
            "[Safety overview + 4–6 practical tips]\n\n"
            "## DAILY ITINERARY\n"
            "Day X – [Label]: morning/afternoon/evening activities\n\n"
            "## BUDGET\n"
            "Accommodation | Food | Activities | Transport | Total\n\n"
            "## LOCAL TIPS\n"
            "[Transport hacks, best times, quiet spots, apps]"
        ),
        agent=local_insider,
        context=[verification_task],
        expected_output="Polished client-ready itinerary with snapshot, safety, daily plan, budget, tips."
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