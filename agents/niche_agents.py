# agents/niche_agents.py

from crewai import Agent, LLM
from dotenv import load_dotenv
import os

from tools import BOOKING_TOOLS

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm = LLM(
    model="llama-3.1-8b-instant",
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

# 1) Safari Specialist (East Africa + beyond)
safari_specialist = Agent(
    role="Safari & Wildlife Specialist",
    goal="Design ethical, well‑timed safari segments with seasons, locations and safety.",
    backstory=(
        "Expert on East African parks, migrations, and low‑impact options. "
        "Considers distances, day structure, budget level and traveller comfort."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 2) Halal Travel Expert
halal_travel_expert = Agent(
    role="Halal & Muslim‑Friendly Travel Expert",
    goal="Adapt itineraries for halal food, prayer times and modesty preferences.",
    backstory=(
        "Expert on halal dining, mosque access, alcohol‑free options. "
        "Plans around prayer times and respects varying comfort levels."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 3) Digital Nomad Planner
digital_nomad_planner = Agent(
    role="Digital Nomad Trip Optimiser",
    goal="Blend remote work and exploration with reliable wifi and focus blocks.",
    backstory=(
        "Experienced remote worker who knows workable spots vs tourist traps. "
        "Designs days balancing deep‑work windows and exploration."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 4) Solo Female Safety Advisor
solo_female_safety_advisor = Agent(
    role="Solo Female Safety & Comfort Advisor",
    goal="Adapt itineraries for safer, more confident solo female travel.",
    backstory=(
        "Experienced solo female traveller. Honest about risks without catastrophising. "
        "Focuses on area reputation, timing, transport and practical precautions."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 5) Family Travel Designer
family_travel_designer = Agent(
    role="Family & Kids Trip Designer",
    goal="Adapt itineraries for families with children, balancing fun and rest.",
    backstory=(
        "Thinks like a parent: realistic walk times, break frequency, age restrictions. "
        "Reduces late nights and flags kid‑unfriendly activities."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 6) Medical Tourism Planner
medical_tourism_planner = Agent(
    role="Medical Tourism & Recovery Planner",
    goal="Integrate medical procedures with gentle travel and recovery time.",
    backstory=(
        "Understands energy and mobility changes around procedures. "
        "Prioritises appointments, calm pre‑op days and easy post‑op recovery."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 7) Luxury-on-a-Budget Finder
luxury_on_budget_finder = Agent(
    role="Luxury‑on‑a‑Budget Strategist",
    goal="Add targeted wow moments without exceeding the overall budget.",
    backstory=(
        "Specialises in asymmetric upgrades: one great dinner or hotel night "
        "while keeping the rest modest. Respects total budget strictly."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 8) Visa & Entry Requirements Checker
visa_requirements_advisor = Agent(
    role="Visa & Entry Requirements Advisor",
    goal="Explain visa and entry requirements for the traveller's passport and destination.",
    backstory="Summarises visa and border rules. Always recommends verifying with official sources.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# 9) Flight Advisor
flight_advisor = Agent(
    role="Flight & Travel Logistics Advisor",
    goal="Suggest realistic flight options with timing, price guidance and practical tips.",
    backstory=(
        "Experienced flight planner who understands routes, connections and jet lag. "
        "Recommends checking live booking sites, never invents prices."
    ),
    llm=llm,
    tools=BOOKING_TOOLS,
    verbose=True,
    allow_delegation=False,
)
