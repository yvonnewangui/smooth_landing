import datetime
import time
import streamlit as st
from crewai import Crew
from dotenv import load_dotenv

from tasks.core_tasks import build_core_tasks
from tasks.niche_tasks import build_niche_tasks
from tasks.tune_up_tasks import build_tune_up_tasks
from services.flights import search_flights_oneway, search_flights_roundtrip, format_flight_options, pick_best_flights

from agents.core_agents import (
    destination_researcher,
    accommodation_planner,
    activities_planner,
    transport_planner,
    itinerary_coordinator,
    trip_verifier,
    local_insider,
)
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

load_dotenv()


# =====================================================
# AIRPORT SEARCH HELPER
# =====================================================
COMMON_AIRPORTS = {
    # ── Africa ──
    "NBO": "Nairobi, Kenya",
    "MBA": "Mombasa, Kenya",
    "KIS": "Kisumu, Kenya",
    "JNB": "Johannesburg, South Africa",
    "CPT": "Cape Town, South Africa",
    "DUR": "Durban, South Africa",
    "ADD": "Addis Ababa, Ethiopia",
    "DAR": "Dar es Salaam, Tanzania",
    "JRO": "Kilimanjaro, Tanzania",
    "ZNZ": "Zanzibar, Tanzania",
    "EBB": "Entebbe, Uganda",
    "KGL": "Kigali, Rwanda",
    "LOS": "Lagos, Nigeria",
    "ABV": "Abuja, Nigeria",
    "ACC": "Accra, Ghana",
    "CMN": "Casablanca, Morocco",
    "RAK": "Marrakech, Morocco",
    "TUN": "Tunis, Tunisia",
    "ALG": "Algiers, Algeria",
    "CAI": "Cairo, Egypt",
    "HRG": "Hurghada, Egypt",
    "SSH": "Sharm El Sheikh, Egypt",
    "LUN": "Lusaka, Zambia",
    "LVI": "Livingstone, Zambia",
    "HRE": "Harare, Zimbabwe",
    "VFA": "Victoria Falls, Zimbabwe",
    "MRU": "Mauritius",
    "SEZ": "Mahé, Seychelles",
    "TNR": "Antananarivo, Madagascar",
    "WDH": "Windhoek, Namibia",
    "GBE": "Gaborone, Botswana",
    "MQP": "Kruger Mpumalanga, South Africa",
    "DSS": "Dakar, Senegal",
    "ABJ": "Abidjan, Ivory Coast",
    "MPM": "Maputo, Mozambique",
    "BZV": "Brazzaville, Congo",
    "FIH": "Kinshasa, DR Congo",
    "LLW": "Lilongwe, Malawi",

    # ── Middle East ──
    "DXB": "Dubai, UAE",
    "AUH": "Abu Dhabi, UAE",
    "DOH": "Doha, Qatar",
    "RUH": "Riyadh, Saudi Arabia",
    "JED": "Jeddah, Saudi Arabia",
    "MCT": "Muscat, Oman",
    "BAH": "Bahrain",
    "KWI": "Kuwait City, Kuwait",
    "AMM": "Amman, Jordan",
    "TLV": "Tel Aviv, Israel",
    "IST": "Istanbul, Turkey",
    "AYT": "Antalya, Turkey",
    "SAW": "Istanbul Sabiha, Turkey",
    "ESB": "Ankara, Turkey",

    # ── Europe ──
    "LHR": "London Heathrow, UK",
    "LGW": "London Gatwick, UK",
    "STN": "London Stansted, UK",
    "LTN": "London Luton, UK",
    "MAN": "Manchester, UK",
    "EDI": "Edinburgh, UK",
    "BHX": "Birmingham, UK",
    "CDG": "Paris CDG, France",
    "ORY": "Paris Orly, France",
    "NCE": "Nice, France",
    "LYS": "Lyon, France",
    "MRS": "Marseille, France",
    "AMS": "Amsterdam, Netherlands",
    "FRA": "Frankfurt, Germany",
    "MUC": "Munich, Germany",
    "BER": "Berlin, Germany",
    "HAM": "Hamburg, Germany",
    "DUS": "Düsseldorf, Germany",
    "FCO": "Rome Fiumicino, Italy",
    "MXP": "Milan Malpensa, Italy",
    "VCE": "Venice, Italy",
    "NAP": "Naples, Italy",
    "FLR": "Florence, Italy",
    "MAD": "Madrid, Spain",
    "BCN": "Barcelona, Spain",
    "AGP": "Malaga, Spain",
    "PMI": "Palma de Mallorca, Spain",
    "SVQ": "Seville, Spain",
    "LIS": "Lisbon, Portugal",
    "OPO": "Porto, Portugal",
    "FAO": "Faro, Portugal",
    "ZRH": "Zurich, Switzerland",
    "GVA": "Geneva, Switzerland",
    "VIE": "Vienna, Austria",
    "PRG": "Prague, Czech Republic",
    "BUD": "Budapest, Hungary",
    "WAW": "Warsaw, Poland",
    "KRK": "Krakow, Poland",
    "CPH": "Copenhagen, Denmark",
    "OSL": "Oslo, Norway",
    "ARN": "Stockholm, Sweden",
    "HEL": "Helsinki, Finland",
    "DUB": "Dublin, Ireland",
    "BRU": "Brussels, Belgium",
    "ATH": "Athens, Greece",
    "SKG": "Thessaloniki, Greece",
    "JTR": "Santorini, Greece",
    "JMK": "Mykonos, Greece",
    "OTP": "Bucharest, Romania",
    "SOF": "Sofia, Bulgaria",
    "ZAG": "Zagreb, Croatia",
    "DBV": "Dubrovnik, Croatia",
    "SPU": "Split, Croatia",
    "LJU": "Ljubljana, Slovenia",
    "BEG": "Belgrade, Serbia",
    "TIA": "Tirana, Albania",
    "KEF": "Reykjavik, Iceland",
    "RIX": "Riga, Latvia",
    "VNO": "Vilnius, Lithuania",
    "TLL": "Tallinn, Estonia",

    # ── North America ──
    "JFK": "New York JFK, USA",
    "EWR": "Newark, USA",
    "LGA": "New York LaGuardia, USA",
    "LAX": "Los Angeles, USA",
    "SFO": "San Francisco, USA",
    "ORD": "Chicago O'Hare, USA",
    "MIA": "Miami, USA",
    "ATL": "Atlanta, USA",
    "DFW": "Dallas, USA",
    "DEN": "Denver, USA",
    "SEA": "Seattle, USA",
    "BOS": "Boston, USA",
    "IAD": "Washington Dulles, USA",
    "IAH": "Houston, USA",
    "MSP": "Minneapolis, USA",
    "DTW": "Detroit, USA",
    "PHX": "Phoenix, USA",
    "LAS": "Las Vegas, USA",
    "MCO": "Orlando, USA",
    "HNL": "Honolulu, USA",
    "SAN": "San Diego, USA",
    "PHL": "Philadelphia, USA",
    "YYZ": "Toronto, Canada",
    "YVR": "Vancouver, Canada",
    "YUL": "Montreal, Canada",
    "YOW": "Ottawa, Canada",
    "YYC": "Calgary, Canada",
    "MEX": "Mexico City, Mexico",
    "CUN": "Cancún, Mexico",
    "GDL": "Guadalajara, Mexico",
    "SJD": "Los Cabos, Mexico",

    # ── Central America & Caribbean ──
    "PTY": "Panama City, Panama",
    "SJO": "San José, Costa Rica",
    "GUA": "Guatemala City, Guatemala",
    "HAV": "Havana, Cuba",
    "MBJ": "Montego Bay, Jamaica",
    "KIN": "Kingston, Jamaica",
    "NAS": "Nassau, Bahamas",
    "PUJ": "Punta Cana, Dominican Republic",
    "SDQ": "Santo Domingo, Dominican Republic",
    "SXM": "St Maarten",
    "AUA": "Aruba",
    "BGI": "Barbados",
    "POS": "Port of Spain, Trinidad",

    # ── South America ──
    "GRU": "São Paulo, Brazil",
    "GIG": "Rio de Janeiro, Brazil",
    "EZE": "Buenos Aires, Argentina",
    "SCL": "Santiago, Chile",
    "BOG": "Bogotá, Colombia",
    "CTG": "Cartagena, Colombia",
    "MDE": "Medellín, Colombia",
    "LIM": "Lima, Peru",
    "CUZ": "Cusco, Peru",
    "UIO": "Quito, Ecuador",
    "MVD": "Montevideo, Uruguay",
    "CCS": "Caracas, Venezuela",
    "LPB": "La Paz, Bolivia",
    "ASU": "Asunción, Paraguay",

    # ── South Asia ──
    "DEL": "New Delhi, India",
    "BOM": "Mumbai, India",
    "BLR": "Bangalore, India",
    "MAA": "Chennai, India",
    "CCU": "Kolkata, India",
    "HYD": "Hyderabad, India",
    "GOI": "Goa, India",
    "COK": "Kochi, India",
    "CMB": "Colombo, Sri Lanka",
    "DAC": "Dhaka, Bangladesh",
    "KTM": "Kathmandu, Nepal",
    "ISB": "Islamabad, Pakistan",
    "KHI": "Karachi, Pakistan",
    "LHE": "Lahore, Pakistan",
    "MLE": "Malé, Maldives",

    # ── East & Southeast Asia ──
    "BKK": "Bangkok, Thailand",
    "CNX": "Chiang Mai, Thailand",
    "HKT": "Phuket, Thailand",
    "USM": "Koh Samui, Thailand",
    "SIN": "Singapore",
    "KUL": "Kuala Lumpur, Malaysia",
    "PEN": "Penang, Malaysia",
    "BKI": "Kota Kinabalu, Malaysia",
    "LGK": "Langkawi, Malaysia",
    "CGK": "Jakarta, Indonesia",
    "DPS": "Bali, Indonesia",
    "MNL": "Manila, Philippines",
    "CEB": "Cebu, Philippines",
    "HAN": "Hanoi, Vietnam",
    "SGN": "Ho Chi Minh City, Vietnam",
    "DAD": "Da Nang, Vietnam",
    "PNH": "Phnom Penh, Cambodia",
    "REP": "Siem Reap, Cambodia",
    "VTE": "Vientiane, Laos",
    "LPQ": "Luang Prabang, Laos",
    "RGN": "Yangon, Myanmar",
    "HKG": "Hong Kong",
    "TPE": "Taipei, Taiwan",

    # ── East Asia ──
    "NRT": "Tokyo Narita, Japan",
    "HND": "Tokyo Haneda, Japan",
    "KIX": "Osaka, Japan",
    "CTS": "Sapporo, Japan",
    "FUK": "Fukuoka, Japan",
    "OKA": "Okinawa, Japan",
    "ICN": "Seoul Incheon, South Korea",
    "GMP": "Seoul Gimpo, South Korea",
    "PUS": "Busan, South Korea",
    "PEK": "Beijing, China",
    "PVG": "Shanghai, China",
    "CAN": "Guangzhou, China",
    "SZX": "Shenzhen, China",
    "CTU": "Chengdu, China",
    "ULN": "Ulaanbaatar, Mongolia",

    # ── Oceania ──
    "SYD": "Sydney, Australia",
    "MEL": "Melbourne, Australia",
    "BNE": "Brisbane, Australia",
    "PER": "Perth, Australia",
    "ADL": "Adelaide, Australia",
    "CNS": "Cairns, Australia",
    "AKL": "Auckland, New Zealand",
    "CHC": "Christchurch, New Zealand",
    "ZQN": "Queenstown, New Zealand",
    "NAN": "Nadi, Fiji",
    "PPT": "Papeete, Tahiti",
    "APW": "Apia, Samoa",
    "NOU": "Nouméa, New Caledonia",
}

# String constants to avoid duplication
CUSTOM_DESTINATION = "Custom destination"
CLOSING_DIV = "</div>"
OPENING_ITINERARY_CARD = '<div class="itinerary-card">'
ITINERARY_VIEW_LABEL = "Smooth Landing view (formatted)"
EDIT_TEXT_LABEL = "#### Edit text (optional)"
PARIS_FRANCE = "Paris, France"


def _escape_dollars(text: str) -> str:
    """Escape $ signs so Streamlit markdown doesn't render them as LaTeX."""
    return text.replace("$", "\\$") if text else text


def search_airports(search_term: str):
    """Search airports by code or city name."""
    if not search_term:
        return []
    
    search_term_lower = search_term.lower()
    matches = []
    
    for code, city in COMMON_AIRPORTS.items():
        if search_term_lower in code.lower() or search_term_lower in city.lower():
            matches.append(f"{code} - {city}")
    
    return sorted(matches)


def parse_airport_selection(selection: str) -> str:
    """Extract IATA code from formatted selection (e.g., 'NBO - Nairobi, Kenya')."""
    if not selection:
        return ""
    return selection.split(" - ")[0]


def _pull_core_to_tune():
    """Callback to pull core itinerary into tune tab."""
    st.session_state.tune_itinerary = st.session_state.get("core_itinerary", "")


# =====================================================

def _run_niche_overlays(destination, budget, days, interests, profile_flags, start_date, passport_country, trip_purpose, home_airport, core_itinerary):
    """Generate niche overlays and store in session state."""
    if not core_itinerary.strip():
        st.error("Generate or paste a core itinerary first.")
        return

    with st.status("Layering in Smooth Landing extras…", expanded=False) as status:
        status.write("Preparing niche tasks based on your profile switches…")
        niche_tasks = build_niche_tasks(
            destination,
            budget,
            int(days),
            interests,
            profile_flags,
            start_date,
            passport_country,
            trip_purpose,
            home_airport,
            core_itinerary,
            airports=COMMON_AIRPORTS,
        )

        niche_agents = []
        if profile_flags["safari"]:
            niche_agents.append(safari_specialist)
        if profile_flags["halal"]:
            niche_agents.append(halal_travel_expert)
        if profile_flags["nomad"]:
            niche_agents.append(digital_nomad_planner)
        # safety agent always added (solo_female branch or general)
        niche_agents.append(solo_female_safety_advisor)
        if profile_flags["family"]:
            niche_agents.append(family_travel_designer)
        if profile_flags["medical"]:
            niche_agents.append(medical_tourism_planner)
        if profile_flags["luxury"]:
            niche_agents.append(luxury_on_budget_finder)
        if profile_flags["visa"] and passport_country.strip():
            niche_agents.append(visa_requirements_advisor)
        if profile_flags["flights"] and home_airport.strip():
            niche_agents.append(flight_advisor)

        if not niche_agents:
            status.update(
                label="No overlays selected.",
                state="error",
                expanded=False,
            )
            st.error("Please switch on at least one Smooth Landing profile above.")
        else:
            status.write("Calling in the specialists…")
            status.write("⏳ Spacing out requests to respect API rate limits (one specialist per second)…")
            
            # Add delay to prevent rate limiting on Groq API
            time.sleep(1)
            
            crew = Crew(
                agents=niche_agents,
                tasks=niche_tasks,
                verbose=False,
            )

            niche_result = crew.kickoff()
            niche_text = _to_text(niche_result)

            status.update(
                label="Smooth Landing overlays ready ✅",
                state="complete",
                expanded=False,
            )

            st.session_state.niche_itinerary = niche_text


def _to_text(result):
    """Best-effort helper to extract text from Crew.kickoff() result."""
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        if "raw" in result:
            return str(result["raw"])
        if "output" in result:
            return str(result["output"])
    return str(result)


# -------------------------
# PAGE CONFIG & THEME
# -------------------------

st.set_page_config(
    page_title="Smooth Landing AI",
    page_icon="smooth_landing_logo.png",  # uses your logo as tab icon
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #fff4e6 0%, #ffffff 30%);
    }
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        max-width: 1200px;
    }
    h1, h2, h3, h4 {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .travel-card {
        padding: 1.2rem 1.5rem;
        border-radius: 1rem;
        background-color: rgba(255, 255, 255, 0.96);
        border: 1px solid #ffe0b2;
    }

    /* Make input widgets solid and readable */
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDateInput input,
    .stTextArea textarea,
    .stSelectbox > div > div {
        background-color: #fffdf8 !important;
        border: 1px solid #f6a65a !important;
        color: #2c2c2c !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus,
    .stTextArea textarea:focus,
    .stSelectbox > div > div:focus {
        border: 1px solid #ff7a3c !important;
        box-shadow: 0 0 0 1px rgba(255, 122, 60, 0.4) !important;
    }

    ::placeholder {
        color: #9a7a5c !important;
        opacity: 1 !important;
    }

    /* Card around editable itinerary text areas */
    .itinerary-card {
        background: #fffdf8;
        border-radius: 16px;
        border: 1px solid #f6a65a;
        padding: 1rem 1.2rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        margin-bottom: 0.75rem;
    }

    /* Make the big editable areas feel like a notebook */
    .itinerary-card textarea {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        resize: vertical;
        font-family: "Georgia", "Times New Roman", serif;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .itinerary-card textarea:focus {
        outline: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# HEADER
# -------------------------

col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("smooth_landing_logo.png", output_format="PNG")
with col_title:
    st.title("Smooth Landing AI")
    st.caption("Gentle, safety‑smart trip planning so you arrive calm and confident.")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Plan a new trip", "Tune an existing trip", "Find flights"])

# -------------------------
# TAB 1: CORE PLANNING + ITERATION
# -------------------------
with tab1:
    st.subheader("Plan a new trip")
    st.caption("Shape a calm, coherent plan first, then layer Smooth Landing extras on top.")

    with st.container():
        st.markdown('<div class="travel-card">', unsafe_allow_html=True)
        st.markdown("#### Trip basics")

        col1, col2 = st.columns(2)
        with col1:
            # Destination - searchable from common airports
            airport_options = sorted(COMMON_AIRPORTS.values()) + [CUSTOM_DESTINATION]
            destination_display = st.selectbox(
                "Destination",
                options=airport_options,
                index=24,  # Paris by default
                key="dest_select_box",
                help="Select from popular destinations or choose 'Custom' to enter manually.",
            )
            
            if destination_display == CUSTOM_DESTINATION:
                new_destination = st.text_input(
                    "Enter custom destination",
                    PARIS_FRANCE,
                    key="new_dest",
                    help="City and country or region you want to explore.",
                )
            else:
                new_destination = destination_display
            
            new_start_date = st.date_input(
                "Start date",
                value=datetime.date.today(),
                key="new_start_date",
            )
            new_days = st.number_input(
                "Trip length (days)",
                min_value=1,
                max_value=10,
                value=4,
                key="new_days",
            )
        with col2:
            new_budget = st.number_input(
                "Total budget (USD)",
                min_value=100.0,
                value=2500.0,
                step=100.0,
                key="new_budget",
                help="Rough total for flights, stays, food, activities.",
            )
            new_interests = st.text_input(
                "Interests",
                "food, culture, museums",
                key="new_interests",
                help="What lights you up on a trip?",
            )
            new_traveller_type = st.selectbox(
                "Traveller type",
                ["solo female", "solo", "family", "group"],
                key="new_traveller_type",
            )

        st.markdown("##### Extra preferences")
        new_raw_preferences = st.text_area(
            "Anything we should know?",
            key="new_raw_prefs",
            placeholder="Mid‑range budget, hates hostels, loves food tours, avoid nightlife…",
        )

        will_fly = st.checkbox(
            "I’ll be flying to this destination",
            value=True,
            key="will_fly",
        )

        # Home airport - searchable selectbox
        airport_codes_with_cities = [f"{code} - {city}" for code, city in COMMON_AIRPORTS.items()]
        home_airport_selection = st.selectbox(
            "Home airport (IATA code)",
            options=airport_codes_with_cities,
            index=0,  # NBO first
            key="home_airport_select",
            help="Select your home airport for flight-aware planning.",
        )
        home_airport = parse_airport_selection(home_airport_selection)


        st.markdown("##### Traveller identity & visa context")
        col_id1, col_id2 = st.columns(2)
        with col_id1:
            passport_country = st.text_input(
                "Passport / nationality",
                "Kenya",
                key="passport_country",
                help="Country that issued your passport.",
            )
        with col_id2:
            trip_purpose = st.selectbox(
                "Trip purpose",
                ["tourism", "business", "study", "visiting friends/family"],
                key="trip_purpose",
            )

        st.markdown(CLOSING_DIV, unsafe_allow_html=True)

    st.markdown("---")

    # Initialize session state for core and niche itineraries
    if "core_itinerary" not in st.session_state:
        st.session_state.core_itinerary = ""
    if "niche_itinerary" not in st.session_state:
        st.session_state.niche_itinerary = ""

    col_core_header, col_core_button = st.columns([3, 1])
    with col_core_header:
        st.markdown("### Core itinerary")
        st.caption("This is your main Smooth Landing plan – clear, realistic, and easy to tweak.")
    with col_core_button:
        if st.button("Generate / regenerate core", key="btn_core", use_container_width=True):
            with st.status("Crafting your Smooth Landing route…", expanded=False) as status:
                status.write("Understanding your destination, dates, and style…")
                core_tasks = build_core_tasks(
                    new_destination,
                    new_budget,
                    int(new_days),
                    new_interests,
                    new_traveller_type,
                    new_raw_preferences,
                    new_start_date,
                    will_fly = will_fly,
                )

                core_agents = [
                    destination_researcher,
                    accommodation_planner,
                    activities_planner,
                    transport_planner,
                    itinerary_coordinator,
                    trip_verifier,
                    local_insider,
                ]

                status.write("Coordinating your Smooth Landing crew…")
                crew = Crew(
                    agents=core_agents,
                    tasks=core_tasks,
                    verbose=False,
                )

                core_result = crew.kickoff()
                core_text = _to_text(core_result)

                status.update(
                    label="Core itinerary ready ✅",
                    state="complete",
                    expanded=False,
                )

            st.session_state.core_itinerary = core_text

    # Core itinerary display + editable notebook
    if st.session_state.core_itinerary.strip():
        with st.expander(ITINERARY_VIEW_LABEL, expanded=True):
            st.markdown(_escape_dollars(st.session_state.core_itinerary), unsafe_allow_html=False)
    else:
        st.info("Generate a core itinerary to see your Smooth Landing view here.")

    st.markdown(EDIT_TEXT_LABEL)
    st.markdown(OPENING_ITINERARY_CARD, unsafe_allow_html=True)
    st.text_area(
        "",
        key="core_itinerary",
        height=320,
        placeholder="Your day‑by‑day Smooth Landing plan will appear here once you generate the core itinerary.",
        label_visibility="collapsed",
    )
    st.markdown(CLOSING_DIV, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # OVERLAYS SECTION — only show after core itinerary exists
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Add Smooth Landing overlays")
    
    if not st.session_state.core_itinerary.strip():
        st.info("Generate a core itinerary first, then come back here to add overlays.")
        # Default profile flags when no itinerary yet
        profile_flags = {
            "safari": False, "halal": False, "nomad": False, "solo_female": False,
            "family": False, "medical": False, "luxury": False, "visa": False, "flights": False,
        }
    else:
        st.caption("Now that you have a plan, pick the overlays that fit your style.")
        
        # Check if solo traveller (hide family/group options)
        is_solo = new_traveller_type in ["solo female", "solo"]
        
        # Check if African destination (for Safari option)
        african_keywords = [
            "kenya", "tanzania", "south africa", "botswana", "namibia", "zambia", "zimbabwe",
            "uganda", "rwanda", "ethiopia", "malawi", "mozambique", "madagascar", "mauritius",
            "seychelles", "zanzibar", "serengeti", "masai mara", "kruger", "okavango", "victoria falls",
            "nairobi", "cape town", "johannesburg", "dar es salaam", "kilimanjaro", "entebbe", "kigali",
            "addis ababa", "lusaka", "harare", "windhoek", "gaborone", "maputo", "antananarivo",
            "mombasa", "arusha", "livingstone", "maun", "kasane"
        ]
        dest_lower = new_destination.lower()
        is_african = any(kw in dest_lower for kw in african_keywords)
        
        # Build dynamic list of options to display
        options_to_show = []
        
        # Add options based on destination and traveler type
        if is_african:
            options_to_show.append(("Safari / East Africa", "safari"))
        options_to_show.append(("Halal-friendly", "halal"))
        options_to_show.append(("Digital nomad", "nomad"))
        options_to_show.append(("Solo female safety", "solo_female"))
        
        if not is_solo:
            options_to_show.append(("Family with kids", "family"))
        
        options_to_show.append(("Medical tourism", "medical"))
        options_to_show.append(("Luxury on a budget", "luxury"))
        options_to_show.append(("Visa & entry requirements", "visa"))
        options_to_show.append(("Flight advisor", "flights"))
        
        # Create columns dynamically - 3 items per row, no gaps
        profile_flags = {
            "safari": False, "halal": False, "nomad": False, "solo_female": False,
            "family": False, "medical": False, "luxury": False, "visa": False, "flights": False,
        }
        
        cols = st.columns(3)
        for idx, (label, key) in enumerate(options_to_show):
            col_idx = idx % 3
            with cols[col_idx]:
                profile_flags[key] = st.checkbox(label, key=f"new_{key}")

        if st.button("Run overlays on this itinerary", key="btn_niche", use_container_width=True):
            _run_niche_overlays(
                new_destination,
                new_budget,
                int(new_days),
                new_interests,
                profile_flags,
                new_start_date,
                passport_country,
                trip_purpose,
                home_airport,
                st.session_state.core_itinerary,
            )

    # Display niche overlays
    if st.session_state.niche_itinerary.strip():
        st.markdown("#### Smooth Landing overlay suggestions")
        with st.expander("View overlays (formatted)", expanded=True):
            st.markdown(_escape_dollars(st.session_state.niche_itinerary), unsafe_allow_html=False)
        st.caption("Copy any parts you like into your core itinerary above, then regenerate or tune.")


# -----------------------------
# TAB 2: ITINERARY TUNE‑UP FLOW
# -----------------------------
with tab2:
    st.subheader("Tune an existing trip")
    st.caption("Drop in any plan and Smooth Landing will gently stress‑test it, then add safety and comfort polish.")

    if "tune_itinerary" not in st.session_state:
        st.session_state.tune_itinerary = ""
    if "tune_result" not in st.session_state:
        st.session_state.tune_result = ""

    col_tune_top = st.columns([2, 1])
    with col_tune_top[0]:
        st.markdown("#### Your current plan")
    with col_tune_top[1]:
        st.button(
            "Use core itinerary from Tab 1",
            key="btn_pull_core",
            use_container_width=True,
            on_click=_pull_core_to_tune,
        )

    st.text_area(
        "Paste or edit your itinerary for tune‑up",
        height=300,
        placeholder="Day 1: Arrival and check‑in…",
        key="tune_itinerary",
    )

    st.markdown("#### Trip context")
    col_ct1, col_ct2, col_ct3 = st.columns(3)
    with col_ct1:
        # Tune destination with airport search
        tune_destination_display = st.selectbox(
            "Destination",
            options=sorted(COMMON_AIRPORTS.values()) + [CUSTOM_DESTINATION],
            index=24,  # Paris by default
            key="tune_dest_select",
        )
        
        if tune_destination_display == CUSTOM_DESTINATION:
            tune_destination = st.text_input(
                "Enter custom destination",
                PARIS_FRANCE,
                key="tune_dest_input",
            )
        else:
            tune_destination = tune_destination_display
    with col_ct2:
        tune_budget = st.number_input(
            "Approx total budget (USD)",
            min_value=100.0,
            value=2500.0,
            step=100.0,
            key="tune_budget",
        )
    with col_ct3:
        traveller_type = st.selectbox(
            "Who is travelling?",
            ["Solo female", "Solo", "Couple", "Family", "Group"],
            key="tune_traveller_type",
        )

    tune_start_date = st.date_input(
        "Trip start date",
        value=datetime.date.today(),
        key="tune_start_date",
    )

    tune_pro_safety = st.checkbox(
        "Include Smooth Landing Pro Safety review",
        value=True,
        key="tune_pro_safety",
    )

    st.write("")
    col_tune_btn = st.columns([3, 1])
    with col_tune_btn[1]:
        run_tune = st.button("Run tune‑up", key="btn_tune_up", use_container_width=True)

    if run_tune:
        if not st.session_state.tune_itinerary.strip():
            st.error("Please paste or pull in an itinerary first.")
        else:
            with st.status(
                "Reviewing and smoothing your itinerary…",
                expanded=False,
            ) as status:
                status.write("Summarising your plan and checking realism, flow, and budget…")
                tune_up_tasks = build_tune_up_tasks(
                    tune_destination,
                    tune_budget,
                    traveller_type,
                    st.session_state.tune_itinerary,
                    use_pro_safety=tune_pro_safety,
                    start_date=tune_start_date,
                )

                tune_agents = [trip_verifier, local_insider]
                if tune_pro_safety:
                    tune_agents.append(solo_female_safety_advisor)

                status.write("Adding Smooth Landing safety and comfort insights…")
                crew = Crew(
                    agents=tune_agents,
                    tasks=tune_up_tasks,
                    verbose=False,
                )

                result = crew.kickoff()
                result_text = _to_text(result)

                status.update(
                    label="Smooth Landing tune‑up complete ✅",
                    state="complete",
                    expanded=False,
                )

            st.success("Your trip just got a Smooth Landing ✨")
            st.markdown("#### Tuned‑up itinerary and notes")

            # Store result in a separate key to avoid widget binding conflict
            st.session_state.tune_result = result_text

            # Formatted view
            with st.expander(ITINERARY_VIEW_LABEL, expanded=True):
                st.markdown(_escape_dollars(st.session_state.tune_result), unsafe_allow_html=False)

            st.markdown(EDIT_TEXT_LABEL)
            st.markdown(OPENING_ITINERARY_CARD, unsafe_allow_html=True)
            st.text_area(
                "",
                value=st.session_state.tune_result,
                height=350,
                label_visibility="collapsed",
                disabled=True,
            )
            st.markdown(CLOSING_DIV, unsafe_allow_html=True)

    # Display existing tune result if it exists (when navigating back to tab)
    elif st.session_state.tune_result.strip():
        st.markdown("#### Previous tune‑up results")
        with st.expander(ITINERARY_VIEW_LABEL, expanded=True):
            st.markdown(_escape_dollars(st.session_state.tune_result), unsafe_allow_html=False)

        st.markdown(EDIT_TEXT_LABEL)
        st.markdown(OPENING_ITINERARY_CARD, unsafe_allow_html=True)
        st.text_area(
            "",
            value=st.session_state.tune_result,
            height=350,
            label_visibility="collapsed",
            disabled=True,
        )
        st.markdown(CLOSING_DIV, unsafe_allow_html=True)

# -----------------------------
# TAB 3: FLIGHT SEARCH (SKYSCANNER)
# -----------------------------
with tab3:
    st.subheader("Find flights for your Smooth Landing")
    st.caption("Quickly check a few flight options and prices for your trip dates.")

    trip_type = st.radio(
        "Trip type",
        ["One‑way", "Return"],
        horizontal=True,
        key="flight_trip_type",
    )

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        flight_origin_selection = st.selectbox(
            "From (airport)",
            options=airport_codes_with_cities,
            index=0,
            key="flight_origin_select",
        )
        flight_origin = parse_airport_selection(flight_origin_selection)
    with col_f2:
        flight_destination_selection = st.selectbox(
            "To (airport)",
            options=airport_codes_with_cities,
            index=24,  # Paris
            key="flight_destination_select",
            help="You can pick your trip destination here.",
        )
        flight_destination = parse_airport_selection(flight_destination_selection)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        flight_depart_date = st.date_input(
            "Departure date",
            value=st.session_state.get("new_start_date", datetime.date.today()),
            key="flight_depart_date",
        )
    with col_d2:
        flight_adults = st.number_input(
            "Adults",
            min_value=1,
            max_value=9,
            value=1,
            step=1,
            key="flight_adults",
        )

    return_date = None
    if trip_type == "Return":
        return_date = st.date_input(
            "Return date",
            value=flight_depart_date,
            key="flight_return_date",
        )

    st.caption("Skyscanner data is indicative only – always confirm details and prices before booking.")

    if st.button("Search flights", key="btn_search_flights"):
        if not flight_origin or not flight_destination:
            st.error("Please enter both origin and destination (IATA codes work best, e.g. NBO, CDG).")
        else:
            with st.status("Checking Skyscanner for options…", expanded=False) as status:
                try:
                    if trip_type == "Return" and return_date:
                        # Search round-trip
                        flight_results = search_flights_roundtrip(
                            origin=flight_origin,
                            destination=flight_destination,
                            outbound_date=flight_depart_date,
                            return_date=return_date,
                            adults=int(flight_adults),
                        )
                        outbound_options = flight_results.get("outbound", [])
                        inbound_options = flight_results.get("return", [])
                    else:
                        # Search one-way only
                        outbound_options = search_flights_oneway(
                            origin=flight_origin,
                            destination=flight_destination,
                            date=flight_depart_date,
                            adults=int(flight_adults),
                        )
                        inbound_options = []
                except Exception as e:
                    status.update(
                        label="Flight search failed",
                        state="error",
                        expanded=True,
                    )
                    st.error(f"Could not fetch flights right now: {e}")
                else:
                    status.update(
                        label="Flight options ready ✅",
                        state="complete",
                        expanded=False,
                    )

                    # Display outbound flights
                    if not outbound_options or (isinstance(outbound_options, dict) and "error" in outbound_options):
                        st.warning("No outbound flights found. Try different dates or airports.")
                    else:
                        st.markdown("### ✈️ Outbound flights")

                        # Show top picks
                        picks = pick_best_flights(outbound_options)
                        pick_cols = st.columns(3)
                        for col, key in zip(pick_cols, ["best", "cheapest", "shortest"]):
                            p = picks[key]
                            if p:
                                with col:
                                    stops_label = "Non-stop" if p.get("stops", 0) == 0 else f"{p['stops']} stop(s)"
                                    st.metric(
                                        label=p["tag"],
                                        value=f"${p.get('price', 'N/A')}",
                                        delta=f"{p.get('duration_minutes', '?')} min · {stops_label}",
                                        delta_color="off",
                                    )
                                    st.caption(f"{p.get('airline', '')} · {p.get('departure', '')} → {p.get('arrival', '')}")
                                    if p.get("deeplink"):
                                        st.link_button("Book", p["deeplink"], key=f"pick_out_{key}")
                        st.divider()

                        # Full list
                        with st.expander("All outbound options", expanded=False):
                            for i, opt in enumerate(outbound_options, start=1):
                                col1, col2, col3 = st.columns([2, 2, 1])
                                with col1:
                                    st.markdown(f"**{opt.get('airline', 'Airline')}**")
                                with col2:
                                    st.markdown(f"{opt.get('departure', 'N/A')} → {opt.get('arrival', 'N/A')}")
                                with col3:
                                    st.markdown(f"**{opt.get('currency', '')} {opt.get('price', 'N/A')}**")
                                st.caption(f"{opt.get('duration_minutes', 'N/A')} min • {opt.get('stops', 0)} stop(s)")
                                if opt.get("deeplink"):
                                    st.link_button("Book on Skyscanner", opt["deeplink"], key=f"out_{i}")
                                st.divider()

                    # Display return flights if round-trip
                    if trip_type == "Return":
                        if not inbound_options or (isinstance(inbound_options, dict) and "error" in inbound_options):
                            st.info("No return flights found for the chosen date. You can still book a one‑way outbound.")
                        else:
                            st.markdown("### ✈️ Return flights")

                            # Show top picks
                            ret_picks = pick_best_flights(inbound_options)
                            ret_cols = st.columns(3)
                            for col, key in zip(ret_cols, ["best", "cheapest", "shortest"]):
                                p = ret_picks[key]
                                if p:
                                    with col:
                                        stops_label = "Non-stop" if p.get("stops", 0) == 0 else f"{p['stops']} stop(s)"
                                        st.metric(
                                            label=p["tag"],
                                            value=f"${p.get('price', 'N/A')}",
                                            delta=f"{p.get('duration_minutes', '?')} min · {stops_label}",
                                            delta_color="off",
                                        )
                                        st.caption(f"{p.get('airline', '')} · {p.get('departure', '')} → {p.get('arrival', '')}")
                                        if p.get("deeplink"):
                                            st.link_button("Book", p["deeplink"], key=f"pick_ret_{key}")
                            st.divider()

                            # Full list
                            with st.expander("All return options", expanded=False):
                                for i, opt in enumerate(inbound_options, start=1):
                                    col1, col2, col3 = st.columns([2, 2, 1])
                                    with col1:
                                        st.markdown(f"**{opt.get('airline', 'Airline')}**")
                                    with col2:
                                        st.markdown(f"{opt.get('departure', 'N/A')} → {opt.get('arrival', 'N/A')}")
                                    with col3:
                                        st.markdown(f"**{opt.get('currency', '')} {opt.get('price', 'N/A')}**")
                                    st.caption(f"{opt.get('duration_minutes', 'N/A')} min • {opt.get('stops', 0)} stop(s)")
                                    if opt.get("deeplink"):
                                        st.link_button("Book on Skyscanner", opt["deeplink"], key=f"ret_{i}")
                                    st.divider()
