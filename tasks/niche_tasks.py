import re
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


def _city_to_iata(city_name: str, airports: dict | None = None) -> str:
    """Resolve a city/destination name to its IATA code. Falls back to the original name."""
    if not city_name or not airports:
        return city_name
    # Already an IATA code (3 uppercase letters)?
    if len(city_name) == 3 and city_name.isalpha() and city_name.isupper():
        return city_name
    city_lower = city_name.lower().strip()
    for code, name in airports.items():
        if name.lower() == city_lower or city_lower in name.lower():
            return code
    return city_name


OFFICIAL_VISA_SITES = {
    "ghana": "https://www.ghana.gov.gh/visa",
    "kenya": "https://www.etakenya.go.ke",
    "south africa": "http://www.dha.gov.za",
    "tanzania": "https://visa.immigration.go.tz",
    "uganda": "https://visas.immigration.go.ug",
    "rwanda": "https://www.migration.gov.rw",
    "ethiopia": "https://www.evisa.gov.et",
    "nigeria": "https://portal.immigration.gov.ng",
    "egypt": "https://visa2egypt.gov.eg",
    "morocco": "https://www.consulat.ma",
    "usa": "https://travel.state.gov/visa",
    "uk": "https://www.gov.uk/check-uk-visa",
    "canada": "https://www.canada.ca/en/immigration-refugees-citizenship",
    "australia": "https://immi.homeaffairs.gov.au",
    "india": "https://indianvisaonline.gov.in",
    "japan": "https://www.mofa.go.jp/j_info/visit/visa",
    "china": "https://www.visaforchina.cn",
    "thailand": "https://www.thaievisa.go.th",
    "uae": "https://www.icp.gov.ae",
    "turkey": "https://www.evisa.gov.tr",
    "brazil": "https://www.gov.br/mre/en/subjects/visas",
    "mexico": "https://www.inm.gob.mx",
    "france": "https://france-visas.gouv.fr",
    "germany": "https://www.auswaertiges-amt.de/en/visa-service",
    "italy": "https://vistoperitalia.esteri.it",
    "spain": "https://www.exteriores.gob.es/en/ServiciosAlCiudadano/Paginas/Visados.aspx",
    "singapore": "https://www.ica.gov.sg/enter-transit-depart/entering-singapore/visa_requirements",
    "malaysia": "https://www.imi.gov.my",
    "indonesia": "https://molina.imigrasi.go.id",
    "philippines": "https://www.dfa.gov.ph",
    "south korea": "https://www.visa.go.kr",
    "new zealand": "https://www.immigration.govt.nz/new-zealand-visas",
    "portugal": "https://www.vistos.mne.gov.pt",
    "netherlands": "https://www.netherlandsandyou.nl/travel-and-residence/visas-for-the-netherlands",
    "colombia": "https://www.cancilleria.gov.co/en/procedures_services/visas",
    "argentina": "https://www.cancilleria.gob.ar/en",
    "peru": "https://www.gob.pe/migraciones",
    "vietnam": "https://evisa.xuatnhapcanh.gov.vn",
    "cambodia": "https://www.evisa.gov.kh",
    "sri lanka": "https://www.eta.gov.lk",
    "nepal": "https://www.immigration.gov.np",
    "zambia": "https://www.zambiaimmigration.gov.zm",
    "zimbabwe": "https://www.evisa.gov.zw",
    "mozambique": "https://www.portaldogoverno.gov.mz",
    "senegal": "https://www.service-public.sn",
    "cote d'ivoire": "https://www.snedai.com",
}


def _get_visa_site(destination: str) -> str:
    """Look up the official visa/immigration site for a destination country."""
    dest_lower = destination.lower().strip()
    for country, url in OFFICIAL_VISA_SITES.items():
        if country in dest_lower or dest_lower in country:
            return url
    return ""


def _summarise_itinerary(core_itinerary: str | None, destination: str) -> str:
    """Extract day headings from the core itinerary to keep token count low."""
    if not core_itinerary:
        return destination
    # Pull lines that look like day headers (e.g. "Day 1: ...", "## Day 2 – ...")
    headers = re.findall(r"(?:^|\n)\s*(?:#+ *)?(?:Day \d+[:\-–—].+)", core_itinerary)
    if headers:
        return " | ".join(h.strip().lstrip("#").strip() for h in headers[:10])
    # Fallback: first 300 chars
    return core_itinerary[:300]


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
    core_itinerary: str | None = None,
    airports: dict | None = None,
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
    plan = _summarise_itinerary(core_itinerary, destination)

    if profile_flags.get("safari"):
        niche_tasks.append(
            Task(
                description=f"Add safari overlay for {destination} ({days}d). Plan: {plan}. Recommend parks, timing, days.",
                agent=safari_specialist,
                expected_output="Safari overlay section.",
            )
        )

    if profile_flags.get("halal"):
        niche_tasks.append(
            Task(
                description=f"Add halal overlay for {destination} ({days}d). Plan: {plan}. Recommend halal food, prayer times.",
                agent=halal_travel_expert,
                expected_output="Halal overlay section.",
            )
        )

    if profile_flags.get("nomad"):
        niche_tasks.append(
            Task(
                description=f"Add nomad overlay for {destination} ({days}d). Plan: {plan}. Recommend co-working, wifi, work blocks.",
                agent=digital_nomad_planner,
                expected_output="Nomad overlay section.",
            )
        )

    # Solo safety (independent of nomad)
    if profile_flags.get("solo_female"):
        niche_tasks.append(
            Task(
                description=f"Add solo female safety overlay for {destination} ({days}d). Plan: {plan}. Flag risks, safer areas, transport.",
                agent=solo_female_safety_advisor,
                expected_output="Solo female safety overlay.",
            )
        )
    else:
        niche_tasks.append(
            Task(
                description=f"Add safety overlay for {destination} ({days}d). Plan: {plan}. Safer areas, transport, timing.",
                agent=solo_female_safety_advisor,
                expected_output="Safety overlay section.",
            )
        )

    if profile_flags.get("family"):
        niche_tasks.append(
            Task(
                description=f"Add family overlay for {destination} ({days}d). Plan: {plan}. Kid-friendly activities, pacing, meals.",
                agent=family_travel_designer,
                expected_output="Family overlay section.",
            )
        )

    if profile_flags.get("medical"):
        niche_tasks.append(
            Task(
                description=f"Add medical overlay for {destination} ({days}d). Plan: {plan}. Facility proximity, rest days.",
                agent=medical_tourism_planner,
                expected_output="Medical overlay section.",
            )
        )

    if profile_flags.get("luxury"):
        niche_tasks.append(
            Task(
                description=f"Add luxury overlay for {destination} ({days}d, ${budget} USD). Plan: {plan}. 3-5 wow moments within budget. All costs in USD.",
                agent=luxury_on_budget_finder,
                expected_output="Luxury overlay section.",
            )
        )

    # Optional: visa branch
    if profile_flags.get("visa") and passport_country and trip_purpose:
        visa_site = _get_visa_site(destination)
        visa_site_line = f" Official visa site: {visa_site}" if visa_site else ""
        niche_tasks.append(
            Task(
                description=(
                    f"Visa requirements: {passport_country} passport → {destination} "
                    f"({trip_purpose}, {days}d from {start_date}).{visa_site_line} "
                    f"Include: 1) visa type needed, 2) required documents (passport validity, photos, "
                    f"invitation letter, proof of funds, return ticket, insurance), "
                    f"3) application steps and where to apply (online portal, embassy, on arrival), "
                    f"4) fees in USD, 5) processing time, 6) official website/portal link for application."
                ),
                agent=visa_requirements_advisor,
                expected_output=(
                    "Visa checklist with: visa type, required documents, application steps, "
                    "fees, processing time, and official application website link."
                ),
            )
        )

    if profile_flags.get("flights") and home_airport:
        from datetime import datetime as _dt
        _now = _dt.now().strftime("%Y-%m-%d %H:%M")
        # Resolve destination city name to IATA code
        dest_iata = _city_to_iata(destination, airports)
        niche_tasks.append(
            Task(
                description=(
                    f"Find flights: {home_airport} → {dest_iata}, departing around {start_date}, budget ${budget} USD. "
                    f"Current date: {_now}. "
                    f"STEP 1: Call search_flights_oneway with origin='{home_airport}', destination='{dest_iata}', date='{start_date}'. "
                    f"STEP 2: If step 1 returns empty, error, or no useful results, MUST call 'Search the internet' with query like "
                    f"'flights from {home_airport} to {dest_iata} airlines prices'. "
                    f"Provide: airlines serving this route, typical price range, flight duration, and links to Skyscanner/Google Flights."
                ),
                agent=flight_advisor,
                expected_output="Flight options from API, OR web-searched route info with airlines, prices, duration, and booking links.",
            )
        )

    return niche_tasks
