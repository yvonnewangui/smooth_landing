# tools.py

import os
import datetime
from typing import List
from dotenv import load_dotenv
from crewai_tools import SerperDevTool

load_dotenv()

# =====================================================
# 1) REAL CREWAI TOOL: WEB SEARCH (SERPER)
# =====================================================

serper_api_key = os.getenv("SERPER_API_KEY")

web_search = SerperDevTool(
    # n_results=10,
    # search_type="search",
    # api_key=serper_api_key,
    # save_file=False,
)

# =====================================================
# 2) HELPER FUNCTIONS (NOT PASSED AS Agent.tools)
# =====================================================
# These keep your rich logic but are plain Python helpers.
# Use them inside Task descriptions (via f-strings), NOT as tools=[].


def build_safety_profile(destination: str, traveller_type: str = "general") -> str:
    """Structured safety notes you can inject into task descriptions."""
    base = [
        f"Safety profile for {destination}:",
        "- Check current travel advisories (government sites, recent news).",
        "- Typical risks: pickpocketing, taxi scams, drink spiking in nightlife areas.",
        "- Safer behaviours: stay in busy, well‑lit areas; avoid deserted streets late at night.",
        "- Prefer official taxis / ride‑hailing apps with tracking.",
    ]
    if "solo" in traveller_type.lower() or "female" in traveller_type.lower():
        base.append("\nSolo female–focused notes:")
        base.extend([
            "- Prioritise well-reviewed hotels/hostels with many female reviews.",
            "- Avoid shared taxis/ride‑shares without licence or app tracking.",
            "- Try to arrive in new cities during daylight when possible.",
            "- Join group tours for nightlife or remote activities.",
        ])
    base.append(
        "\nAlways cross‑check with up‑to‑date sources (government advisories, local news, recent blogs)."
    )
    return "\n".join(base)


def estimate_route_reasonableness(stops: List[str], last_activity_time: str = "22:00") -> str:
    """Helper describing whether a sequence of stops is reasonable and safe."""
    if not stops:
        return "No stops provided – route looks empty."

    transfers = len(stops) - 1
    approx_travel_minutes = transfers * 30
    lines = [
        f"Planned stops: {', '.join(stops)}",
        f"Approximate transfers: {transfers}, ~{approx_travel_minutes} minutes total transit.",
    ]

    try:
        hour = int(last_activity_time.split(":")[0])
        if hour >= 22:
            lines.append(
                "Last activity ends after 22:00: ideally keep the final stop close to the accommodation "
                "and in a busy, well‑lit area."
            )
    except Exception:
        lines.append("Could not parse last_activity_time; check late‑night moves manually.")

    if transfers >= 4:
        lines.append(
            "There are many area changes in one day – consider clustering activities by neighbourhood."
        )

    return "\n".join(lines)


def build_budget_summary_hint(
    total_budget_usd: float,
    num_days: int,
    accommodation_per_night: float | None = None,
    daily_food: float | None = None,
    daily_activities: float | None = None,
    total_transport: float | None = None,
) -> str:
    """
    Very rough budget breakdown hint you can pre‑inject into tasks.
    If per‑category values are not provided, use simple heuristics.
    """
    if accommodation_per_night is None:
        accommodation_per_night = (total_budget_usd * 0.45) / max(num_days, 1)
    if daily_food is None:
        daily_food = (total_budget_usd * 0.25) / max(num_days, 1)
    if daily_activities is None:
        daily_activities = (total_budget_usd * 0.20) / max(num_days, 1)
    if total_transport is None:
        total_transport = total_budget_usd * 0.10

    acc_total = accommodation_per_night * num_days
    food_total = daily_food * num_days
    act_total = daily_activities * num_days
    total_est = acc_total + food_total + act_total + total_transport
    buffer = total_budget_usd - total_est

    lines = [
        f"Rough budget hint for ~${total_budget_usd:.0f} over {num_days} days:",
        f"- Accommodation ≈ ${acc_total:.0f} total (≈ ${accommodation_per_night:.0f}/night)",
        f"- Food           ≈ ${food_total:.0f} total (≈ ${daily_food:.0f}/day)",
        f"- Activities      ≈ ${act_total:.0f} total (≈ ${daily_activities:.0f}/day)",
        f"- Transport       ≈ ${total_transport:.0f} total",
        f"- Estimated total ≈ ${total_est:.0f} (buffer ≈ ${buffer:.0f}).",
        "Use these as soft guides only; you may deviate but should explain if you go far above.",
    ]
    return "\n".join(lines)


def describe_season(destination: str, month: int | None = None) -> str:
    """High‑level seasonal description based on month."""
    if month is None:
        month = datetime.datetime.utcnow().month

    if month in (12, 1, 2):
        season = "winter (north) / summer (south)"
    elif month in (3, 4, 5):
        season = "spring (north) / autumn (south)"
    elif month in (6, 7, 8):
        season = "summer (north) / winter (south)"
    else:
        season = "autumn (north) / spring (south)"

    return (
        f"For {destination}, this month likely corresponds to {season}. "
        "Use this to bias clothing and activity suggestions (lighter days in heat, "
        "more indoor options in rain/cold), then refine with live forecasts via web search."
    )


def build_solo_female_checklist(destination: str) -> str:
    """Detailed solo‑female checklist you can embed in Pro Safety / niche tasks."""
    lines = [
        f"Solo female travel checklist for {destination}:",
        "- Choose accommodation with 24/7 reception and strong recent reviews.",
        "- Prefer central, busy areas over isolated outskirts.",
        "- Avoid walking alone through quiet, poorly‑lit areas late at night.",
        "- Use licensed taxis/ride‑hailing apps at night instead of long walks.",
        "- Share your itinerary and hotel details with a trusted contact.",
        "- Use live location sharing when going out in the evening.",
        "- Join group tours or meetups for socialising in a safer way.",
    ]
    return "\n".join(lines)


def demo_flight_options(origin: str, destination: str, departure_date: str) -> str:
    """Stub text for flight options you can include in itineraries."""
    return (
        f"[Demo] Flights {origin} → {destination} on {departure_date}:\n"
        "- Morning flight ~08:30, economy, about $650.\n"
        "- Evening flight ~19:45, economy, about $620.\n"
        "Replace with a real flight API later."
    )


def demo_hotel_options(destination: str, budget_level: str = "mid") -> str:
    """Stub text for hotel options you can include in itineraries."""
    if budget_level == "low":
        return (
            f"[Demo] Budget stays in {destination}:\n"
            "- Friendly Hostel – dorms, ~$25/night.\n"
            "- Basic Guesthouse – private room, ~$45/night.\n"
        )
    elif budget_level == "high":
        return (
            f"[Demo] Higher-end stays in {destination}:\n"
            "- Grand City Hotel – 4★, central, ~$220/night.\n"
            "- Boutique Luxe – design hotel, ~$260/night.\n"
        )
    else:
        return (
            f"[Demo] Mid-range stays in {destination}:\n"
            "- City Central Hotel – 3★+, ~$120/night.\n"
            "- Cozy Boutique Stay – ~$150/night.\n"
        )


# =====================================================
# 3) GROUPS EXPOSED TO AGENTS
# =====================================================

# Only SerperDevTool is passed as a true CrewAI tool; helpers are used inside task descriptions.
RESEARCH_TOOLS = [web_search]
SAFETY_TOOLS = [web_search]
BOOKING_TOOLS = [web_search]