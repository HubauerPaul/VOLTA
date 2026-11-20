# VOLTA – Bestellliste (Produktauswahl)

Stand: 2026-11-19 · Für den Einkauf: Hersteller und Typ sind festgelegt, der Händler ist frei wählbar. Preise sind grobe Schätzungen pro Stück, keine Angebote.

Grundlage ist die Hardware-Entscheidung vom 13.11.2026: Riverdi-Display, Raspberry Pi 4, LoRa als Standard-Funkverbindung, kein GPS. Die Spalte „Labor?“ vor der Bestellung abhaken: Was im Labor vorhanden ist, wird nicht bestellt.

## Kart-Einheit

| Pos. | Menge | Bauteil                                                                            | Hersteller / Typ                                                                                              | Wofür                                                                                | Labor? | ca. €   |
| ---- | ----- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------ | ------- |
| 1    | 1     | Display 7″, 1024×600, HDMI, 1000 cd/m², ohne Touch, mit Metallrahmen               | Riverdi **RVT70HSHFWN00**                                                                                     | Fahreranzeige, sonnenlesbar, Versorgung 7–30 V direkt vom Kart                       |        | 150–250 |
| 2    | 1     | Raspberry Pi 4 Model B, 2 GB                                                       | Raspberry Pi Ltd                                                                                              | Rechner im Kart                                                                      | ☐      | 50      |
| 3    | 1     | Step-down-Wandler 5 V / 5,5 A, Eingang 5,5–50 V                                    | Pololu **D36V50F5** (Art. 4091)                                                                               | 5 V für den Pi aus der Kart-Versorgung, verpolungsgeschützt                          | ☐      | 25      |
| 4    | 1     | Echtzeituhr DS3231 für Raspberry Pi                                                | Adafruit **PiRTC 4282**                                                                                       | Richtige Uhrzeit in den Logs ohne Netz (Pi 4 hat keine Uhr)                          | ☐      | 15      |
| 5    | 1     | Knopfzelle CR1220                                                                  | beliebig                                                                                                      | Batterie für Pos. 4                                                                  | ☐      | 2       |
| 6    | 1     | USB-CAN-Adapter mit candleLight-Firmware (gs_usb)                                  | baugleich zum vorhandenen Adapter (VID 1D50 / PID 606F); mit galvanischer Trennung z. B. DSD TECH **SH-C30G** | CAN-Anschluss fest im Kart, funktioniert mit unseren Tools                           | ☐      | 30      |
| 7    | 1     | LoRa-Modul 868 MHz, SX1262, mit Antenne                                            | Waveshare **SX1262 868M LoRa HAT** (SKU 16806)                                                                | Live-Daten zum Pit; per USB am Pi betrieben, damit keine GPIO-Konflikte              | ☐      | 25      |
| 8    | 1     | M12-T-Verteiler, 5-polig, A-kodiert, 2× Buchse / 1× Stecker, parallel              | Phoenix Contact **SAC-5PT-F/F-M VP** (1424712)                                                                | Abgriff am CANlink-Stecker: CAN, Versorgung 8–32 V und Zündung (Klemme 15)           | ☐      | 55      |
| 9    | 1     | M12-Anschlusskabel, 5-polig, A-kodiert, Stecker gerade, offenes Ende, ca. 2 m, PUR | beliebig (z. B. Phoenix Contact SAC-5P-…-PUR)                                                                 | Vom T-Verteiler zum VOLTA-Gehäuse                                                    | ☐      | 20      |
| 10   | 1     | microSD 32 GB, für Dauerbetrieb                                                    | SanDisk **High Endurance** 32 GB                                                                              | Betriebssystem und Logs                                                              | ☐      | 12      |
| 11   | 1     | Kabel Micro-HDMI auf HDMI, 0,5–1 m, möglichst gewinkelt                            | beliebig                                                                                                      | Pi 4 → Display                                                                       | ☐      | 8       |
| 12   | 1     | DC-Kabel mit Hohlstecker passend zum Display                                       | beliebig (Maß laut Riverdi-Datenblatt)                                                                        | Display-Versorgung vom Kart                                                          | ☐      | 5       |
| 13   | 1     | Kunststoffgehäuse IP65, ca. 160 × 100 × 60 mm                                      | beliebig, oder 3D-Druck                                                                                       | Pi, Wandler, Adapter                                                                 | ☐      | 20      |
| 14   | 4     | Kabelverschraubung M16, IP68                                                       | beliebig                                                                                                      | Kabeldurchführungen Gehäuse (CAN, Display, Antenne, Tasten)                          | ☐      | 2       |
| 15   | 1     | Kfz-Flachsicherungshalter (fliegend) + Sicherung 3 A                               | beliebig                                                                                                      | Absicherung der Abzweigung                                                           | ☐      | 6       |
| 16   | 1     | Optokoppler-Modul (PC817), 1 Kanal                                                 | beliebig                                                                                                      | Zündungssignal (Klemme 15, 8–32 V) sicher an einen GPIO, für sauberes Herunterfahren | ☐      | 5       |
| 17   | 1     | Kühlkörper-Set für Raspberry Pi 4                                                  | beliebig                                                                                                      | Wärme im geschlossenen Gehäuse in der Sonne                                          | ☐      | 6       |
| 18   | 1     | SMA-Verlängerung 868 MHz, ca. 1 m, mit Gehäusedurchführung                         | beliebig                                                                                                      | LoRa-Antenne außen am Kart montieren                                                 | ☐      | 8       |

### Lenkradtasten

Vier gleiche, beleuchtete Taster ersetzen die vorhandenen Boost- und Rückwärts-Taster und kommen mit D und Reserve neu dazu. Bauart wie der vorhandene Boost-Taster: Edelstahl-Drucktaster, flach, tastend, 1 Schließer, mit LED-Leuchtring, 4 Lötanschlüsse (2 Kontakt + 2 LED), IP67, Kontakt mindestens **2 A / 48 V DC**, LED **12 V**, Einbau-Ø **19 mm** (vorläufig, siehe Prüfpunkt 6). Buchstabe lasergraviert, er leuchtet mit. Halterung am Lenkrad per 3D-Druck, keine Bestellung.

**Anschluss:** B und R bleiben wie bisher direkt mit dem Kart verbunden (Kontakte, beim Boost auch die 12-V-LED „Boost verfügbar“). VOLTA liest den Boost-Status nur über den CAN-Bus (0x7D2). D und Reserve gehen an GPIOs des Pi. Die LEDs von R, D und Reserve schaltet der Pi über Pos. 23; die 12 V dafür erzeugt Pos. 24 aus den 5 V des Pi-Wandlers, weil die Kart-Versorgung zwischen 8 und 32 V liegen kann.

| Pos. | Menge | Bauteil | Hersteller / Typ | Wofür | Labor? | ca. € |
|---|---|---|---|---|---|---|
| 19 | 1 | Drucktaster wie oben, LED **blau**, Buchstabe **B** | beliebig, alle vier aus derselben Serie | Boost (ersetzt den vorhandenen Taster) | ☐ | 10 |
| 20 | 1 | Drucktaster wie oben, LED **gelb**, Buchstabe **R** | wie Pos. 19 | Rückwärtsgang (ersetzt den vorhandenen, unbeleuchteten Taster) | ☐ | 10 |
| 21 | 1 | Drucktaster wie oben, LED **grün**, Buchstabe **D** | wie Pos. 19 | Display-Seiten durchschalten | ☐ | 10 |
| 22 | 1 | Drucktaster wie oben, LED **rot**, ohne Buchstabe | wie Pos. 19 | Reserve | ☐ | 10 |
| 23 | 3 | N-Kanal-MOSFET 2N7000 (TO-92) + Widerstände 1 kΩ und 100 kΩ | beliebig | 12-V-LEDs von R, D und Reserve vom GPIO schalten | ☐ | 1 |
| 24 | 1 | Step-up-Wandler 5 V → 12 V, mind. 100 mA | beliebig, z. B. MT3608-Modul (auf 12 V eingestellt) | 12 V für die LEDs von R, D und Reserve | ☐ | 3 |
| 25 | 2 m | Steuerleitung 8 × 0,25 mm², geschirmt, flexibel (LiYCY) | beliebig | Lenkrad → VOLTA-Gehäuse: 2 Taster (D, Reserve), 3 LEDs (R, D, Reserve), 12 V, Masse, 1 Ader frei | ☐ | 6 |
| 26 | 1 Paar | Rundsteckverbinder M12, 8-polig, A-kodiert, Stecker + Buchse zur Kabelmontage, IP67 | beliebig (z. B. Phoenix Contact, Binder, Lumberg) | Lenkrad abnehmbar, ohne die Leitung abzulöten | ☐ | 30 |

## Pit-Station

| Pos. | Menge | Bauteil | Hersteller / Typ | Wofür | Labor? | ca. € |
|---|---|---|---|---|---|---|
| 27 | 1 | Raspberry Pi 4 Model B, 4 GB | Raspberry Pi Ltd | Pit-Monitor (Grafik, Auswertung) | ☐ | 65 |
| 28 | 1 | LoRa-Modul 868 MHz, SX1262 | Waveshare **SX1262 868M LoRa HAT** (SKU 16806) | Gegenstelle zu Pos. 7 | ☐ | 25 |
| 29 | 1 | Netzteil USB-C 5,1 V / 3 A | Raspberry Pi **offizielles Pi-4-Netzteil** | Versorgung Pit-Pi | ☐ | 10 |
| 30 | 1 | microSD 32 GB | SanDisk **High Endurance** 32 GB | Betriebssystem und Daten | ☐ | 12 |
| 31 | 1 | Bildschirm | **? – heute zu besprechen** | Anzeige im Pit | ☐ | ? |
| 32 | 1 | Kabel Micro-HDMI auf HDMI | beliebig | Pi 4 → Bildschirm | ☐ | 8 |

## Entwicklung

| Pos. | Menge | Bauteil | Hersteller / Typ | Wofür | Labor? | ca. € |
|---|---|---|---|---|---|---|
| 33 | 1 | Display 7″, 1024×600, HDMI | Joy-IT **RB-LCD-7-2** (falls nicht mehr lieferbar: RB-LCD-7-3) | Günstiges Testdisplay am Arbeitsplatz, gleiche Auflösung wie Pos. 1 | ☐ | 60–80 |
| 34 | 1 | microSD 32 GB | SanDisk **High Endurance** 32 GB | Reserve / Entwicklungsimage | ☐ | 12 |

**Summe grob:** etwa 720–820 € (Kart ca. 520–620 € inkl. Lenkradtasten ca. 85 €, Pit ca. 120 €, Entwicklung ca. 70–90 €) ohne Pit-Bildschirm und ohne Teile, die im Labor vorhanden sind.

## Bewusst nicht auf der Liste

- **GPS, IMU, Lichtschranke:** optional, erst wenn Zeitmessung oder Streckenaufzeichnung beschlossen sind.
- **USV/Pufferung für den Pi:** Stattdessen schreibgeschütztes Dateisystem und Herunterfahren über das Zündungssignal (Pos. 16).
- **Router und Mast für den Pit:** nur als späteres Upgrade, der Kart-Pi öffnet selbst einen WLAN-Hotspot.

## Vor der Bestellung prüfen

1. **Riverdi-Datenblatt:** HDMI-Buchsentyp (Standard oder Mini) und Hohlstecker-Maß, davon hängen Pos. 11 und 12 ab.
2. **Kabel zum CANlink:** Ist das Kart-Kabel wirklich M12, 5-polig, A-kodiert (Foto vom 12.11. spricht dafür)? Der T-Verteiler (Pos. 8) muss alle 5 Pole 1:1 durchreichen. Belegung am CANlink: 1 GND, 2 VCC 8–32 V, 3 Klemme 15, 4 CAN-H, 5 CAN-L.
3. **Spannung am CANlink-Stecker** messen und prüfen, ob sie mit dem Schlüssel geschaltet wird.
4. **Labor-Bestand** abhaken (vor allem Pi 4, USB-CAN-Adapter, Kleinteile, Gehäuse).
5. **Pit-Bildschirm** (Pos. 31) entscheiden.
6. **Taster-Durchmesser:** Das Lenkrad wird neu konstruiert, der Durchmesser ist deshalb noch frei. Eingetragen sind 19 mm (mit Handschuhen besser zu treffen, mehr Platz für den Buchstaben); 16 mm geht auch, wenn der Platz knapp ist. Vor der Bestellung mit der Lenkrad-Konstruktion abstimmen.
7. **Rückwärts-Taster:** Mit dem Multimeter prüfen, ob der alte Taster ein Schließer und tastend ist; sonst Pos. 20 anpassen.
8. **LED am Rückwärts-Taster:** Steht der Rückwärtsgang auf dem CAN-Bus (z. B. in 0x7D1), leuchtet die LED nur bei eingelegtem Rückwärtsgang, sonst dauerhaft. Beides schaltet der Pi über Pos. 23.
