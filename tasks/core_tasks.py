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
            f"Research {destination} {fly_note}: safety, neighborhoods, costs, transport. "
            f"\n\n"
            f"CRITICAL - MUST DO ALL THREE PARTS:\n"
            f"1) GENERAL INFO: safety notes, neighborhoods, costs, local transport options.\n"
            f"2) WEATHER (REQUIRED): You MUST search the internet for the SPECIFIC travel dates ({start_date} for {days} days). "
            f"Search for: current weather forecast for {destination}, typical weather during those dates, temperature range (min/max), "
            f"rainfall/rainy season info, humidity levels, air quality.\n"
            f"3) PACKING ADVICE (REQUIRED): Based on the weather found above, provide specific packing recommendations (clothing, gear, etc.).\n"
            f"\n"
            f"Use the 'Search the internet' tool to find weather data. This is NOT optional. "
            f"Do NOT rely on general knowledge - MUST search for actual weather for {start_date}.\n"
            f"Do NOT call brave_search or any tool not in your tools list."
        ),
        agent=destination_researcher,
        context=[profile_task],
        expected_output=(
            f"MUST INCLUDE:\n"
            f"1) Safety notes and travel tips\n"
            f"2) Neighbourhoods and areas to stay\n"
            f"3) Budget estimates (accommodation, food, transport)\n"
            f"4) WEATHER FORECAST for {start_date} ({days} days): temperature range, rain/humidity, season info\n"
            f"5) PACKING RECOMMENDATIONS based on the actual weather forecast\n"
            f"6) Additional safety precautions if needed for the weather conditions"
        )
    )

    # 3) Accommodation
    budget_for_stay = budget * 0.35
    per_day_stay = budget_for_stay / days
    accommodation_task = Task(
        description=(
            f"Suggest 3-5 hotel stays in {destination} (~${per_day_stay:.0f}/night MAX). "
            f"HOTELS ONLY: Do NOT suggest Airbnb, hostels, guesthouses, host homes, family stays, or other accommodations. "
            f"Focus exclusively on traditional hotels (3-5 star mid-range properties). "
            f"BUDGET-CONSCIOUS: Prioritize affordable mid-range hotel options only. "
            f"Avoid luxury/high-end chains. Must have safe location, walkable area, good transport access. "
            f"All costs in USD. MUST NOT exceed ${per_day_stay:.0f}/night for any hotel."
        ),
        agent=accommodation_planner,
        context=[research_task],
        expected_output="3-5 hotel options: hotel name, location/area, rate in USD (≤${per_day_stay:.0f}/night), brief reason. All mid-range hotels."
    )

    # 4) Activities (day-by-day)
    budget_for_activities = budget * 0.40
    per_day_activities = budget_for_activities / days
    activities_task = Task(
        description=(
            f"Plan {days} days in {destination} around {interests}, departing {start_date}. "
            f"Schedule activities based on the ACTUAL TRAVEL DATES ({start_date}, {days} days). "
            f"Consider weather/season—check research for weather forecast and adjust activity suggestions accordingly. "
            f"For outdoor activities, suggest indoor alternatives if rain is forecasted. "
            f"CRITICAL: Group activities by geographic proximity. Each day's activities must be close to each other to minimize travel time. "
            f"2-3 activities/day max, cluster in same neighborhood, balance active/light based on weather. Avoid backtracking across the city."
        ),
        agent=activities_planner,
        context=[research_task],
        expected_output="Day-by-day activities scheduled for {start_date} with timing, energy level, geographic clustering. Include indoor/outdoor options based on weather forecast."
    )

    # 5) Transport
    budget_for_transport = budget * 0.25
    per_day_transport = budget_for_transport / days
    transport_task = Task(
        description=(
            f"Transport plan for {destination} {days}d (budget ~${per_day_transport:.0f}/day): "
            f"accommodations, area-to-area, evening/late-night options (no long walks after 22:00). "
            f"BUDGET MODE: Suggest affordable transit (public transport, shared taxis, walking). Avoid expensive services. "
            f"All costs in USD. MUST stay within ~${per_day_transport:.0f}/day budget."
        ),
        agent=transport_planner,
        context=[research_task],
        expected_output="Transport modes, costs in USD (~${per_day_transport:.0f}/day), safety notes, late-night options. All budget-friendly."
    )

    # 6) Coordination (whole-trip shaping)
    coordination_task = Task(
        description=(
            f"Organize the trip into a clear day-by-day plan. BUDGET BREAKDOWN: Allow ~${per_day_stay:.0f}/night for accommodation, "
            f"~${per_day_activities:.0f}/day for activities+meals, ~${per_day_transport:.0f}/day for transport. Total budget: ${budget}. "
            f"STAY WITHIN THESE ALLOCATIONS—do not suggest expensive items. "
            f"PRIORITY: Group each day's activities by geographic zone—all activities in the same neighborhood/area per day. "
            f"Minimize travel between locations within each day. Route activities geographically (e.g., north → south) to avoid backtracking. "
            f"Keep realistic pace (no >12hr days). All costs in USD. "
            f"CRITICAL: Create activities for ALL {days} days. Do not leave any day empty or with just headings. "
            f"OUTPUT FORMAT - MUST USE EXACT MARKDOWN TABLE FORMAT:"
            f"\n\n## Day 1\n\n"
            f"| Time | Activity | Location | Transport | Cost (USD) | Comment |\n"
            f"| --- | --- | --- | --- | --- | --- |\n"
            f"| 9:00 AM | Visit National Museum | Downtown | Walking | $10 | Learn about local history |\n"
            f"| 11:00 AM | Coffee break | Downtown | Walking | $5 | Local café with wifi |\n"
            f"| 1:00 PM | Lunch at market | Downtown | Walking | $12 | Traditional food, busy area |\n\n"
            f"## Day 2\n\n"
            f"[Next table with same format]\n\n"
            f"REQUIREMENTS: Use pipes (|), include separator row (| --- |), add activities for every single day 1 through {days}."
            f"\nCOMMENT GUIDELINES: For each activity, add a helpful comment that includes:"
            f"\n- Brief activity description OR value (e.g., 'Scenic viewpoint', 'Local market, peak hours 8-11am', 'Highly rated, book ahead')"
            f"\n- Realistic experience level (e.g., 'Easy walk', 'Moderate climbing', 'Peaceful spot')"
            f"\n- Travel time to next activity if relevant"
            f"\nDO NOT write generic comments like 'Below budget' or 'Within allocation'—be specific about the activity."
        ),
        agent=itinerary_coordinator,
        context=[research_task, accommodation_task, activities_task, transport_task],
        expected_output=f"Complete markdown itinerary with activities for ALL {days} days. Each day must have: ## Day X heading, blank line, proper markdown table with pipes (|) and separator row (| --- |), then blank line before next day. Columns: Time | Activity | Location | Transport | Cost (USD) | Comment. All activities per day grouped in same geographic area. Total cost must fit in ${budget}. Comments must be descriptive about activity value/experience, NOT budget status. NO EMPTY DAYS - every day 1 through {days} must have activities."
    )

    # 7) Verification (scores + light edits)
    verification_task = Task(
        description=(
            f"Verify itinerary: realistic pacing? Safe areas/no risky patterns? Geographic clustering (all activities per day grouped by area)? "
            f"MOST IMPORTANT: Budget-aligned (${budget} USD total). "
            f"Per-day allocations: ~${per_day_stay:.0f}/night accommodation, ~${per_day_activities:.0f}/day activities+meals, ~${per_day_transport:.0f}/day transport. "
            f"Extract all costs. Check per-day breakdown stays within allocations. Sum total. Ensure total ≤ ${budget}. "
            f"If any day or total exceeds limits, flag ALL excessive items. Check day activities grouped geographically. "
            f"CRITICAL: Add scores (Feasibility, Safety, Budget Adherence, Per-day Fit, Geographic Flow) EXACTLY ONCE per day. NO duplicate metrics. "
            f"Consolidate all information - each metric reported only once. All costs in USD."
        ),
        agent=trip_verifier,
        context=[coordination_task],
        expected_output="Verified itinerary with consolidated per-day breakdown, allocation checks, total spent. Each day shows metrics (Geographic Flow, Feasibility, Safety, Budget Adherence, Per-day Fit) ONCE only. If over budget/allocation flag items. All costs in USD. Markdown. NO REDUNDANT INFORMATION."
    )

    # 8) Local insights & final client format
    local_insights_task = Task(
        description=(
            f"Polish itinerary for {destination} ({days}d from {start_date}, ${budget} USD HARD BUDGET). "
            f"BUDGET ALLOCATIONS: ~${per_day_stay:.0f}/night accommodation, ~${per_day_activities:.0f}/day activities+meals, ~${per_day_transport:.0f}/day transport. "
            f"CRITICAL 1: Ensure per-day costs stay within allocations AND total trip cost ≤ ${budget}. If over, cut/reduce activities or lodging. "
            f"CRITICAL 2: Verify each day's activities are grouped by geographic area—no backtracking across the city. "
            "Activities within the same day should be clustered (same neighborhood/zone). "
            f"CRITICAL 3: Include WEATHER SECTION showing forecast summary for travel dates ({start_date}, {days} days). "
            f"CRITICAL 4: Add PACKING LIST section with SPECIFIC recommendations based on weather forecast and destination {destination}. "
            f"Include temperature range, rain probability, humidity, and activity type. List items specific to {destination} weather conditions. "
            f"Example: 'Lightweight breathable clothing for {destination}s hot/humid climate', 'Waterproof bag for rainy season', NOT generic 'comfortable shoes'. "
            f"Add: trip snapshot at top showing travel dates, weather overview, budget breakdown, safety tips, per-day cost breakdown showing totals ≤ allocations, local hacks. "
            f"FORMATTING CRITICAL: Each major section should be followed by a BLANK LINE. Keep daily plan as SEPARATE TABLES per day:"
            f"\n- Use '## Day X' heading"
            f"\n- Add a BLANK LINE after the heading"
            f"\n- Then the markdown table with proper pipes (|) and separator row (| --- | --- | ... |)"
            f"\n- Add BLANK LINE after each table before the next day heading"
            f"\nFOR COMMENTS: Each row's comment should describe the activity (what to do, why it's worth it), experience level, or helpful logistics—NOT budget status. "
            f"Example good comments: 'Best local market in the area, peak hours 7-11am', 'Scenic viewpoint, easy 15min walk', 'Visit early to avoid crowds'. "
            f"Example BAD comments: 'Below budget', 'Within allocation', 'Affordable option'—these add no value. "
            f"All costs in USD. FINAL OUTPUT MUST NOT EXCEED ${budget} AND MUST STAY WITHIN PER-DAY ALLOCATIONS."
        ),
        agent=local_insider,
        context=[verification_task],
        expected_output=f"Final itinerary with: snapshot (travel dates, weather overview, per-day allocations), BLANK LINES between sections, weather forecast section, packing list with destination and weather-specific recommendations, safety, separate table per day preceded by ## Day X heading (activities clustered, with descriptive comments), cost breakdown (per-day ≤ allocations, total ≤ ${budget}), tips. Use proper markdown formatting with BLANK LINES between major sections and after each table. All costs in USD. Comments should be descriptive and helpful, NOT mention budget status."
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