import datetime
import streamlit as st
from crewai import Crew
from dotenv import load_dotenv

from tasks.core_tasks import build_core_tasks
from tasks.niche_tasks import build_niche_tasks
from tasks.tune_up_tasks import build_tune_up_tasks

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
)

load_dotenv()


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

tab1, tab2 = st.tabs(["Plan a new trip", "Tune an existing trip"])


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
            new_destination = st.text_input(
                "Destination",
                "Paris, France",
                key="new_dest",
                help="City and country or region you want to explore.",
            )
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

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("#### Optional Smooth Landing profile")
    st.caption("Flip on the layers that help your arrival feel extra smooth and safe.")

    col_n1, col_n2, col_n3 = st.columns(3)
    with col_n1:
        new_safari = st.toggle("Safari / East Africa", key="new_safari")
        new_halal = st.toggle("Halal‑friendly", key="new_halal")
    with col_n2:
        new_nomad = st.toggle("Digital nomad", key="new_nomad")
        new_solo_f = st.toggle("Solo female safety", key="new_solo_f")
    with col_n3:
        new_family = st.toggle("Family with kids", key="new_family")
        new_medical = st.toggle("Medical tourism", key="new_medical")
    new_luxury = st.toggle("Luxury on a budget", key="new_luxury")
    new_visa = st.toggle("Visa & entry requirements", key="new_visa")

    profile_flags = {
        "safari": new_safari,
        "halal": new_halal,
        "nomad": new_nomad,
        "solo_female": new_solo_f,
        "family": new_family,
        "medical": new_medical,
        "luxury": new_luxury,
        "visa": new_visa,
    }

    st.markdown("---")

    # Initialize session state for core itinerary
    if "core_itinerary" not in st.session_state:
        st.session_state.core_itinerary = ""

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
        with st.expander("Smooth Landing view (formatted)", expanded=True):
            st.markdown(st.session_state.core_itinerary, unsafe_allow_html=False)
    else:
        st.info("Generate a core itinerary to see your Smooth Landing view here.")

    st.markdown("#### Edit text (optional)")
    st.markdown('<div class="itinerary-card">', unsafe_allow_html=True)
    st.text_area(
        "",
        key="core_itinerary",
        height=320,
        placeholder="Your day‑by‑day Smooth Landing plan will appear here once you generate the core itinerary.",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Add Smooth Landing overlays")
    st.caption("Run a lighter pass to add extra calm – safety, halal options, family tweaks, visa notes and more.")

    if st.button("Run overlays on this itinerary", key="btn_niche", use_container_width=True):
        if not st.session_state.core_itinerary.strip():
            st.error("Generate or paste a core itinerary first.")
        else:
            with st.status("Layering in Smooth Landing extras…", expanded=False) as status:
                status.write("Preparing niche tasks based on your profile switches…")
                niche_tasks = build_niche_tasks(
                    new_destination,
                    new_budget,
                    int(new_days),
                    new_interests,
                    profile_flags,
                    new_start_date,
                    passport_country,
                    trip_purpose,
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

                if not niche_agents:
                    status.update(
                        label="No overlays selected.",
                        state="error",
                        expanded=False,
                    )
                    st.error("Please switch on at least one Smooth Landing profile above.")
                else:
                    status.write("Calling in the specialists…")
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

                    st.markdown("#### Smooth Landing overlay suggestions")
                    with st.expander("View overlays (formatted)", expanded=True):
                        st.markdown(niche_text, unsafe_allow_html=False)
                    st.caption("Copy any parts you like into your core itinerary above, then regenerate or tune.")


# -----------------------------
# TAB 2: ITINERARY TUNE‑UP FLOW
# -----------------------------
with tab2:
    st.subheader("Tune an existing trip")
    st.caption("Drop in any plan and Smooth Landing will gently stress‑test it, then add safety and comfort polish.")

    if "tune_itinerary" not in st.session_state:
        st.session_state.tune_itinerary = ""

    col_tune_top = st.columns([2, 1])
    with col_tune_top[0]:
        st.markdown("#### Your current plan")
    with col_tune_top[1]:
        if st.button("Use core itinerary from Tab 1", key="btn_pull_core", use_container_width=True):
            st.session_state.tune_itinerary = st.session_state.get("core_itinerary", "")

    st.text_area(
        "Paste or edit your itinerary for tune‑up",
        height=300,
        placeholder="Day 1: Arrival and check‑in…",
        key="tune_itinerary",
    )

    st.markdown("#### Trip context")
    col_ct1, col_ct2, col_ct3 = st.columns(3)
    with col_ct1:
        tune_destination = st.text_input(
            "Destination",
            "Paris, France",
            key="tune_dest",
        )
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

            st.session_state.tune_itinerary = result_text

            # Formatted view
            with st.expander("Smooth Landing view (formatted)", expanded=True):
                st.markdown(st.session_state.tune_itinerary, unsafe_allow_html=False)

            st.markdown("#### Edit text (optional)")
            st.markdown('<div class="itinerary-card">', unsafe_allow_html=True)
            st.text_area(
                "",
                key="tune_itinerary",
                height=350,
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)
