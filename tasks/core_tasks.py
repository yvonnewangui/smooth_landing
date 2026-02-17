from crewai import Task
from agents.core_agents import (
    destination_researcher,
    accommodation_planner,
    activities_planner,
    transport_planner,
    itinerary_coordinator,
    trip_verifier,
    local_insider,
    visa_requirements_advisor,
    health_wellness_advisor,
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
    passport_country: str = None,
    trip_purpose: str = None,
):
    # 1) Research (account for traveller profile: {traveller_type}, preferences: {raw_preferences})
    fly_note = "(Will fly in/out)" if will_fly else ""
    research_task = Task(
        description=(
            f"Research {destination} {fly_note} for a {traveller_type} traveler with preferences: {raw_preferences}. "
            f"Focus on: safety, neighborhoods, costs, transport, and activity fit for their interests. "
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

    # 3) Visa Requirements (CORE)
    visa_task = Task(
        description=(
            f"CRITICAL: Research visa requirements for travel FROM {passport_country} TO {destination}. "
            f"Traveler: {passport_country} passport holder going to {destination} for {trip_purpose} ({days} days from {start_date}). "
            f"DO NOT research {passport_country} visa requirements. "
            f"DO research what a {passport_country} citizen needs to enter {destination} for {trip_purpose}. "
            f"CRITICAL ACCURACY REQUIRED: "
            f"1) ONLY use official government websites from {destination}'s immigration authority (NOT {passport_country}'s). "
            f"2) Search for: '{passport_country} citizens {destination} visa {trip_purpose}' or '{destination} visa {passport_country} nationality'. "
            f"3) If the official site is unclear or you cannot access it, recommend checking the official embassy/consulate directly. "
            f"4) DO NOT assume visa-free policies - VERIFY from official sources only. "
            f"5) Include: visa type (or 'Check official sources' if uncertain), required documents, application steps, fees in USD, processing time. "
            f"6) For any uncertainty, add a clear warning to verify directly with {destination}'s official embassy/consulate. "
            f"7) Be conservative: if you cannot confirm a policy, state that verification is needed."
        ),
        agent=visa_requirements_advisor,
        context=[research_task],
        expected_output=(
            f"Visa requirements for {passport_country} passport holders entering {destination} for {trip_purpose}. "
            f"From {destination}'s official government sources only. "
            f"Include: visa type required (or visa-free/on-arrival/e-visa), required documents, application process, fees (USD), processing time, official {destination} immigration website link. "
            f"If information is unclear or not verifiable, recommend consulting {destination}'s official embassy/consulate directly in {passport_country}."
        )
    )

    # 4) Health & Wellness Requirements (CORE)
    health_task = Task(
        description=(
            f"Comprehensive health and wellness requirements for {destination} ({traveller_type}, {days}d from {start_date}). "
            f"Research from WHO, CDC, and official health authorities. PROVIDE DETAILED, COMPREHENSIVE OUTPUT. "
            f"CRITICAL SECTIONS (all required, all MUST BE DETAILED): "
            f"1) VACCINES/IMMUNIZATIONS - List EVERY required or recommended vaccine with details: "
            f"   - Which vaccines (MMR, typhoid, hepatitis A/B, yellow fever, etc.) "
            f"   - When to get them (how far in advance before travel) "
            f"   - Why they're needed for this destination "
            f"2) DISEASE RISKS - Detailed overview: "
            f"   - Malaria: risk areas, transmission season, prophylaxis medications and timing "
            f"   - Dengue, yellow fever, typhoid, etc. if applicable: risk level, prevention methods "
            f"   - Include which regions/seasons are highest risk in {destination} "
            f"3) WATER & FOOD SAFETY - Detailed guidance: "
            f"   - Safe water (bottled, filtered, boiled) and proper handling "
            f"   - Food safety practices specific to {destination} "
            f"   - Common foodborne illnesses and how to avoid them "
            f"   - Restaurants/areas to avoid if applicable "
            f"4) COMMON ILLNESSES & PREVENTION - For {destination} specifically: "
            f"   - Most common travel illnesses (traveler's diarrhea, etc.) "
            f"   - How they spread and prevention methods "
            f"   - Symptoms and when to seek medical help "
            f"5) HEALTHCARE QUALITY & ACCESS - {destination} details: "
            f"   - Quality of hospitals/clinics in major cities "
            f"   - Quality in remote areas "
            f"   - Cost of healthcare "
            f"   - Availability of specific medications "
            f"   - Evacuation/repatriation services if needed "
            f"6) TRAVEL MEDICAL INSURANCE - Detailed recommendations: "
            f"   - Why it's essential for {destination} "
            f"   - What coverage to look for (medical evacuation, emergency treatment costs) "
            f"   - Cost estimates and providers "
            f"7) SPECIFIC PRECAUTIONS FOR {traveller_type.upper()} - Age/type-specific guidance. "
            f"CRITICAL: Provide FULL SENTENCES with explanations, not bullet-point summaries. "
            f"Include specific medication names, dosages, timing. Include cost estimates where relevant. "
            f"Recommend consulting healthcare provider 4-6 weeks before travel for personalized advice."
        ),
        agent=health_wellness_advisor,
        context=[research_task],
        expected_output=(
            f"COMPREHENSIVE health requirements for {destination} with detailed sections: "
            f"(1) VACCINES/IMMUNIZATIONS with specific names, timing, reasons; "
            f"(2) DISEASE RISKS with malaria/dengue/typhoid details, seasonal timing, prophylaxis options; "
            f"(3) WATER & FOOD SAFETY with specific guidelines for {destination}; "
            f"(4) COMMON ILLNESSES & PREVENTION specific to this destination; "
            f"(5) HEALTHCARE QUALITY & ACCESS in {destination} cities and remote areas; "
            f"(6) TRAVEL MEDICAL INSURANCE recommendations with specifics; "
            f"(7) SPECIFIC PRECAUTIONS for {traveller_type} travelers. "
            f"MUST use full sentences with explanations. MUST NOT be abbreviated or bullet-point-only. "
            f"Include medication names, dosages, timing. Include cost info. Include recommendation to see healthcare provider 4-6 weeks before travel."
        )
    )

    # 5) Accommodation
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
            f"CRITICAL - ACTIVITY SPECIFICITY: Do NOT suggest vague activities like 'Dinner at a local restaurant' or 'Visit a market'. "
            f"Instead, provide SPECIFIC, NAMED recommendations: "
            f"\n- SPECIFIC VENUES: Name actual restaurants, museums, landmarks (e.g., 'Taj Mahal', 'Joe's Pizza', 'Old Town Market' instead of 'a restaurant'). "
            f"\n- WHAT TO DO: Clearly describe the experience (e.g., 'Try local biryani at famous family-run restaurant' vs 'eat dinner'). "
            f"\n- WHY IT MATTERS: Include why visitors should go (local specialty, historic significance, best views, food culture, etc.). "
            f"\n- PRACTICAL INFO: Add hours, booking tips, dress code, or peak visit times when relevant. "
            f"CRITICAL: Group activities by geographic proximity. Each day's activities must be close to each other to minimize travel time. "
            f"2-3 activities/day max, cluster in same neighborhood, balance active/light based on weather. Avoid backtracking across the city."
        ),
        agent=activities_planner,
        context=[research_task],
        expected_output="Day-by-day activities scheduled for {start_date} with timing, energy level, geographic clustering. Each activity must include: specific venue name, what to do there, why it's worth experiencing, and practical details. Include indoor/outdoor options based on weather forecast. NO vague activity descriptions."
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
            f"NEVER USE ABBREVIATIONS OR PLACEHOLDERS (no '[...continues...]', '[see above]', '[complete details below]', 'etc.', etc.). "
            f"ALWAYS PROVIDE FULL, COMPLETE OUTPUT for every single day. "
            f"ACTIVITY SPECIFICITY CRITICAL: Use SPECIFIC venue names and clear descriptions, NOT vague labels. "
            f"✗ AVOID: 'Visit a market', 'Dinner at restaurant', 'Go shopping' "
            f"✓ USE: 'Explore Old Town Spice Market' or 'Dinner at Chef Marco's seafood restaurant, famous for local catch'. "
            f"For each activity in the 'Activity' column: include the specific venue name and a brief description of what to do there. "
            f"OUTPUT FORMAT - MUST USE EXACT MARKDOWN TABLE FORMAT:"
            f"\n\n## Day 1\n\n"
            f"| Time | Activity | Location | Transport | Cost (USD) | Comment |\n"
            f"| --- | --- | --- | --- | --- | --- |\n"
            f"| 9:00 AM | Visit National Museum | Downtown | Walking | $10 | Learn about local history |\n"
            f"| 11:00 AM | Coffee break | Downtown | Walking | $5 | Local café with wifi |\n"
            f"| 1:00 PM | Lunch at market | Downtown | Walking | $12 | Traditional food, busy area |\n\n"
            f"## Day 2\n\n"
            f"[Next table with same format]\n\n"
            f"REQUIREMENTS: Use pipes (|), include separator row (| --- |), add activities for every single day 1 through {days}. "
            f"DO NOT PUT '[Complete itinerary below]' or similar placeholders or abbreviated forms. Include the FULL itinerary here."
            f"\nCOMMENT GUIDELINES: For each activity, add a helpful comment that includes:"
            f"\n- Brief activity description OR value (e.g., 'Scenic viewpoint', 'Local market, peak hours 8-11am', 'Highly rated, book ahead')"
            f"\n- Realistic experience level (e.g., 'Easy walk', 'Moderate climbing', 'Peaceful spot')"
            f"\n- Travel time to next activity if relevant"
            f"\nDO NOT write generic comments like 'Below budget' or 'Within allocation'—be specific about the activity."
        ),
        agent=itinerary_coordinator,
        context=[research_task, visa_task, health_task, accommodation_task, activities_task, transport_task],
        expected_output=f"Complete markdown itinerary WITH VISA & HEALTH SECTIONS at top, then activities for ALL {days} days. Each day must have: ## Day X heading, blank line, proper markdown table with pipes (|) and separator row (| --- |), then blank line before next day. Columns: Time | Activity | Location | Transport | Cost (USD) | Comment. ALL ACTIVITY NAMES MUST BE SPECIFIC AND CLEAR: Include venue names and 'what to do' descriptions (e.g., 'Visit Old Town Market' or 'Dinner at Marco's Seafood Restaurant'), NOT generic labels like 'Go to a market' or 'Have dinner'. All activities per day grouped in same geographic area. Total cost must fit in ${budget}. Comments must be descriptive about activity value/experience, NOT budget status. NO EMPTY DAYS - every day 1 through {days} must have activities. NO ABBREVIATIONS, PLACEHOLDERS, OR SHORTENED FORMS - OUTPUT MUST BE COMPLETE AND DETAILED."
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
            f"STRUCTURE (in this order): "
            f"\n1. TRIP SNAPSHOT at the very top: travel dates, weather overview, budget breakdown by category. "
            f"\n2. VISA REQUIREMENTS section: visa type, required documents, application process, fees USD, processing time, official website. "
            f"\n3. HEALTH & WELLNESS section: required/recommended vaccines, disease risks, water/food safety, healthcare facilities, travel insurance. "
            f"\n4. ACCOMMODATION section: recommended hotels/lodging options from previous agent output. "
            f"\n5. DAILY ITINERARY: Full day-by-day activity schedule for all {days} days (see formatting below). "
            f"\n6. WEATHER FORECAST section: summary for travel dates ({start_date}, {days} days). "
            f"\n7. PACKING LIST section with SPECIFIC recommendations based on weather and {destination}. "
            f"\n8. SAFETY TIPS section. "
            f"\n9. COST BREAKDOWN section showing per-day allocations. "
            f"Each section must be followed by a BLANK LINE. "
            f"BUDGET ALLOCATIONS: ~${per_day_stay:.0f}/night accommodation, ~${per_day_activities:.0f}/day activities+meals, ~${per_day_transport:.0f}/day transport. "
            f"CRITICAL: Ensure per-day costs stay within allocations AND total trip cost ≤ ${budget}. If over, cut/reduce activities or lodging. "
            f"DAILY FORMAT: Each day uses '## Day X' heading, BLANK LINE, then metrics line 'Feasibility: X/5 | Safety: X/5 | Budget Adherence: X/1 | Per-day Fit: X/1 | Geographic Flow: [locations]', BLANK LINE, then markdown table. "
            f"TABLE COLUMNS ONLY: Time, Activity, Location, Transport, Cost (USD), Comment. "
            f"CRITICAL: All activities MUST BE SPECIFIC with venue names (✗ NEVER 'Visit market' ✓ ALWAYS 'Explore Old Town Spice Market'). "
            f"Each day's activities must be grouped by geographic area—no backtracking across the city. "
            f"Comments describe the activity (what to do, why worth it, experience level), NOT budget status. "
            f"PACKING LIST: Include temperature range, humidity, activity type. Items specific to {destination} conditions, NOT generic advice. "
            f"NEVER USE ABBREVIATIONS OR PLACEHOLDERS like '[...continues...]', 'etc.', '[see above]'. PROVIDE FULL, COMPLETE OUTPUT FOR EVERY DAY AND SECTION. "
            f"All costs in USD. FINAL OUTPUT MUST NOT EXCEED ${budget} AND MUST STAY WITHIN PER-DAY ALLOCATIONS."
        ),
        agent=local_insider,
        context=[verification_task, visa_task, health_task],
        expected_output=f"Final itinerary structure: \n1. ##Trip Snapshot (travel dates, weather, budget breakdown)\n2. ##Visa Requirements (type, documents, process, fees USD, processing time)\n3. ##Health & Wellness (vaccines, disease risks, water/food safety, healthcare)\n4. ##Accommodation Options\n5. ##Daily Itinerary (# Day X heading, metrics line, activity table with Time|Activity|Location|Transport|Cost|Comment) for ALL {days} days\n6. Weather Forecast\n7. Packing List (specific to {destination} weather)\n8. Safety Tips\n9. Cost Breakdown. BLANK LINES between sections. All activity names specific with venue names. Markdown formatted. All costs USD. NO ABBREVIATIONS."
    )

    return [
        research_task,
        visa_task,
        health_task,
        accommodation_task,
        activities_task,
        transport_task,
        coordination_task,
        verification_task,
        local_insights_task,
    ]