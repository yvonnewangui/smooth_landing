# tasks/tune_up_tasks.py

from crewai import Task
from agents.core_agents import trip_verifier, local_insider
from agents.niche_agents import solo_female_safety_advisor

# Hard cap on how much raw itinerary we ever send to the model
MAX_RAW_ITINERARY_CHARS = 2500  # tighten as needed


def build_tune_up_tasks(
    destination: str,
    budget: float,
    traveller_type: str,
    raw_itinerary: str,
    use_pro_safety: bool = True,
    start_date=None,
):
    """
    Token-optimized tune-up pipeline:
    1) Summarise raw itinerary (short bullets, capped input length).
    2) Verify & lightly tune based on summary, not full text.
    3) Local polish on tuned itinerary.
    4) Optional Pro Safety pass (brief, advisory).

    All task descriptions are kept short and avoid repeating large blocks.
    """

    # --- 0) Short internal summary of the user's itinerary ---
    truncated_itinerary = raw_itinerary[:MAX_RAW_ITINERARY_CHARS]

    date_line = f"Trip start date: {start_date}.\n" if start_date else ""

    summarise_description = (
        f"Destination: {destination}.\n"
        f"{date_line}\n"
        "You are helping another agent by creating a SHORT internal summary of a user-provided itinerary.\n\n"
        "TASK:\n"
        "- Write 8–12 bullet points summarising the structure of the trip.\n"
        "- Focus on: days, main areas/regions, key activities, and pacing.\n"
        "- Do NOT add new ideas, just compress what is there.\n\n"
        "OUTPUT FORMAT:\n"
        "### ITINERARY SUMMARY\n"
        "- [Bullet 1]\n"
        "- [Bullet 2]\n"
    )

    summarise_task = Task(
        description=(
            summarise_description
            + "\n\nUSER ITINERARY (TRUNCATED IF VERY LONG):\n\n"
            + truncated_itinerary
        ),
        agent=trip_verifier,
        expected_output="A concise bullet summary (8–12 bullets) under '### ITINERARY SUMMARY'.",
    )

    # --- 1) Verification + tuned itinerary, using ONLY the summary ---
    verify_description = (
        f"Destination: {destination}. Budget about ${budget}.\n"
        f"{date_line}\n"
        "You are the Trip Verifier.\n"
        "You will see an 'ITINERARY SUMMARY' created from the user's plan.\n"
        "Work ONLY from that summary and the budget; do not invent a totally new trip.\n\n"
        "TASK:\n"
        "1) Assess the plan using this checklist:\n"
        "   - Timeline realism\n"
        "   - Transit/backtracking\n"
        "   - General and solo-female-aware safety\n"
        "   - Rough budget fit\n"
        "   - Overall coherence\n"
        "2) Suggest specific, concrete improvements (not generic advice).\n\n"
        "OUTPUT FORMAT:\n"
        "### TUNED ITINERARY (DRAFT)\n"
        "[Improved but still recognisably similar itinerary, in day-by-day bullets]\n\n"
        "### ISSUES FOUND\n"
        "- [Issue 1]\n"
        "- [Issue 2]\n\n"
        "### CHECKLIST\n"
        "- Timeline: [OK / Needs changes + why]\n"
        "- Transit: [OK / Needs changes + why]\n"
        "- Safety: [OK / Needs changes + why]\n"
        "- Budget: [OK / Needs changes + why]\n"
        "- Coherence: [OK / Needs changes + why]\n"
    )

    verify_task = Task(
        description=verify_description,
        agent=trip_verifier,
        context=[summarise_task],  # only summary flows forward
        expected_output="Draft tuned itinerary plus issues and checklist as specified.",
    )

    # --- 2) Local polish on the tuned itinerary ---
    polish_description = (
        f"Destination: {destination}.\n"
        f"{date_line}\n"
        "You are the Local Insider.\n"
        "Take the 'TUNED ITINERARY (DRAFT)' and turn it into a clear, client-ready version.\n\n"
        "TASK:\n"
        "- Keep the same structure and decisions unless something is clearly unsafe or unrealistic.\n"
        "- Add a SHORT safety & comfort summary at the top (3–5 sentences max).\n"
        "- Keep the day-by-day section concise and skimmable.\n\n"
        "OUTPUT FORMAT:\n"
        "### TRAVEL NINJA ITINERARY\n"
        "[Client-ready, day-by-day itinerary, with dates if helpful]\n\n"
        "### SAFETY & COMFORT SUMMARY\n"
        "[3–5 sentences]\n"
    )

    polish_task = Task(
        description=polish_description,
        agent=local_insider,
        context=[verify_task],
        expected_output="Polished client-ready itinerary with a short safety & comfort summary.",
    )

    tasks = [summarise_task, verify_task, polish_task]

    # --- 3) Optional Pro Safety layer (brief, advisory) ---
    if use_pro_safety:
        pro_safety_description = (
            f"Destination: {destination}.\n"
            f"{date_line}"
            f"Traveller type: {traveller_type}.\n\n"
            "You are the Solo Female Safety & Comfort Advisor running a PRO SAFETY tune-up.\n"
            "Write advice that is especially useful for a cautious or solo-female traveller, "
            "but phrased so any cautious traveller can benefit.\n\n"
            "TASK:\n"
            "- Scan the final itinerary for key risks or discomfort points.\n"
            "- Suggest practical adjustments without rewriting the whole trip.\n"
            "- Provide a short, actionable checklist the traveller can save.\n\n"
            "OUTPUT FORMAT:\n"
            "### PRO SAFETY TUNE-UP REPORT\n"
            "- Key risks\n"
            "- Recommended adjustments\n"
            "- Short checklist\n"
        )

        pro_safety_task = Task(
            description=pro_safety_description,
            agent=solo_female_safety_advisor,
            context=[polish_task],
            expected_output="Brief Pro Safety tune-up report with risks, adjustments, and checklist.",
        )
        tasks.append(pro_safety_task)

    return tasks
