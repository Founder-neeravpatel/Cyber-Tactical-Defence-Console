import aiohttp
import asyncio
from config import ADSB_API_URL, MILITARY_CALLSIGNS, PRIORITY_SQUAWKS

class GeoIntelTracker:
    def __init__(self):
        self.api_url = ADSB_API_URL
        self.last_cache = []

    async def fetch_military_aircrafts(self):
        events = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, timeout=3) as response:
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

                            if lat and lon:
                                region = "GLOBAL"
                                if 8.0 <= lat <= 37.0 and 68.0 <= lon <= 97.0:
                                    region = "INDIA"
                                elif 23.5 <= lat <= 37.0 and 60.5 <= lon <= 77.0:
                                    region = "PAKISTAN"

                                is_priority = any(c in callsign for c in MILITARY_CALLSIGNS) or squawk in PRIORITY_SQUAWKS or region != "GLOBAL"
                                events.append({
                                    "callsign": callsign if callsign else "MIL_RECON",
                                    "type": t_type,
                                    "lat": lat,
                                    "lon": lon,
                                    "alt": alt,
                                    "speed": gs,
                                    "squawk": squawk,
                                    "priority": is_priority,
                                    "region": region
                                })
        except Exception:
            pass

        if events:
            self.last_cache = events
        return self.last_cache
