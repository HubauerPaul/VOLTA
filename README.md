# VOLTA

**V**ehicle **O**nboard **L**ive **T**elemetry & **A**nalytics: a digital driver display and race engineer monitoring system for the HTL electric kart.

| Part | What it is |
|---|---|
| **VOLTA Cockpit** | Driver display mounted in the kart. Reads the kart's CAN bus, shows speed, power, battery and boost status, and logs every drive. |
| **VOLTA Pit** | Race engineer dashboard in the pit: live telemetry, lap times, energy strategy, alerts and preset messages to the driver. |
| **VOLTA App** | Configuration app for speed limit, driving mode and boost, protected by a safety layer and user roles. |
| **VOLTA Gate** | Portable, battery-powered timing gate on a tripod (IR beacon, optional light barrier). One gate for laps, or separate start and finish gates for runs. |
| **VOLTA Pit Hub** | Portable pit connection: battery-powered Wi-Fi access point + LoRa radio on a mast. No fixed infrastructure or internet needed. |

VOLTA is built to move: there is no fixed track, and everything outside the kart can be set up at a new venue in under 15 minutes.

## Status

Concept phase. The display layout and system architecture are drafted; **the hardware is only a proposal and has not been discussed yet.**

## Documents

- [`docs/concept.html`](docs/concept.html): concept page with interactive cockpit and pit dashboard mockups, architecture, hardware proposal, performance targets and open questions. Open it in a browser. (The architecture diagram is Mermaid source and only renders on the published version of the page.)

The project is based on the *E-Kart Smart Cockpit* specification (Projekt 7, requirements F01–F135), which is treated as a recommendation rather than a fixed contract.
