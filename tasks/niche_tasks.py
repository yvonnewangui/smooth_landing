from crewai import Task
from agents.niche_agents import (
    safari_specialist,
    halal_travel_expert,
    digital_nomad_planner,
    solo_female_safety_advisor,
    family_travel_designer,
    medical_tourism_planner,
    luxury_on_budget_finder,
    visa_requirements_advisor,
    flight_advisor,
)


def build_niche_tasks(
    destination: str,
    budget: float,
    days: int,
    interests: str,
    profile_flags: dict,
    start_date,
    passport_country: str | None = None,
    trip_purpose: str | None = None,
    home_airport: str | None = None,
):
    """
    profile_flags example:
    {
        "safari": True,
        "halal": False,
        "nomad": True,
        "solo_female": False,
        "family": False,
        "medical": False,
        "luxury": True,
        "visa": True,
    }

    Each task produces a short section that can be appended or woven into
    the core itinerary by the user.
    """
    niche_tasks = []

    if profile_flags.get("safari"):
        niche_tasks.append(
            Task(
                description=(
                    f"Weave ethical safari into {days}-day {destination} trip ({interests}).\\n"
                    "Recommend specific parks/conservancies, best timing in trip, days to allocate."
                ),
                agent=safari_specialist,
                expected_output="Safari suggestions section for main itinerary.",
            )
        )

    if profile_flags.get("halal"):
        niche_tasks.append(
            Task(
                description=(
                    f"Adapt {destination} trip ({interests}) for Muslim traveller.\\n"
                    "Highlight: halal food options, prayer times integration, appropriate activities/nightlife."
                ),
                agent=halal_travel_expert,
                expected_output="Halal-focused adjustments for main itinerary.",
            )
        )

    if profile_flags.get("nomad"):
        niche_tasks.append(
            Task(
                description=(
                    f"Adjust {days}-day {destination} plan ({interests}) for digital nomad.\\n"
                    "Suggest: work-focused blocks, suitable cafes/co-working, balance work vs exploration without burnout."
                ),
                agent=digital_nomad_planner,
                expected_output="Digital-nomad adjustments for main itinerary.",
            )
        )

    # Solo safety (independent of nomad)
    if profile_flags.get("solo_female"):
        niche_tasks.append(
            Task(
                description=(
                    f"Solo female review: {days}-day {destination} trip ({interests}).\\n"
                    "Flag unsafe patterns (late nights, isolated areas, risky transport).\\n"
                    "Suggest safer lodging, adjusted late-night returns, transport options. Include safety checklist."
                ),
                agent=solo_female_safety_advisor,
                expected_output="Solo-female safety notes with checklist.",
            )
        )
    else:
        niche_tasks.append(
            Task(
                description=(
                    f"General safety review: {days}-day {destination} trip ({interests}).\\n"
                    "Highlight safer neighborhoods, better-lit routes, low-risk evening options.\\n"
                    "Suggest practical safety habits."
                ),
                agent=solo_female_safety_advisor,
                expected_output="Safety notes and itinerary adjustments.",
            )
        )

    if profile_flags.get("family"):
        niche_tasks.append(
            Task(
                description=(
                    f"Adapt {days}-day {destination} trip ({interests}) for family with kids.\\n"
                    "Adjust timing (no exhaustion), check age/height restrictions, suggest kid-friendly stops/meals."
                ),
                agent=family_travel_designer,
                expected_output="Family-focused adjustments section.",
            )
        )

    if profile_flags.get("medical"):
        niche_tasks.append(
            Task(
                description=(
                    f"Adapt {destination} trip ({interests}) for medical travel.\\n"
                    "Schedule low-exertion days before/after key appointments.\\n"
                    "Ensure facility proximity, avoid risky activities. Keep advice practical."
                ),
                agent=medical_tourism_planner,
                expected_output="Medical-tourism adjustments section.",
            )
        )

    if profile_flags.get("luxury"):
        niche_tasks.append(
            Task(
                description=(
                    f"Add luxury within ${budget} {destination} trip ({interests}).\\n"
                    "Suggest 3–7 targeted 'wow' elements (special dinners, memorable night, standout experience) "
                    "while keeping rest reasonable."
                ),
                agent=luxury_on_budget_finder,
                expected_output="Luxury-on-a-budget suggestions in bullet form.",
            )
        )

    # Optional: visa branch, only if you have passport_country and trip_purpose and flag set
    if profile_flags.get("visa") and passport_country and trip_purpose:
        niche_tasks.append(
            Task(
                description=(
                    f"Passport: {passport_country} → {destination} ({trip_purpose}, {days}d from {start_date}).\\n\\n"
                    "Summarize: visa/entry status (free/arrival/eVisa/required), passport validity, "
                    "onward ticket, proof-of-funds, special forms (eTA, eArrival).\\n"
                    "Remind traveller to verify with official government/embassy before booking.\\n\\n"
                    "OUTPUT:\\n"
                    "### VISA & ENTRY\\n"
                    "[Summary]\\n\\n"
                    "### CHECKLIST\\n"
                    "- [Item 1]\\n"
                    "- [Item 2]"
                ),
                agent=visa_requirements_advisor,
                expected_output="Visa overview with checklist.",
            )
        )

    if profile_flags.get("flights") and home_airport:
        niche_tasks.append(
            Task(
                description=(
                    f"{home_airport} → {destination} ({days}d from {start_date}, ~${budget}).\n\n"
                    "CRITICAL: You MUST use search_flights_oneway or search_flights_roundtrip to get real flight data.\n"
                    "For each leg, display ACTUAL flight results with: airline, departure/arrival times, duration, price, stops.\n"
                    "Then suggest 2–3 recommended outbound windows and 2–3 return windows based on real options.\n"
                    "Include price levels (budget/moderate/premium), practical tips (connections, jet lag, transfers)."
                ),
                agent=flight_advisor,
                expected_output=(
                    "### FLIGHT OPTIONS (REAL DATA)\n"
                    "**OUTBOUND OPTIONS:**\n"
                    "- [Airline] Flight [Number] | [Depart Time] → [Arrive Time] | Duration: [Time] | Stops: [number] | Price: $[Amount]\n\n"
                    "**RETURN OPTIONS:**\n"
                    "- [Airline] Flight [Number] | [Depart Time] → [Arrive Time] | Duration: [Time] | Stops: [number] | Price: $[Amount]\n\n"
                    "### RECOMMENDED WINDOWS\n"
                    "**OUTBOUND (prefer morning/evening):**\n"
                    "- Window 1: [Date, airline, price]\n"
                    "- Window 2: [Date, airline, price]\n\n"
                    "**RETURN (prefer morning/evening):**\n"
                    "- Window 1: [Date, airline, price]\n"
                    "- Window 2: [Date, airline, price]\n\n"
                    "### PRICE & TIPS\n"
                    "- [Budget/moderate/premium summary]\n"
                    "- [Practical tips: connections, jet lag, transfers]"
                ),
            )
        )

    return niche_tasks
