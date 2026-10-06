from datetime import datetime

class ThreatScoringEngine:
    def __init__(self):
        self.recent_events = []
        self.score_weights = {
            "AIRSPACE_PRIORITY": 25,
            "SIGINT_CRITICAL": 40,
            "INFRA_CRITICAL": 35,
            "INFRA_HIGH": 20
        }

    def process_event(self, source_module, event_data):
        """Calculates risk score and evaluates multi-source cross-correlation."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        calculated_score = 0
        correlation_alert = None

        if source_module == "AIRSPACE" and event_data.get("priority"):
            calculated_score = self.score_weights["AIRSPACE_PRIORITY"]
            self.recent_events.append({"type": "AIRSPACE", "data": event_data, "time": timestamp})

        elif source_module == "SIGINT":
            if event_data.get("severity") == "CRITICAL":
                calculated_score = self.score_weights["SIGINT_CRITICAL"]
                self.recent_events.append({"type": "SIGINT", "data": event_data, "time": timestamp})

        elif source_module == "INFRA":
            risk = event_data.get("risk")
            if risk == "CRITICAL":
                calculated_score = self.score_weights["INFRA_CRITICAL"]
                self.recent_events.append({"type": "INFRA", "data": event_data, "time": timestamp})
            elif risk == "HIGH":
                calculated_score = self.score_weights["INFRA_HIGH"]

        # Keep buffer sized to last 20 events
        if len(self.recent_events) > 20:
            self.recent_events.pop(0)

        # Cross-Module Correlation Detection
        types_in_buffer = {e["type"] for e in self.recent_events[-5:]}
        if len(types_in_buffer) >= 2 and calculated_score >= 35:
            correlation_alert = {
                "timestamp": timestamp,
                "score": calculated_score + 25,  # Boost score for correlated events
                "types": list(types_in_buffer),
                "summary": f"[CORRELATED ALERT] Multi-Source Threat Event Detected ({'+'.join(types_in_buffer)})"
            }

        return calculated_score, correlation_alert
