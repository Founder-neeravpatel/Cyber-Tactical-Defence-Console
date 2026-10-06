import aiohttp
import asyncio
from datetime import datetime

class TelegramSigintScraper:
    def __init__(self):
        self.seen_exploits = set()
        self.index = 0

    async def initialize(self):
        pass

    async def fetch_latest_sigint_events(self):
        events = []
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 1. Real Live Ransomware Leak Stream
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.ransomware.live/v2/recentattacks", timeout=2.5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if self.index < len(data):
                            item = data[self.index]
                            self.index += 1
                            group = item.get('group_name', 'LockBit')
                            title = item.get('post_title', 'Exfiltration')[:40]
                            post_id = f"{group}_{title}"
                            
                            if post_id not in self.seen_exploits:
                                self.seen_exploits.add(post_id)
                                events.append({
                                    "timestamp": timestamp,
                                    "channel": "@RansomwareLive",
                                    "keyword": "RANSOMWARE",
                                    "severity": "CRITICAL",
                                    "raw_text": f"[REAL LEAK] {group} -> {title}"
                                })
        except Exception:
            pass

        # 2. Real Live CISA KEV Engine
        if not events:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", timeout=2.5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            vulns = data.get("vulnerabilities", [])
                            if vulns:
                                import random
                                item = random.choice(vulns[-50:])
                                cve = item.get("cveID", "CVE-2026")
                                vendor = item.get("vendorProject", "Core")
                                name = item.get("vulnerabilityName", "Exploit")[:30]
                                
                                if cve not in self.seen_exploits:
                                    self.seen_exploits.add(cve)
                                    events.append({
                                        "timestamp": timestamp,
                                        "channel": "@CISA_KEV",
                                        "keyword": "EXPLOIT",
                                        "severity": "CRITICAL",
                                        "raw_text": f"[REAL EXPLOIT] {cve} ({vendor}): {name}"
                                    })
            except Exception:
                pass

        if len(self.seen_exploits) > 200:
            self.seen_exploits.clear()

        return events
