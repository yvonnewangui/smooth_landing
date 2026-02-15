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
        "Create a concise traveller profile summary based only on the details below.\n\n"
        f"Traveller type: {traveller_type}\n"
        f"New preferences: {raw_preferences}\n\n"
        "Write 3–6 bullet points covering likely stable preferences:\n"
        "- Budget level\n"
        "- Accommodation style\n"
        "- Preferred activities\n"
        "- Pace (relaxed / full)\n"
        "- Safety sensitivities (e.g. dislikes late nights, crowded bars)\n\n"
        "OUTPUT FORMAT:\n"
        "### TRAVELLER PROFILE SUMMARY\n"
        "- [Preference 1]\n"
        "- [Preference 2]\n"
        "- [Preference 3]\n"
        "(Keep it short and general, not tied to one specific day.)\n"
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
):
    # 1) Profile
    profile_task = build_profile_task(traveller_type, raw_preferences)

    # 2) Research (uses profile)
    research_task = Task(
        description=(
            "Using the traveller profile and trip details, research the destination.\n\n"
            f"Trip: {days}-day visit to {destination} with total budget about ${budget}.\n"
            f"Key interests: {interests}.\n"
            "Respect stable preferences from the traveller profile (budget, pace, accommodation type,\n"
            "safety sensitivities, solo-travel concerns).\n\n"
            "Use the web_search tool whenever you need up-to-date information such as weather,\n"
            "current safety notes, or recent local changes. Call tools first, then write your answer\n"
            "based on the tool results.\n\n"
            "OUTPUT: A brief research outline (bullet points) including:\n"
            "- Key neighbourhoods to stay / visit\n"
            "- Rough daily cost level (budget / mid / high)\n"
            "- Major safety points and areas to be cautious about\n"
            "- Main local transport options\n"
            "- Important seasonal/weather notes\n"
        ),
        agent=destination_researcher,
        context=[profile_task],
        expected_output="Short research brief covering areas, costs, safety, transport, season."
    )

    # 3) Accommodation
    accommodation_task = Task(
        description=(
            f"Propose 3–5 accommodation options in {destination} using the traveller profile and research brief.\n\n"
            "Follow these principles:\n"
            "- Match the traveller's budget level and accommodation style preferences.\n"
            "- Prefer safe, convenient areas (easy to reach, okay to walk early evening).\n"
            f"- As a rough guide, keep total accommodation within ~40–50% of the budget (${budget}).\n"
            "- Call out if a place is especially good for solo travellers (e.g. 24/7 reception, strong reviews).\n\n"
            "If you need current hotel area information, you may briefly use the web_search tool.\n"
            "Call the tool first, then update your list based on what you found.\n\n"
            "OUTPUT:\n"
            "- 3–5 bullets, each with: name/area, approx nightly price, why it fits this traveller.\n"
        ),
        agent=accommodation_planner,
        context=[research_task],
        expected_output="3–5 accommodation options with area, price band, and fit."
    )

    # 4) Activities (day-by-day)
    activities_task = Task(
        description=(
            f"Create a realistic {days}-day activity plan in {destination} that matches the research brief,\n"
            f"traveller profile and interests: {interests}.\n\n"
            "Rules (keep them lightweight but applied):\n"
            "- Each day has Morning / Afternoon / Evening blocks.\n"
            "- Max 2–3 major activities per day; balance with lighter stops (parks, cafes, viewpoints).\n"
            "- Cluster each day around 1–2 nearby areas to reduce long cross-city trips.\n"
            "- Consider season/weather: avoid planning long exposed outdoor blocks on likely extreme days.\n"
            "- Make it solo-friendly: include at least a couple of social/group options over the whole stay.\n\n"
            "Use the web_search tool only when needed for up-to-date opening info or weather-sensitive choices.\n"
            "Call tools first, then adjust your plan based on the results.\n\n"
            "OUTPUT (for each day):\n"
            "Day X:\n"
            "- Morning: [activities + area]\n"
            "- Afternoon: [activities + area]\n"
            "- Evening: [activities + area]\n"
            "- Notes: [energy level, flexibility, any brief safety/comfort remark]\n"
        ),
        agent=activities_planner,
        context=[research_task],
        expected_output="Day-by-day outline with short notes on pace and practicality."
    )

    # 5) Transport
    transport_task = Task(
        description=(
            "Design a simple, safe transport plan for the whole trip.\n\n"
            f"Cover this {days}-day stay in {destination} with budget about ${budget}.\n"
            "Focus on:\n"
            "- Airport/station ↔ accommodation transfers.\n"
            "- Getting between the main areas used in the activity plan.\n"
            "- Any day trips or evening returns that might feel risky.\n\n"
            "Guidelines:\n"
            "- Prefer clear, easy-to-follow routes over complex chains of buses/transfers.\n"
            "- Avoid recommending long unfamiliar walks or multiple changes after ~22:00; suggest taxis/ride-hailing instead.\n"
            "- Give rough cost ranges for the main segments and a trip-level transport estimate.\n\n"
            "When you need current options or typical fares (e.g. airport → city), use the web_search tool with\n"
            "a short query, then incorporate the results into your plan.\n\n"
            "OUTPUT:\n"
            "- Airport/station → accommodation: modes + approx cost + brief note.\n"
            "- Typical daily movement patterns: main modes and when to use them.\n"
            "- Any specific cautions and safer alternatives.\n"
        ),
        agent=transport_planner,
        context=[research_task],
        expected_output="Simple whole-trip transport plan with rough costs and cautions."
    )

    # 6) Coordination (whole-trip shaping)
    coordination_task = Task(
        description=(
            "Combine research, accommodation, activities and transport into one coherent itinerary.\n\n"
            "You may reshuffle days or swap blocks if it clearly improves:\n"
            "- Location clustering (less back-and-forth across the city).\n"
            "- Safety (busy areas in evenings, simpler late-night moves).\n"
            "- Pace (no obviously overloaded days).\n\n"
            "Check for:\n"
            "- Very long days (over ~10–12 hours of activities + transit).\n"
            "- Awkward late-night returns after 22:00.\n"
            "- Obvious clashes between profile preferences and the plan.\n\n"
            "OUTPUT: One consolidated day-by-day itinerary with stays, activities and key movements.\n"
        ),
        agent=itinerary_coordinator,
        context=[research_task, accommodation_task, activities_task, transport_task],
        expected_output="Consolidated itinerary for the whole stay with days, areas, and key moves."
    )

    # 7) Verification (scores + light edits)
    verification_task = Task(
        description=(
            f"Review the consolidated {days}-day itinerary for {destination} against budget, feasibility and safety,\n"
            f"especially for a {traveller_type} traveller with the given preferences.\n\n"
            "Checklist:\n"
            "- Timeline: days feel realistic (not clearly overstuffed).\n"
            "- Transit: no excessive backtracking or complex late-night journeys.\n"
            "- Safety: nothing obviously worrying for a solo traveller at night.\n"
            "- Budget: rough split across accommodation, food, activities, transport stays near the target.\n\n"
            "If you spot clear problems, adjust the itinerary briefly before scoring.\n\n"
            "OUTPUT STRUCTURE:\n"
            "### VERIFIED ITINERARY\n"
            "[Improved final itinerary text]\n\n"
            "### SCORES\n"
            "- Feasibility (0–10): X\n"
            "- Safety (0–10): Y\n"
            "- Budget fit (0–10): Z\n"
            "- Overall confidence (0–100): C\n\n"
            "### NOTES\n"
            "[2–5 bullets: key risks, compromises, or suggestions.]\n"
        ),
        agent=trip_verifier,
        context=[coordination_task],
        expected_output="Verified itinerary with short scores and notes."
    )

    # 8) Local insights & final client format
    local_insights_task = Task(
        description=(
            "Turn the verified itinerary into a clear, client-ready document with local tips.\n\n"
            f"Trip dates: starting {start_date} for {days} days.\n"
            "Follow this structure:\n"
            "## TRIP SUMMARY\n"
            f"- Destination: {destination}\n"
            f"- Duration: {days} days\n"
            f"- Approx. budget: ${budget}\n"
            f"- Traveller type: {traveller_type}\n"
            "- Style: [brief label you infer, e.g. balanced / foodie / culture-heavy]\n\n"
            "## SAFETY OVERVIEW\n"
            "[2–4 sentences on general safety and solo-travel awareness: safer areas, typical scams,\n"
            "simple night-time advice.]\n\n"
            "## DAILY ITINERARY\n"
            "For each day:\n"
            "- Day X – [Short label]\n"
            "  - Morning: [activities + area]\n"
            "  - Afternoon: [activities + area]\n"
            "  - Evening: [activities + area]\n"
            "  - Notes: [1–2 lines on walking time, safety, or flexibility]\n\n"
            "## BUDGET SNAPSHOT (ROUGH)\n"
            "- Accommodation (total): ~$A\n"
            "- Food (total): ~$B\n"
            "- Activities (total): ~$C\n"
            "- Transport (total): ~$D\n"
            f"- Estimated total: ~$T vs target ${budget}\n"
            "- Comment: [Under / near / over target with one line of context]\n\n"
            "## SOLO-SMART TIPS (USEFUL FOR EVERYONE)\n"
            "[4–8 bullets: practical habits and small behaviours that improve comfort and safety.]\n"
        ),
        agent=local_insider,
        context=[verification_task],
        expected_output="Polished client-ready itinerary following the structure above."
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