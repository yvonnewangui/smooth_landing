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
                    f"For this {days}-day trip including {destination}, for a traveller interested in {interests}, "
                    f"starting on {start_date}, suggest how to weave in an ethical safari experience "
                    "(especially East Africa if applicable). "
                    "Recommend specific parks or conservancies, best timing in the trip, "
                    "and how many days to allocate. Keep it concise (max ~400 words)."
                ),
                agent=safari_specialist,
                expected_output="Safari suggestions section that can be appended to the main itinerary.",
            )
        )

    if profile_flags.get("halal"):
        niche_tasks.append(
            Task(
                description=(
                    f"For this trip to {destination}, for a traveller whose main interests are {interests}, "
                    "adapt the itinerary for a Muslim traveller: highlight halal food options, "
                    "practical ways to align prayer times with the schedule, "
                    "and avoid activities or nightlife that may not be appropriate. "
                    "Assume a mid-range budget and keep it under ~400 words."
                ),
                agent=halal_travel_expert,
                expected_output="Halal-focused notes section that can be appended.",
            )
        )

    if profile_flags.get("nomad"):
        niche_tasks.append(
            Task(
                description=(
                    f"For this {days}-day trip to {destination}, for someone interested in {interests}, "
                    "adjust the plan for a digital nomad working online. "
                    "Suggest where to place focused work blocks, which areas/cafes/co-working spots are suitable, "
                    "and how to balance work and exploration without burnout. "
                    "Limit to ~400 words and use clear bullet points."
                ),
                agent=digital_nomad_planner,
                expected_output="Digital-nomad notes section that can be appended.",
            )
        )

    # Solo safety (independent of nomad)
    if profile_flags.get("solo_female"):
        niche_tasks.append(
            Task(
                description=(
                    f"From a solo female perspective, review this {days}-day {destination} trip for someone "
                    f"whose top interests are {interests}. "
                    "Flag typical unsafe patterns (very late nights, isolated areas, risky transport), "
                    "suggest safer lodging areas, adjust late-night returns, "
                    "and propose safer transport options. Include a clear safety checklist. "
                    f"Trip dates: starting {start_date} for {days} days.\n"
                    "Keep it focused and under ~500 words."
                ),
                agent=solo_female_safety_advisor,
                expected_output="Solo-female enhanced safety notes plus a checklist.",
            )
        )
    else:
        niche_tasks.append(
            Task(
                description=(
                    f"Review this {days}-day {destination} trip for general personal safety, "
                    f"for a traveller interested in {interests}. "
                    "Highlight safer neighbourhoods, better-lit routes, and low-risk evening options, "
                    "and suggest a few practical safety habits. "
                    f"Trip dates: starting {start_date} for {days} days.\n"
                    "Write a short notes section (max ~300 words)."
                ),
                agent=solo_female_safety_advisor,
                expected_output="General safety notes and small itinerary tweaks.",
            )
        )

    if profile_flags.get("family"):
        niche_tasks.append(
            Task(
                description=(
                    f"Adapt this {days}-day {destination} trip for a family with children who enjoy {interests}. "
                    "Adjust timing so children are not exhausted, check for age/height restrictions on activities, "
                    "and suggest explicitly kid-friendly stops and meal choices. "
                    "Summarise in a concise section (max ~400 words)."
                ),
                agent=family_travel_designer,
                expected_output="Family-focused adjustments section.",
            )
        )

    if profile_flags.get("medical"):
        niche_tasks.append(
            Task(
                description=(
                    f"Adapt this trip to {destination} for someone combining travel with medical appointments "
                    f"or a procedure, whose interests are mainly {interests}. "
                    "Schedule low-exertion days before and after key appointments, "
                    "ensure proximity to facilities, and avoid risky activities. "
                    "Keep the advice practical and under ~400 words."
                ),
                agent=medical_tourism_planner,
                expected_output="Medical-tourism adjustments section.",
            )
        )

    if profile_flags.get("luxury"):
        niche_tasks.append(
            Task(
                description=(
                    f"Within a total budget of about ${budget}, for a traveller interested in {interests}, "
                    f"add a few targeted 'luxury' elements to this trip to {destination} "
                    "(one or two special dinners, a memorable hotel night, a standout experience) "
                    "while keeping the rest of the trip reasonable. "
                    "Provide 3–7 specific suggestions in bullet form."
                ),
                agent=luxury_on_budget_finder,
                expected_output="Luxury-on-a-budget suggestions section.",
            )
        )

    # Optional: visa branch, only if you have passport_country and trip_purpose and flag set
    if profile_flags.get("visa") and passport_country and trip_purpose:
        niche_tasks.append(
            Task(
                description=(
                    "You are the Visa & Entry Requirements Advisor.\n\n"
                    f"Traveller passport: {passport_country}.\n"
                    f"Destination: {destination}.\n"
                    f"Trip purpose: {trip_purpose}.\n"
                    f"Trip start date: {start_date} (approx {days} days).\n\n"
                    "TASK:\n"
                    "- Summarise the likely visa/entry situation for this trip "
                    "(visa-free, visa on arrival, eVisa, or visa required).\n"
                    "- Mention passport validity rules, onward ticket, and typical proof-of-funds requirements if relevant.\n"
                    "- Highlight any special forms (e.g. eTA, eArrival, online registrations) a cautious traveller should know.\n"
                    "- Always tell the traveller to confirm with official government or embassy sources before booking.\n\n"
                    "OUTPUT FORMAT:\n"
                    "### VISA & ENTRY OVERVIEW\n"
                    "[3–6 sentences]\n\n"
                    "### PRACTICAL CHECKLIST\n"
                    "- [Checklist item 1]\n"
                    "- [Checklist item 2]\n"
                    "- [Checklist item 3]\n"
                ),
                agent=visa_requirements_advisor,
                expected_output="Visa & entry overview plus a short practical checklist.",
            )
        )

    return niche_tasks
