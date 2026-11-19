# VOLTA – Bestellliste (Produktauswahl)

Stand: 2026-11-19 · Für den Einkauf: Hersteller und Typ sind festgelegt, der Händler ist frei wählbar. Preise sind grobe Schätzungen pro Stück, keine Angebote.

Grundlage ist die Hardware-Entscheidung vom 13.11.2026: Riverdi-Display, Raspberry Pi 4, LoRa als Standard-Funkverbindung, kein GPS. Die Spalte „Labor?“ vor der Bestellung abhaken: Was im Labor vorhanden ist, wird nicht bestellt.

## Kart-Einheit

| Pos. | Menge | Bauteil | Hersteller / Typ | Wofür | Labor? | ca. € |
|---|---|---|---|---|---|---|
| 1 | 1 | Display 7″, 1024×600, HDMI, 1000 cd/m², ohne Touch, mit Metallrahmen | Riverdi **RVT70HSHFWN00** | Fahreranzeige, sonnenlesbar, Versorgung 7–30 V direkt vom Kart | | 150–250 |
| 2 | 1 | Raspberry Pi 4 Model B, 2 GB | Raspberry Pi Ltd | Rechner im Kart | ☐ | 50 |
| 3 | 1 | Step-down-Wandler 5 V / 5,5 A, Eingang 5,5–50 V | Pololu **D36V50F5** (Art. 4091) | 5 V für den Pi aus der Kart-Versorgung, verpolungsgeschützt | ☐ | 25 |
| 4 | 1 | Echtzeituhr DS3231 für Raspberry Pi | Adafruit **PiRTC 4282** | Richtige Uhrzeit in den Logs ohne Netz (Pi 4 hat keine Uhr) | ☐ | 15 |
| 5 | 1 | Knopfzelle CR1220 | beliebig | Batterie für Pos. 4 | ☐ | 2 |
| 6 | 1 | USB-CAN-Adapter mit candleLight-Firmware (gs_usb) | baugleich zum vorhandenen Adapter (VID 1D50 / PID 606F); mit galvanischer Trennung z. B. DSD TECH **SH-C30G** | CAN-Anschluss fest im Kart, funktioniert mit unseren Tools | ☐ | 30 |
| 7 | 1 | LoRa-Modul 868 MHz, SX1262, mit Antenne | Waveshare **SX1262 868M LoRa HAT** (SKU 16806) | Live-Daten zum Pit; per USB am Pi betrieben, damit keine GPIO-Konflikte | ☐ | 25 |
| 8 | 1 | M12-T-Verteiler, 5-polig, A-kodiert, 2× Buchse / 1× Stecker, parallel | Phoenix Contact **SAC-5PT-F/F-M VP** (1424712) | Abgriff am CANlink-Stecker: CAN, Versorgung 8–32 V und Zündung (Klemme 15) | ☐ | 55 |
| 9 | 1 | M12-Anschlusskabel, 5-polig, A-kodiert, Stecker gerade, offenes Ende, ca. 2 m, PUR | beliebig (z. B. Phoenix Contact SAC-5P-…-PUR) | Vom T-Verteiler zum VOLTA-Gehäuse | ☐ | 20 |
| 10 | 1 | microSD 32 GB, für Dauerbetrieb | SanDisk **High Endurance** 32 GB | Betriebssystem und Logs | ☐ | 12 |
| 11 | 1 | Kabel Micro-HDMI auf HDMI, 0,5–1 m, möglichst gewinkelt | beliebig | Pi 4 → Display | ☐ | 8 |
| 12 | 1 | DC-Kabel mit Hohlstecker passend zum Display | beliebig (Maß laut Riverdi-Datenblatt) | Display-Versorgung vom Kart | ☐ | 5 |
| 13 | 1 | Kunststoffgehäuse IP65, ca. 160 × 100 × 60 mm | beliebig, oder 3D-Druck | Pi, Wandler, Adapter | ☐ | 20 |
| 14 | 3 | Kabelverschraubung M16, IP68 | beliebig | Kabeldurchführungen Gehäuse | ☐ | 2 |
| 15 | 1 | Kfz-Flachsicherungshalter (fliegend) + Sicherung 3 A | beliebig | Absicherung der Abzweigung | ☐ | 6 |
| 16 | 1 | Optokoppler-Modul (PC817), 1 Kanal | beliebig | Zündungssignal (Klemme 15, 8–32 V) sicher an einen GPIO, für sauberes Herunterfahren | ☐ | 5 |
| 17 | 1 | Kühlkörper-Set für Raspberry Pi 4 | beliebig | Wärme im geschlossenen Gehäuse in der Sonne | ☐ | 6 |
| 18 | 1 | SMA-Verlängerung 868 MHz, ca. 1 m, mit Gehäusedurchführung | beliebig | LoRa-Antenne außen am Kart montieren | ☐ | 8 |

## Pit-Station

| Pos. | Menge | Bauteil | Hersteller / Typ | Wofür | Labor? | ca. € |
|---|---|---|---|---|---|---|
| 19 | 1 | Raspberry Pi 4 Model B, 4 GB | Raspberry Pi Ltd | Pit-Monitor (Grafik, Auswertung) | ☐ | 65 |
| 20 | 1 | LoRa-Modul 868 MHz, SX1262 | Waveshare **SX1262 868M LoRa HAT** (SKU 16806) | Gegenstelle zu Pos. 7 | ☐ | 25 |
| 21 | 1 | Netzteil USB-C 5,1 V / 3 A | Raspberry Pi **offizielles Pi-4-Netzteil** | Versorgung Pit-Pi | ☐ | 10 |
| 22 | 1 | microSD 32 GB | SanDisk **High Endurance** 32 GB | Betriebssystem und Daten | ☐ | 12 |
| 23 | 1 | Bildschirm | **? – heute zu besprechen** | Anzeige im Pit | ☐ | ? |
| 24 | 1 | Kabel Micro-HDMI auf HDMI | beliebig | Pi 4 → Bildschirm | ☐ | 8 |

## Entwicklung

| Pos. | Menge | Bauteil | Hersteller / Typ | Wofür | Labor? | ca. € |
|---|---|---|---|---|---|---|
| 25 | 1 | Display 7″, 1024×600, HDMI | Joy-IT **RB-LCD-7-2** (falls nicht mehr lieferbar: RB-LCD-7-3) | Günstiges Testdisplay am Arbeitsplatz, gleiche Auflösung wie Pos. 1 | ☐ | 60–80 |
| 26 | 1 | microSD 32 GB | SanDisk **High Endurance** 32 GB | Reserve / Entwicklungsimage | ☐ | 12 |

**Summe grob:** etwa 650–750 € (Kart ca. 450–550 €, Pit ca. 120 €, Entwicklung ca. 70–90 €) ohne Pit-Bildschirm und ohne Teile, die im Labor vorhanden sind.

## Bewusst nicht auf der Liste

- **GPS, IMU, Lichtschranke:** optional, erst wenn Zeitmessung oder Streckenaufzeichnung beschlossen sind.
- **Lenkradtasten:** Ohne Tasten und ohne Touch kann der Fahrer nicht selbst zwischen den Anzeigen wechseln; der Wechsel müsste automatisch oder über die App erfolgen.
- **USV/Pufferung für den Pi:** Stattdessen schreibgeschütztes Dateisystem und Herunterfahren über das Zündungssignal (Pos. 16).
- **Router und Mast für den Pit:** nur als späteres Upgrade, der Kart-Pi öffnet selbst einen WLAN-Hotspot.

## Vor der Bestellung prüfen

1. **Riverdi-Datenblatt:** HDMI-Buchsentyp (Standard oder Mini) und Hohlstecker-Maß, davon hängen Pos. 11 und 12 ab.
2. **Kabel zum CANlink:** Ist das Kart-Kabel wirklich M12, 5-polig, A-kodiert (Foto vom 12.11. spricht dafür)? Der T-Verteiler (Pos. 8) muss alle 5 Pole 1:1 durchreichen. Belegung am CANlink: 1 GND, 2 VCC 8–32 V, 3 Klemme 15, 4 CAN-H, 5 CAN-L.
3. **Spannung am CANlink-Stecker** messen und prüfen, ob sie mit dem Schlüssel geschaltet wird.
4. **Labor-Bestand** abhaken (vor allem Pi 4, USB-CAN-Adapter, Kleinteile, Gehäuse).
5. **Pit-Bildschirm** (Pos. 23) entscheiden.
