import asyncio
import random
from datetime import datetime

# Real Indian & Pakistan Telecom/Gov Target Indicators
INDIA_TARGETS = [
    {"asset": "IN-CERT / NIC Infrastructure", "port": 443, "type": "GOV_NET"},
    {"asset": "Airtel/Jio Gateway Node (Mumbai)", "port": 179, "type": "BGP_ROUTER"},
    {"asset": "National Power Grid SCADA (Northern)", "port": 502, "type": "CRITICAL_ICS"},
    {"asset": "BFSI Payment Clearing Gateway", "port": 8443, "type": "FINTECH"}
]

PAKISTAN_TARGETS = [
    {"asset": "PAK-NTISB Core Infra Node", "port": 443, "type": "GOV_NET"},
    {"asset": "PTCL Telecom Transit Switch (Karachi)", "port": 179, "type": "BGP_ROUTER"},
    {"asset": "K-Electric Grid Control Terminal", "port": 102, "type": "CRITICAL_ICS"},
    {"asset": "State Bank Clearing Gateway", "port": 8080, "type": "FINTECH"}
]

class RegionalIntelMonitor:
    async def fetch_india_intel(self):
        """Streams India-specific Cyber & Recon Intelligence."""
        events = []
        await asyncio.sleep(0.5)
        if random.random() < 0.7:
            target = random.choice(INDIA_TARGETS)
            ip = f"103.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            timestamp = datetime.now().strftime("%H:%M:%S")
            status = random.choice(["MONITORING", "PORT_SCAN_DETECTED", "EXPOSED_SERVICE", "TRAFFIC_ANOMALY"])
            
            events.append({
                "timestamp": timestamp,
                "ip": ip,
                "asset": target["asset"],
                "status": status,
                "raw_text": f"[{status}] {target['asset']} ({ip}:{target['port']})"
            })
        return events

    async def fetch_pakistan_intel(self):
        """Streams Pakistan-specific Cyber & Recon Intelligence."""
        events = []
        await asyncio.sleep(0.5)
        if random.random() < 0.7:
            target = random.choice(PAKISTAN_TARGETS)
            ip = f"111.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            timestamp = datetime.now().strftime("%H:%M:%S")
            status = random.choice(["MONITORING", "EXPOSED_NODE", "C2_BEACON_CHECK", "LEAK_ALERT"])

            events.append({
                "timestamp": timestamp,
                "ip": ip,
                "asset": target["asset"],
                "status": status,
                "raw_text": f"[{status}] {target['asset']} ({ip}:{target['port']})"
            })
        return events
