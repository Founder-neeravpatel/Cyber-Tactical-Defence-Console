# modules/geo_tracker.py
import aiohttp
import asyncio
from config import ADSB_API_URL, MILITARY_CALLSIGNS, PRIORITY_SQUAWKS

class GeoIntelTracker:
    def __init__(self):
        self.api_url = ADSB_API_URL

    async def fetch_military_aircrafts(self):
        """Fetch real-time military flight tracking data."""
        events = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        aircrafts = data.get("ac", [])
                        
                        for ac in aircrafts:
                            callsign = ac.get("flight", "").strip()
                            squawk = str(ac.get("squawk", "")).strip()
                            lat = ac.get("lat")
                            lon = ac.get("lon")
                            alt = ac.get("alt_baro", "N/A")
                            gs = ac.get("gs", "N/A")
                            t_type = ac.get("t", "MIL")

                            # Filter for specific high-priority military assets or squawk codes
                            is_priority = any(c in callsign for c in MILITARY_CALLSIGNS) or squawk in PRIORITY_SQUAWKS
                            
                            if lat and lon:
                                events.append({
                                    "callsign": callsign if callsign else "UNKNOWN_MIL",
                                    "type": t_type,
                                    "lat": lat,
                                    "lon": lon,
                                    "alt": alt,
                                    "speed": gs,
                                    "squawk": squawk,
                                    "priority": is_priority
                                })
        except Exception as e:
            events.append({"error": f"ADS-B Feed Connection Error: {str(e)}"})
            
        return events