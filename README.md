# Smooth Landing AI - Safety-Smart Trip Planning

**Smooth Landing AI** is an intelligent travel planning assistant that helps you create calm, coherent itineraries with built-in safety considerations. It uses CrewAI agents to orchestrate a team of specialized travel advisors—from destination researchers to solo female safety experts—all working together to craft your perfect trip.

## Features

### Core Planning
- **Destination Research**: Smart analysis of your chosen destination
- **Accommodation Planning**: Budget-friendly recommendations matched to your style
- **Activities Customization**: Personalized activity suggestions based on interests
- **Transport Coordination**: Seamless local transportation guidance
- **Itinerary Coordination**: Professional-grade day-by-day planning
- **Trip Verification**: Safety and feasibility checks
- **Local Insights**: Authentic neighborhood recommendations

### Smooth Landing Overlays (Optional Layers)
Activate specialized advisors based on your travel profile:

- **Safari / East Africa Expert**: Specialized recommendations for East African safaris
- **Halal-Friendly Travel**: Curated halal dining and cultural considerations
- **Digital Nomad Planner**: Work-friendly accommodations and co-spaces
- **Solo Female Safety Advisor**: Comprehensive safety guidance (activated by default; automatic when "Solo female" is selected)
- **Family Travel Designer**: Kid-friendly activities and family-safe routes
- **Medical Tourism Planner**: Healthcare facility recommendations
- **Luxury on a Budget Finder**: High-end experiences at reasonable prices
- **Visa & Entry Requirements**: Passport-specific visa and entry documentation
- **Flight Advisor**: Find and book flights with real-time Skyscanner integration

### Additional Features
- **Itinerary Tuning**: Refine existing itineraries with new dates, budgets, or styles
- **Editable Plans**: Edit and customize generated itineraries directly in the app
- **Flight Search**: Integrated flight search across the "Find flights" tab
- **Airport Selection**: Searchable database of 50+ major international airports

---

## Requirements

- **Python**: 3.12.7 or higher
- **Operating System**: macOS, Linux, or Windows
- **Package Manager**: pip or conda
- **LLM Access**: Groq API key (free tier available)
- **External APIs**:
  - Skyscanner API key (for flight search)
  - SerperDev API key (for web search)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yvonnewangui/smooth_landing.git
cd smooth_landing
```

### 2. Set Up Python Environment

#### Using Virtual Environment (Recommended)
```bash
# Create venv
python3.12 -m venv venv

# Activate venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

#### Using Conda
```bash
conda create -n smooth_landing python=3.12.7
conda activate smooth_landing
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `streamlit` - Web UI framework
- `crewai` - Multi-agent orchestration
- `crewai-tools` - Extended tools library
- `groq` - LLM integration (llama-3.3-70b)
- `python-dotenv` - Environment variable management
- `requests` - HTTP client for API calls

---

## Configuration

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
cp .env.example .env  # if template provided
# or create manually
nano .env
```

### 2. Add Required API Keys

```env
# Groq LLM (required)
# Get free key at: https://console.groq.com
GROQ_API_KEY=your_groq_api_key_here

# Skyscanner API (for flight search)
# Get key at: https://rapidapi.com/skyscanner/api/skyscanner-api/
SKYSCANNER_API_KEY=your_skyscanner_key_here

# SerperDev (for web search)
# Get key at: https://serper.dev
SERPER_API_KEY=your_serper_key_here
```

### 3. Verify Configuration

```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Groq Key:', 'loaded' if os.getenv('GROQ_API_KEY') else 'MISSING')"
```

---

## Running the Application

### Start the Streamlit Server

```bash
streamlit run app.py
```

The application will open automatically in your default browser at `http://localhost:8501`

### Access Different Tabs

1. **Plan a new trip** - Create a new itinerary from scratch
2. **Tune an existing trip** - Refine an existing itinerary
3. **Find flights** - Search and book flights

---

## Project Structure

```
travel_ninja/
├── app.py                      # Main Streamlit application
├── main.py                     # Alternative entry point
├── tools.py                    # CrewAI tool definitions (flight search, web search)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this file)
├── smooth_landing_logo.png     # App logo
│
├── agents/
│   ├── __init__.py
│   ├── core_agents.py         # 8 core planning agents
│   └── niche_agents.py        # 9 specialized niche agents
│
├── services/
│   └── flights.py             # Flight search service (Skyscanner integration)
│
├── tasks/
│   ├── __init__.py
│   ├── core_tasks.py          # 8 core itinerary generation tasks
│   ├── niche_tasks.py         # 9 niche overlay tasks
│   └── tune_up_tasks.py       # Itinerary tuning tasks
│
└── __pycache__/               # Python cache (auto-generated)
```

---

## Usage Guide

### Planning a New Trip

1. **Go to "Plan a new trip" tab**
2. **Fill in trip basics:**
   - Destination (searchable from 50+ airports)
   - Start date
   - Trip length (days)
   - Total budget
   - Interests (comma-separated)
   - Traveller type (solo, family, group)

3. **Add extra preferences** (optional):
   - Any special notes about your style or requirements

4. **Set up flight context:**
   - Check "I'll be flying to this destination" if applicable
   - Select your home airport
   - Select trip purpose

5. **Select profile layers:**
   - Toggle any Smooth Landing profiles that match your trip
   - Note: "Solo female safety" automatically disables family/group options
   - Note: Solo female advisor is always active (general or specialized)

6. **Click "Generate / regenerate core"** to create your base itinerary

7. **Review and edit** the generated itinerary in the editable text area

8. **Click "Run overlays"** to add specialized recommendations if you toggled any profiles

### Tuning an Existing Trip

1. **Go to "Tune an existing trip" tab**
2. **Paste or clear** your existing itinerary
3. **Adjust parameters** (destination, budget, dates, etc.)
4. **Click "Tune this itinerary"** to regenerate with new parameters
5. **Review results** in the formatted view

### Finding Flights

1. **Go to "Find flights" tab**
2. **One-way flight:**
   - Select origin and destination airports
   - Choose departure date
   - Click "Search one-way" to get options
3. **Round-trip flight:**
   - Select origin and destination airports
   - Choose departure and return dates
   - Click "Search round-trip" for options

---

## API Integration Details

### Groq (LLM)
- **Model**: llama-3.3-70b-versatile
- **Purpose**: Powers all agent reasoning and writing
- **Free Tier**: 30 requests/minute (sufficient for interactive use)
- **Sign Up**: https://console.groq.com

### Skyscanner (Flight Search)
- **Purpose**: Real-time flight availability and pricing
- **Required for**: Flight advisor overlay and flight search tab
- **Integration**: Via RapidAPI
- **Sign Up**: https://rapidapi.com/skyscanner/api/skyscanner-api/

### SerperDev (Web Search)
- **Purpose**: General web search for destination research
- **Required for**: Destination researcher and other research agents
- **Sign Up**: https://serper.dev

---

## Troubleshooting

### Issue: "API key not found" Error

**Solution**: Verify your `.env` file is in the project root and contains all required keys.

```bash
# Check file exists
ls -la .env

# Verify keys are set
cat .env | grep GROQ_API_KEY
```

### Issue: Streamlit Won't Start

**Solution**: Ensure virtual environment is activated and dependencies installed.

```bash
# Activate venv
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Start again
streamlit run app.py
```

### Issue: "Token limit exceeded" on Generation

**Solution**: Reduce trip complexity or use a larger model:
- Shorten interests description
- Simplify preferences
- The app automatically uses llama-3.3-70b (70B parameters) for capacity

### Issue: Flight Search Returns No Results

**Possible causes**:
- Skyscanner API key is invalid or rate-limited
- Destination airport code is incorrect
- Date is in the past
- Verify airport codes at [IATA codes](https://www.world-airport-codes.com/)

### Issue: "Solo female safety" Hides Family Toggle

**This is intentional!** Solo female travel and family travel are mutually exclusive. When you toggle "Solo female safety," the family option is hidden to prevent conflicting recommendations.

---

## Environment Variables Reference

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| `GROQ_API_KEY` | Yes | LLM access | `gsk_xxxxx...` |
| `SKYSCANNER_API_KEY` | No* | Flight search | `xxx_api_key_xxx` |
| `SERPER_API_KEY` | No* | Web search | `xxx_serper_key_xxx` |

*Optional unless using that specific feature

---

## Development

### Adding a New Agent

1. Define agent in `agents/core_agents.py` or `agents/niche_agents.py`
2. Create corresponding tasks in `tasks/core_tasks.py` or `tasks/niche_tasks.py`
3. Add tools to `tools.py` if needed
4. Reference agent in `app.py` UI logic

### Adding a New API Integration

1. Create a new file in `services/` (e.g., `services/hotels.py`)
2. Implement API wrapper function
3. Create tool wrapper in `tools.py` using `BaseTool` class
4. Register in agent tool list
5. Add to app UI

---

## Performance Optimization Tips

1. **Use the "Edit text" option** to refine itineraries instead of regenerating
2. **Keep preferences concise** to reduce token usage
3. **Reuse destination research** for multiple trip variations
4. **Disable unused layers** to speed up overlay generation

---

## Support & Feedback

For issues, questions, or feature requests, please open an issue on GitHub:
- GitHub: https://github.com/yvonnewangui/smooth_landing
- Report Issues: https://github.com/yvonnewangui/smooth_landing/issues

---

## License

[Specify your license - MIT, Apache 2.0, etc.]

---

## Acknowledgments

Built with:
- **CrewAI** - Multi-agent framework
- **Streamlit** - Web interface
- **Groq** - LLM inference
- **Skyscanner** - Flight data
- **SerperDev** - Web search

---

**Last Updated**: February 2026  
**Version**: 1.0  
**Status**: Active Development
