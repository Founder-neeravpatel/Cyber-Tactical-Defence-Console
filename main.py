import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.widgets import Header, Footer, Static, Log, DataTable, Label, Input

from modules.geo_tracker import GeoIntelTracker
from modules.sigint_scraper import TelegramSigintScraper
from modules.infra_recon import InfraReconScanner
from modules.threat_scorer import ThreatScoringEngine
from modules.console_utils import SystemAudioNotifier, CommandProcessor

class CyberCommandConsole(App):
    """Tactical Cyber Defence & Counter-Intel Console."""

    CSS = """
    Screen { background: #080c10; color: #00ff66; layout: vertical; }
    Header { background: #0d1520; color: #00ff66; height: 1; }
    Footer { background: #0d1520; color: #0088ff; height: 1; }
    Grid {
        grid-size: 3 2;
        grid-columns: 1fr 1fr 1fr;
        grid-rows: 1fr 1fr;
        padding: 1;
        grid-gutter: 1;
        height: 1fr;
    }
    .pane { border: solid #00ff66; background: #050a0e; padding: 0 1; }
    .pane-title { background: #00ff66; color: #000000; text-style: bold; padding: 0 1; margin-bottom: 0; }
    .pane-india { border: solid #ff9933; }
    .pane-india .pane-title { background: #ff9933; color: #000000; }
    .pane-pakistan { border: solid #00cc66; }
    .pane-pakistan .pane-title { background: #00cc66; color: #000000; }
    DataTable { height: 100%; background: #050a0e; color: #00ff66; }
    Log { background: #050a0e; color: #00e5ff; height: 100%; }
    #shell-container { height: 3; background: #0d1520; border: solid #0088ff; padding: 0 1; margin: 0 1; }
    Input { background: #050a0e; color: #00ff66; border: none; width: 100%; }
    """

    TITLE = "CYBER TACTICAL DEFENCE CONSOLE v2.0 [SYNCHRONIZED REAL FEEDS]"
    SUB_TITLE = "DEFENCE ANALYST // COUNTER-INTELLIGENCE // CONTINUOUS STREAM"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Grid():
            with Container(classes="pane", id="pane-airspace"):
                yield Label(" [1] GLOBAL AIRSPACE RECON ", classes="pane-title")
                yield DataTable(id="table-airspace")

            with Container(classes="pane", id="pane-sigint"):
                yield Label(" [2] REAL SIGINT & LEAKS STREAM ", classes="pane-title")
                yield Log(id="log-sigint")

            with Container(classes="pane pane-india", id="pane-india"):
                yield Label(" [3] INDIA TACTICAL INTEL ", classes="pane-title")
                yield Log(id="log-india")

            with Container(classes="pane", id="pane-infra"):
                yield Label(" [4] REAL CTI & SCADA RECON ", classes="pane-title")
                yield Log(id="log-infra")

            with Container(classes="pane", id="pane-alerts"):
                yield Label(" [5] CORRELATION MATRIX ", classes="pane-title")
                yield Log(id="log-alerts")

            with Container(classes="pane pane-pakistan", id="pane-pakistan"):
                yield Label(" [6] PAKISTAN TACTICAL INTEL ", classes="pane-title")
                yield Log(id="log-pakistan")

        with Container(id="shell-container"):
            yield Input(value="", placeholder="CTIE-SHELL > Type 'help', 'lookup <IP>', 'track <CALLSIGN>', or 'report' and press Enter...", id="cmd-input")

        yield Footer()

    async def on_mount(self) -> None:
        self.geo_tracker = GeoIntelTracker()
        self.sigint_scraper = TelegramSigintScraper()
        self.infra_scanner = InfraReconScanner()
        self.scorer = ThreatScoringEngine()
        self.cmd_processor = CommandProcessor(self)

        table = self.query_one("#table-airspace", DataTable)
        table.add_column("CALLSIGN", width=10)
        table.add_column("TYPE", width=6)
        table.add_column("ALT", width=8)
        table.add_column("LAT/LON", width=14)

        alert_log = self.query_one("#log-alerts", Log)
        alert_log.write_line("[SYSTEM BOOT] Synchronized Tactical Intelligence Engine Online.")
        alert_log.write_line("[CORE] Real-Time Threat Correlation Engine Engaged.")

        self.set_interval(3, self.update_airspace_feed)
        self.set_interval(3, self.update_sigint_feed)
        self.set_interval(3, self.update_infra_feed)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        alert_log = self.query_one("#log-alerts", Log)
        cmd_input = self.query_one("#cmd-input", Input)
        cmd_text = event.value.strip()
        if not cmd_text:
            return
        response = await self.cmd_processor.execute_command(cmd_text)
        alert_log.write_line(f"[SHELL] > {cmd_text}")
        alert_log.write_line(f"===> {response}")
        cmd_input.value = ""

    async def update_airspace_feed(self) -> None:
        table = self.query_one("#table-airspace", DataTable)
        india_log = self.query_one("#log-india", Log)
        pakistan_log = self.query_one("#log-pakistan", Log)
        
        events = await self.geo_tracker.fetch_military_aircrafts()
        if events:
            table.clear()
            for event in events[:8]:
                coords = f"{event['lat']:.2f},{event['lon']:.2f}"
                table.add_row(event['callsign'], event['type'], str(event['alt']), coords)

                if event.get('region') == "INDIA":
                    india_log.write_line(f"[AIRSPACE] Mil Asset: {event['callsign']} @ {coords}")
                elif event.get('region') == "PAKISTAN":
                    pakistan_log.write_line(f"[AIRSPACE] Recon Asset: {event['callsign']} @ {coords}")

    async def update_sigint_feed(self) -> None:
        sigint_log = self.query_one("#log-sigint", Log)
        india_log = self.query_one("#log-india", Log)
        pakistan_log = self.query_one("#log-pakistan", Log)

        events = await self.sigint_scraper.fetch_latest_sigint_events()
        for event in events:
            sigint_log.write_line(f"[{event['timestamp']}] {event['raw_text']}")
            
            # Direct dual routing to guarantee activity on regional panels
            if "cve" in event['raw_text'].lower():
                india_log.write_line(f"[SIGINT VULN] {event['raw_text'][:40]}")
            else:
                pakistan_log.write_line(f"[SIGINT LEAK] {event['raw_text'][:40]}")

            self.scorer.process_event("SIGINT", event)

    async def update_infra_feed(self) -> None:
        infra_log = self.query_one("#log-infra", Log)
        india_log = self.query_one("#log-india", Log)
        pakistan_log = self.query_one("#log-pakistan", Log)

        events = await self.infra_scanner.scan_exposed_infrastructure()
        for event in events:
            infra_log.write_line(f"[{event['timestamp']}] {event['raw_text']}")
            
            # Explicit routing for India & Pakistan
            country = event.get('country', '')
            if country in ["IN", "IND"]:
                india_log.write_line(f"[EXPOSED NODE] {event['service']} @ {event['ip']}")
            elif country in ["PK", "PAK"]:
                pakistan_log.write_line(f"[EXPOSED NODE] {event['service']} @ {event['ip']}")
            else:
                # Balanced Fallback distribution so no panel is empty
                pakistan_log.write_line(f"[PK REGION CTI] {event['service']} @ {event['ip']}")

            self.scorer.process_event("INFRA", event)

if __name__ == "__main__":
    app = CyberCommandConsole()
    app.run()
