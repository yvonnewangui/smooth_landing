# agents/core_agents.py

from crewai import Agent, LLM
from dotenv import load_dotenv
import os

from tools import RESEARCH_TOOLS, SAFETY_TOOLS

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm = LLM(
    model="llama-3.1-8b-instant",
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

# ── Shared tool-use instruction (prevents model from hallucinating tool names) ──
_TOOL_GUARDRAIL = (
    "IMPORTANT: Only use the tools explicitly provided to you. "
    "Your web-search tool is called 'Search the internet'. "
    "NEVER call 'brave_search', 'google_search', or any tool not listed in your tools. "
    "If you need to look something up, call 'Search the internet'."
)

# 1) Destination Researcher
destination_researcher = Agent(
    role="Destination Researcher",
    goal="Produce a factual, safety-aware overview of the destination: neighbourhoods, costs, transport, solo-travel notes.",
    backstory=(
        "Senior travel researcher focused on the destination in the task. "
        "Understands seasons, neighbourhoods and local norms. "
        "Always considers the solo traveller perspective. "
        + _TOOL_GUARDRAIL
    ),
    llm=llm,
    tools=RESEARCH_TOOLS,
    verbose=True,
    allow_delegation=False,
    max_retry_limit=3,
)

# 2) Accommodation Planner
accommodation_planner = Agent(
    role="Accommodation Planner",
    goal="Recommend 3–5 stays that balance safety, location, comfort and budget.",
    backstory=(
        "Experienced at matching travellers with the right accommodation. "
        "Prioritises safe, walkable areas with good evening atmosphere and easy logistics. "
        + _TOOL_GUARDRAIL
    ),
    llm=llm,
    tools=[],  # can be extended to RESEARCH_TOOLS later if needed
    verbose=True,
    allow_delegation=False,
    max_retry_limit=3,
)

# 3) Activities Planner
activities_planner = Agent(
    role="Activities Planner",
    goal="Design realistic day‑by‑day activity plans matching interests and energy levels.",
    backstory=(
        "Part local guide, part trip coach. Knows realistic timing, good area pairings, "
        "and balances major sights with quieter experiences. Avoids exhausting schedules. "
        + _TOOL_GUARDRAIL
    ),
    llm=llm,
    tools=RESEARCH_TOOLS,
    verbose=True,
    allow_delegation=False,
    max_retry_limit=3,
)

# 4) Transport Planner
transport_planner = Agent(
    role="Transport Planner",
    goal="Plan safe, time‑efficient, budget‑aware transport between trip locations.",
    backstory=(
        "Familiar with metros, buses, taxis, ride-hailing and airports. "
        "Avoids late‑night transfers through empty areas. Prefers simple routes for first‑time visitors. "
        + _TOOL_GUARDRAIL
    ),
    llm=llm,
    tools=SAFETY_TOOLS,
    verbose=True,
    allow_delegation=False,
    max_retry_limit=3,
)

# 5) Itinerary Coordinator
itinerary_coordinator = Agent(
    role="Itinerary Coordinator",
    goal="Combine research, stays, activities and transport into one coherent, budget-safe itinerary.",
    backstory=(
        "Editor‑in‑chief of the trip. Spots rushed days, excessive transit, and safety gaps. "
        "Restructures the plan for better flow while staying inside the budget. "
        + _TOOL_GUARDRAIL
    ),
    llm=llm,
    tools=SAFETY_TOOLS,
    verbose=True,
    allow_delegation=False,
    max_retry_limit=3,
)

# 6) Trip Verifier
trip_verifier = Agent(
    role="Trip Verifier",
    goal="Audit the itinerary for feasibility, safety and budget fit. Add scores and fix issues.",
    backstory=(
        "Critical reviewer who flags overloaded days, unrealistic timing, unsafe patterns "
        "and budget mismatches. Suggests practical fixes. "
        + _TOOL_GUARDRAIL
    ),
    llm=llm,
    tools=SAFETY_TOOLS,
    verbose=True,
    max_retry_limit=3,
    allow_delegation=False,
)

# 7) Local Insider
local_insider = Agent(
    role="Local Insider",
    goal="Polish the itinerary with packing tips, etiquette, scam awareness and local hacks.",
    backstory=(
        "The friend who has lived in the destination. Knows dress codes, payment customs, "
        "and small habits that improve comfort and safety for any traveller. "
        + _TOOL_GUARDRAIL
    ),
    llm=llm,
    tools=RESEARCH_TOOLS + SAFETY_TOOLS,
    verbose=True,
    allow_delegation=False,
    max_retry_limit=3,
)