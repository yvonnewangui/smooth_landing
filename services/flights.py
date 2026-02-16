import os
import requests
from datetime import datetime, timedelta

SKYSCANNER_API_HOST = os.getenv("SKYSCANNER_API_HOST", "flights-sky.p.rapidapi.com")
SKYSCANNER_API_KEY = os.getenv("SKYSCANNER_API_KEY")


def search_flights_oneway(origin, destination, date, adults=1, currency="USD"):
    """
    Search one-way flights using Skyscanner API.
    
    Args:
        origin (str): Departure airport IATA code (e.g., 'NBO', 'CDG')
        destination (str): Arrival airport IATA code
        date (datetime.date or str): Departure date in YYYY-MM-DD format
        adults (int): Number of adult passengers
        currency (str): Currency code (default: USD)
    
    Returns:
        list: List of flight options with airline, times, duration, stops, price, deeplink
    """
    if not SKYSCANNER_API_KEY:
        raise RuntimeError("SKYSCANNER_API_KEY not set in environment")

    # Convert date to string if needed
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = str(date)

    # Validate: don't search for past dates — bump to tomorrow
    try:
        search_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        if search_date < today:
            date_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif search_date == today and datetime.now().hour >= 18:
            # Same day but evening — most flights already departed
            date_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    except ValueError:
        pass  # If date parsing fails, let the API handle it

    url = f"https://{SKYSCANNER_API_HOST}/api/v1/flights/search-oneway"
    headers = {
        "x-rapidapi-key": SKYSCANNER_API_KEY,
        "x-rapidapi-host": SKYSCANNER_API_HOST,
    }
    params = {
        "fromEntityId": origin,
        "toEntityId": destination,
        "departDate": date_str,
        "adults": adults,
        "currency": currency,
        "cabinClass": "economy",
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Flight search failed: {str(e)}", "results": []}

    # Parse results
    results = []
    itineraries = data.get("itineraries", [])[:5]  # Top 5 options
    for it in itineraries:
        legs = it.get("legs", [])
        if not legs:
            continue
        leg = legs[0]
        price = it.get("price", {})
        
        try:
            results.append(
                {
                    "airline": ", ".join({s.get("marketingCarrier", "Unknown") for s in leg.get("segments", [])}),
                    "departure": leg.get("departure", "N/A"),
                    "arrival": leg.get("arrival", "N/A"),
                    "duration_minutes": leg.get("durationInMinutes", "N/A"),
                    "stops": len(leg.get("segments", [])) - 1,
                    "price": price.get("amount", "N/A"),
                    "currency": price.get("currencyCode", currency),
                    "deeplink": it.get("deeplink", ""),
                }
            )
        except Exception as e:
            continue
    
    return results


def search_flights_roundtrip(origin, destination, outbound_date, return_date, adults=1, currency="USD"):
    """
    Search round-trip flights (outbound + return).
    
    Args:
        origin (str): Departure airport IATA code
        destination (str): Arrival airport IATA code
        outbound_date (datetime.date or str): Outbound departure date (YYYY-MM-DD)
        return_date (datetime.date or str): Return departure date (YYYY-MM-DD)
        adults (int): Number of adult passengers
        currency (str): Currency code (default: USD)
    
    Returns:
        dict: Contains 'outbound' and 'return' flight options
    """
    if not SKYSCANNER_API_KEY:
        raise RuntimeError("SKYSCANNER_API_KEY not set in environment")
    
    # Search both directions
    outbound_results = search_flights_oneway(origin, destination, outbound_date, adults, currency)
    return_results = search_flights_oneway(destination, origin, return_date, adults, currency)
    
    return {
        "outbound": outbound_results,
        "return": return_results,
        "summary": {
            "route": f"{origin} → {destination} → {origin}",
            "outbound_date": str(outbound_date),
            "return_date": str(return_date),
            "adults": adults,
            "outbound_options": len(outbound_results) if isinstance(outbound_results, list) else 0,
            "return_options": len(return_results) if isinstance(return_results, list) else 0,
        }
    }


def format_flight_options(flights, direction="outbound"):
    """
    Format flight results for display.
    
    Args:
        flights (list): Flight options from search_flights_oneway
        direction (str): 'outbound' or 'return' for context
    
    Returns:
        str: Formatted flight information
    """
    if not flights or (isinstance(flights, dict) and "error" in flights):
        return f"No {direction} flights found."
    
    output = f"\n### {direction.upper()} FLIGHTS\n"
    for i, flight in enumerate(flights, 1):
        stops_text = f"{flight['stops']} stop{'s' if flight['stops'] != 1 else ''}" if flight['stops'] > 0 else "Non-stop"
        output += (
            f"\n**Option {i}:**\n"
            f"- Airline: {flight.get('airline', 'Unknown')}\n"
            f"- Departure: {flight.get('departure', 'N/A')}\n"
            f"- Arrival: {flight.get('arrival', 'N/A')}\n"
            f"- Duration: {flight.get('duration_minutes', 'N/A')} minutes\n"
            f"- {stops_text}\n"
            f"- Price: {flight.get('currency', '')} {flight.get('price', 'N/A')}\n"
        )
        if flight.get('deeplink'):
            output += f"- [Book here]({flight['deeplink']})\n"
    
    return output


def pick_best_flights(flights):
    """
    From a list of flight options, pick the best, cheapest, and shortest.

    Returns:
        dict with keys 'best', 'cheapest', 'shortest' — each a flight dict
        with an added 'tag' field, or None if no valid flights.
        Flights may overlap (e.g. cheapest may also be shortest).
    """
    if not flights or isinstance(flights, dict):
        return {"best": None, "cheapest": None, "shortest": None}

    valid = [f for f in flights if _safe_num(f.get("price")) is not None]
    if not valid:
        return {"best": None, "cheapest": None, "shortest": None}

    cheapest = min(valid, key=lambda f: _safe_num(f["price"]))
    shortest = min(valid, key=lambda f: _safe_num(f.get("duration_minutes"), 99999))

    # "Best" = fewest stops first, then shortest duration, then cheapest
    best = min(valid, key=lambda f: (
        f.get("stops", 99),
        _safe_num(f.get("duration_minutes"), 99999),
        _safe_num(f["price"]),
    ))

    return {
        "best": {**best, "tag": "🏆 Best"},
        "cheapest": {**cheapest, "tag": "💰 Cheapest"},
        "shortest": {**shortest, "tag": "⚡ Shortest"},
    }


def _safe_num(val, default=None):
    """Safely convert a value to float, returning default on failure."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
