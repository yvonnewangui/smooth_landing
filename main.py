from crewai import Crew
from dotenv import load_dotenv
from tasks.core_tasks import build_core_tasks
from tasks.niche_tasks import build_niche_tasks
from agents.core_agents import (
    destination_researcher,
    accommodation_planner,
    activities_planner,
    transport_planner,
    itinerary_coordinator,
    trip_verifier,
    local_insider,
    llm,  # 👈 import the shared LLM
)
from agents.niche_agents import (
    safari_specialist,
    halal_travel_expert,
    digital_nomad_planner,
    solo_female_safety_advisor,
    family_travel_designer,
    medical_tourism_planner,
    luxury_on_budget_finder,
)
from tasks.pro_safety_tasks import build_pro_safety_task

load_dotenv()


def run_cli():
    print("🧠 Smooth Landing – Multi‑Niche CLI")

    destination = input("Destination (e.g. Paris, France): ")
    budget = float(input("Total budget in USD (e.g. 2500): "))
    days = int(input("Number of days (e.g. 5): "))
    interests = input("Interests (e.g. food, culture, nightlife): ")

    print("\nNiche flags (y/n):")
    safari = input("Include safari planning? (y/n): ").strip().lower() == "y"
    halal = input("Halal/Muslim‑friendly trip? (y/n): ").strip().lower() == "y"
    nomad = input("Digital nomad (working while travelling)? (y/n): ").strip().lower() == "y"
    solo_f = input("Solo female safety focus? (y/n): ").strip().lower() == "y"
    family = input("Family with kids? (y/n): ").strip().lower() == "y"
    medical = input("Medical tourism component? (y/n): ").strip().lower() == "y"
    luxury = input("Add luxury touches on a budget? (y/n): ").strip().lower() == "y"
    raw_preferences = input(
        "\nAny preferences we should remember? "
        "(e.g. mid‑range budget, hate hostels, love food tours, avoid nightlife): "
    )

    pro_safety = input("Add pro safety features? (y/n): ").strip().lower() == "y"

    profile_flags = {
        "safari": safari,
        "halal": halal,
        "nomad": nomad,
        "solo_female": solo_f,
        "family": family,
        "medical": medical,
        "luxury": luxury,
    }

    if solo_f:
        traveller_type = "solo female"
    elif family:
        traveller_type = "family"
    else:
        traveller_type = "solo"

    core_tasks = build_core_tasks(
        destination,
        budget,
        days,
        interests,
        traveller_type,
        raw_preferences,
    )

    core_final_task = core_tasks[-1]
    niche_tasks = build_niche_tasks(destination, budget, days, interests, profile_flags, core_final_task)

    all_tasks = core_tasks + niche_tasks

    if pro_safety:
        pro_safety_task = build_pro_safety_task(destination, days, traveller_type, core_final_task)
        all_tasks.append(pro_safety_task)

    agents = [
        destination_researcher,
        accommodation_planner,
        activities_planner,
        transport_planner,
        itinerary_coordinator,
        trip_verifier,
        local_insider,
        safari_specialist,
        halal_travel_expert,
        digital_nomad_planner,
        solo_female_safety_advisor,
        family_travel_designer,
        medical_tourism_planner,
        luxury_on_budget_finder,
    ]

    crew = Crew(
        agents=agents,
        tasks=all_tasks,
        llm=llm,      # 👈 force Crew to use the Groq-backed LLM with tools
        verbose=True,
    )

    result = crew.kickoff()
    print("\n================ FINAL MULTI‑NICHE ITINERARY ================\n")
    print(result)


if __name__ == "__main__":
    run_cli()