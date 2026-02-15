from crewai import Task
from agents.niche_agents import solo_female_safety_advisor


def build_pro_safety_task(destination: str, days: int, traveller_type: str, core_final_task):
    """
    core_final_task: usually the local_insights_task (already verified itinerary).
    traveller_type: e.g. 'solo female', 'solo', 'family', etc.
    """

    description = (
        "You are the Solo Female Safety & Comfort Advisor running a PRO SAFETY review.\n\n"
        f"TRIP CONTEXT: A {days}-day trip to {destination} for a {traveller_type} traveller.\n\n"
        "INPUT: An already-verified and locally polished itinerary.\n\n"
        "YOUR JOB (PRO SAFETY LAYER):\n"
        "1) Deep-scan the itinerary for safety and comfort, especially from a solo female perspective, "
        "but keep your advice useful for any traveller:\n"
        "- Flag risky late-night movements (after ~22:00), long walks in unfamiliar areas, or complex transfers when tired.\n"
        "- Check accommodation areas for isolation, poor connections, or frequent safety concerns.\n"
        "- Review nightlife and social elements; prefer group formats, trusted venues, and clearer routes home.\n"
        "- Note where a traveller might feel isolated or overwhelmed and suggest softer options.\n\n"
        "2) PROPOSE ADJUSTMENTS:\n"
        "- Suggest specific changes to timings, locations or transport modes to reduce risk.\n"
        "- Briefly explain the reason for each change.\n"
        "- Be calm and practical; avoid alarmist tone.\n\n"
        "3) OUTPUT IN THIS FORMAT:\n\n"
        "### PRO SAFETY REPORT\n"
        "[2–4 short paragraphs summarising overall safety level and key themes.]\n\n"
        "### KEY RISKS IDENTIFIED\n"
        "- [Risk 1]\n"
        "- [Risk 2]\n"
        "- [Risk 3]\n"
        "(If few clear risks, say so and explain why the trip feels relatively safe.)\n\n"
        "### RECOMMENDED ADJUSTMENTS\n"
        "- [Change X → Y, because ...]\n"
        "- [Change A → B, because ...]\n\n"
        "### PRO SAFETY CHECKLIST\n"
        "- Accommodation: [OK / Improve] – short note\n"
        "- Evening movements: [OK / Improve] – short note\n"
        "- Social activities: [OK / Improve] – short note\n"
        "- Emergency readiness: [OK / Improve] – short note\n\n"
        "### UPDATED ITINERARY (IF CHANGES ARE SIGNIFICANT)\n"
        "[If you made meaningful changes, rewrite the affected days here. "
        "If not, state: 'No structural changes needed; itinerary remains as previously verified.']\n"
    )

    pro_safety_task = Task(
        description=description,
        agent=solo_female_safety_advisor,
        context=[core_final_task],
        expected_output="A structured Pro Safety report with any key itinerary changes."
    )

    return pro_safety_task
