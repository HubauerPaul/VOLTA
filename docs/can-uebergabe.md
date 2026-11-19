# CAN-Daten: Übergabe an Simulator und Dekodierung

Stand 19.11.2026. Alles stammt aus der Messung vom 12.11.2026 am aufgebockten Kart, ohne echte Fahrt. Gesendet wurde nur beim Schreibtest (Capture 03), sonst wurde ausschließlich mitgehört.

## Dateien

| Datei | Inhalt |
|---|---|
| `captures/README.md` | Was in welchem Capture steckt, Spaltenformat |
| `captures/01_…`, `02_…`, `05_…` | Rohdaten des Busses (CSV): Leerlauf, Gaspedal-Sweep, Leerlauf am Ende |
| `captures/03_probe_counter_vmax30.csv` | Schreibtest (vMax 30), vom Kart ignoriert |
| `captures/config_backup_*.json` | Konfiguration aus 0x7D1/0x7D2, dekodiert |
| `docs/can-ids.md` / `.csv` | **Katalog aller 81 IDs:** Rate, DLC, CRC, jedes Byte (konstant, Zähler oder Wertebereich), Hinweise aus dem Sweep. Die CSV ist maschinenlesbar. |
| `docs/can-bus.md` | Bisherige Analyse: dekodierte Signale, E2E-Schutz, Schreibtests, Diagnose-Antworten |
| `reference_docs/2020_12_04_MAXDome_InterfaceSpec (8).pdf` | Rotax-Spezifikation (Entwurf REV05) für 0x015, 0x083, 0x7D1, 0x7D2, 0x7F3–0x7F8 |
| `tools/can/` | `sniff.py` (mitlesen), `e2e.py` (CRC), `catalogue.py` (erzeugt den Katalog), `config.py`, `probe.py`, `uds_scan.py` |

## Was bekannt ist

**Bus:** 500 kbit/s, 11-Bit-IDs, etwa 2190 Frames/s, 81 IDs mit 100, 10, 4, 2 und 1 Hz, keine Error-Frames.

**Dekodierte Signale**

| Signal | ID | Bytes | Kodierung | Sicherheit |
|---|---|---|---|---|
| Gaspedal | 0x083 | b5 | 0–200 = 0–100 % | hoch |
| Motordrehzahl | 0x03C | b4–b5 | int16 little endian, rpm | hoch |
| Motordrehzahl | 0x010 | b4 | ca. rpm / 60 | mittel |
| Fahrzeuggeschwindigkeit | 0x015 | b2 | folgt der Drehzahl, Skalierung ungeprüft | mittel |
| Kart-Status | 0x7D1 | b0–b4 | laut Spezifikation; vMax 40 = Rohwert 0x23 stimmt mit der Konfiguration überein | hoch |
| Boost-Status | 0x7D2 | b0–b7 | laut Spezifikation | hoch |
| DC-Strom? | 0x050 | b6–b7 | int16 LE, unter Last negativ, Einheit unbekannt | mittel |
| Strom oder Leistung? | 0x008 | b0 | 0..47, steigt unter Last | niedrig |

**E2E-Schutz:** Bei den meisten zyklischen IDs ist Byte 0 eine CRC und Byte 1 (Bits 0–3) ein Zähler 0–15.
- **Bekannt:** Für 33 IDs ist die Berechnung bekannt und auf allen Captures geprüft (`e2e.py`).
- **Unbekannt:** Für 0x015, 0x028, 0x064, 0x078 und 0x083 ist die CRC-Berechnung noch offen. Die frühere Angabe in `can-bus.md`, dass sie gelöst sei, war falsch und ist korrigiert.

**Schreiben funktioniert nicht:** Der Kart ignoriert vMax-Anfragen über 0x7F5 mit Life-Counter auf 0x7F7, sowohl in Drive als auch in Neutral. Die alten Skripte des Teams haben es auch nie geschafft.

## Für den Simulator

Ziel ist, dass Display und Backend ohne Kart entwickelt werden können.

1. **Replay:** Ein Capture mit den originalen Zeitabständen abspielen (`hw_us` für die exakten Abstände). CRC und Zähler bleiben dabei gültig, auch bei den unbekannten IDs. Das ist der schnellste Start.
2. **Synthetisch:** Die Werte für Drehzahl, Gas, Geschwindigkeit, Status und Boost frei vorgeben und daraus Frames erzeugen.
   - Rate und DLC jeder ID stehen in `docs/can-ids.csv`.
   - Bytes, die sich nie ändern, kommen aus `idle_example`.
   - Zähler pro Frame um 1 erhöhen, CRC mit `e2e.py` berechnen.
   - Für die 5 IDs mit unbekannter CRC gibt es keine gültige CRC. Das Display darf die CRC dort nicht prüfen; das ist eine Entscheidung für das Backend.
3. **Fehler einspeisen:** ID fällt aus, Zähler springt, falsche CRC, Bus ganz still (wie im Projektdokument gefordert, F95).

Schnittstelle: python-can `virtual` oder `udp_multicast` unter Windows, SocketCAN `vcan0` auf dem Raspberry Pi. Dann kann das Backend ohne Codeänderung zwischen Simulator und Kart wechseln.

Den Simulator nie auf den echten Kart-Bus legen.

## Für die Dekodierung

Offene Aufgaben, die wichtigsten zuerst:

1. **Geschwindigkeit 0x015:** Skalierung von b2 bestimmen. Die Bitposition laut Spezifikation kollidiert mit dem E2E-Zähler. Braucht eine Messung bei echter Fahrt mit bekanntem Tempo (z. B. GPS am Handy als Referenz).
2. **SoC, SoH, Reichweite, Störungsanzeige (MIL) in 0x083:** Laut Spezifikation liegen sie dort, die Bitpositionen passen aber nicht zum E2E-Layout. b2 ist im Leerlauf 0x50 und im Sweep 0x51 oder 0xD1. Braucht Messungen bei bekanntem Ladestand (Anzeige am Ladegerät).
3. **0x006:** neuer Hinweis aus dem Sweep. b3–b4 (int16 LE) folgt der Drehzahl negativ (r = −1,00), b6–b7 positiv (r = +0,99). Das sind Kandidaten für Drehmoment oder Strom.
4. **Batterieblöcke 0x220–0x23B:** vier gleich aufgebaute Blöcke zu je 7 IDs, vermutlich die vier Batteriemodule (Zellspannungen, Temperaturen). Mehrere Bytes ändern sich unter Last.
5. **Strom 0x050 b6–b7 und 0x008 b0:** Einheit und Vorzeichen klären. Rekuperation beim Loslassen des Pedals?
6. **0x700–0x707:** 100/10 Hz ohne CRC, Byte 0 oder 1 sieht nach Index oder Zähler aus. Möglicherweise multiplexed.
7. **CRC der 5 offenen IDs:** nur nötig, wenn wir diese IDs selbst erzeugen oder prüfen wollen.
8. **Konstante IDs** (0x004, 0x206, 0x208–0x20F, 0x225, 0x22C, 0x311, 0x401, 0x500, 0x510–0x513): niedrige Priorität, vermutlich Versionen oder Konfiguration.

**Vorgehen:** Neue Captures mit `sniff.py log` aufzeichnen (immer listen-only) und mit `catalogue.py` auswerten. Für neue Referenzsignale die Liste `KNOWN` in `catalogue.py` ergänzen.

**Benötigte neue Messungen:**
- echte Fahrt mit Tempo-Referenz
- Bremsen
- Zündung aus und wieder ein
- Laden mit bekanntem Ladestand
- Boost-Taste drücken
- verschiedene Power Maps (am Kart umgestellt, nicht per CAN)

**Für die Filterung (US 04):** Für den Fahrer sind Geschwindigkeit, SoC, Boost, vMax und MIL kritisch. Für die Diagnose zählen SoH, Statusbits, Batteriemodule und Strom. Alles andere wird gefiltert.
