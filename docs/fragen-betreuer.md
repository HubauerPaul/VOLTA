# VOLTA – Fragen an den Kart-Betreuer

Stand: 2026-11-05

27 offene Fragen für das Gespräch mit dem Betreuer des Rotax-MAX-Dome-Karts. Mit ★ markierte Fragen zuerst klären: Ohne sie können wir nicht weiterplanen.

Bereits geklärt, daher nicht gefragt: Bitrate 500 kbit/s. Aus der MAX-Dome-Spezifikation (REV05, Entwurf vom 02.12.2020): Boost-Auslösung per Lenkradtaste mit LED, alle Zykluszeiten 100 ms, Bitbelegung von 0x015, 0x083, 0x7D1 und 0x7D2, Statusbits, und unzulässige Schreibbefehle werden ohne Rückmeldung ignoriert.

> **Fehler im Tool, vor dem nächsten Boost-Test beheben:** Die Spezifikation legt für `fMap,Boost` Faktor 0,01 und Offset 1 fest. `maxdome_can_tool.py` ignoriert den Offset beim Senden und Lesen. Eingestellte 1,50 ergeben laut Spezifikation 2,50 am Kart, und die Anzeige zeigt trotzdem 1,50. Das ist nicht am Kart geprüft.

## Fahrzeug und Leistung

1. ★ Welche Motor- und Batteriedaten hat das Kart: Spitzen- und Dauerleistung, maximales Drehmoment, maximale Drehzahl, Nennspannung, Kapazität? Gelten die Power Maps von 2020 noch (Eco 3 kW, Normal 5 kW, Sport 8 kW)?
2. ★ Welche Boost-Werte sind aktuell eingestellt und für uns freigegeben (Dauer, Ladezeit, Anzahl, Faktor)? Wurde der Faktor schon mit `maxdome_can_tool.py` gesetzt?
3. ★ Gibt es Rekuperation über die Motorbremse beim Speed-Limit hinaus (laut Spezifikation max. 1,33 m/s²)? Wenn ja: wie viel Leistung, wann aktiv, einstellbar, und ist sie auf dem CAN-Bus sichtbar?
4. ★ Welche Grenzen sind fest in der VCU (Leistung, Strom, Temperatur), und welche Werte dürfen wir auch innerhalb der Spezifikation nie setzen?
5. Welche der drei Getriebekonfigurationen (Gear 0–2) gibt es an diesem Kart tatsächlich?

## Hardware

6. ★ Wo schließen wir physisch an: vorhandener Stecker, Kabelbaum oder Leitung? Welcher Steckertyp, wo sitzt er, und dürfen wir den Kabelbaum verändern?
7. ★ Woher kommt der Strom fürs Display: 12-V-Schiene oder DC/DC-Wandler? Welcher Spannungsbereich, wie viel Strom, wie abgesichert? Gibt es ein Zündungssignal (Klemme 15), und bleibt die Versorgung beim Ausschalten kurz bestehen?
8. ★ Wie ist der CAN-Bus terminiert: Wo sitzen die 120-Ω-Widerstände, sind sie fest verbaut, und welche Stichleitungslänge ist erlaubt? Der CANlink ist nicht galvanisch getrennt: Ist das an diesem Kart zulässig, oder ist eine Trennung vorgeschrieben?
9. Welche Geräte hängen schon am Bus (VCU, BMS, Motorsteuerung, Originaldisplay, das WLAN-Modul aus der Spezifikation), und wie hoch ist die Buslast? Welches CANlink-Modell haben wir (3001: bis 75 m, 3002: bis 200 m), und ist es fest verbaut?
10. Wo kann das Display montiert werden: Lenkrad oder Lenksäule, wie viel Platz, welcher Abstand zum Auge? Wird auch bei Regen gefahren?

## CAN-Protokoll

11. ★ Gibt es eine offizielle DBC-Datei oder eine neuere Spezifikation als den Entwurf REV05 von 2020? Was bedeuten die Signale ohne Namen in 0x083 (Bit 12, 14, 15, 23, 42, 48, 57, 59, 60)?
12. ★ Life-Counter 0x7F7: Laut Spezifikation sendet ihn der Server alle 100 ms, und die Nachricht heißt „Torque Lock“. Wer sendet ihn an diesem Kart? Sperrt das Kart das Drehmoment, wenn er ausbleibt oder springt? Welcher der drei Abläufe aus den Skripten hat zuletzt am echten Kart funktioniert?
13. ★ Auf welchen IDs liegen Drehzahl, Drehmoment, Spannung, Strom, Temperaturen und Rekuperation? In der Spezifikation stehen sie nicht.
14. Darf die Power Map im Fahrmodus geändert werden? Die Spezifikation widerspricht sich: Kapitel 3.4 nennt Neutral und Drive, die Tabelle in Kapitel 4 nur Neutral.
15. Bleiben geschriebene Einstellungen nach dem Ausschalten erhalten?
16. Was bewirkt `f_Pwr` in 0x7F8 genau, und welches Referenzgewicht (mref) gilt für die Parity?

## Sicherheit

17. ★ Gibt es sicherheitsrelevante CAN-Nachrichten, die wir nicht lesen, verzögern oder stören dürfen? Reicht es, standardmäßig nur mitzuhören (Listen-only)?
18. ★ Wie reagiert das Kart, wenn die Verbindung zum Display abbricht oder das Display während der Fahrt ausfällt?
19. ★ Sind die Prüfungen aus der Spezifikation am Kart wirklich umgesetzt (Fahrzustand, Parity mindestens 0,7, Geschwindigkeitsschwellen)? Dürfen wir vMax während der Fahrt senken, obwohl das Kart dann selbst bremst?
20. Gibt es Herstellervorgaben für Displays oder Zusatzgeräte (Zulassung, Garantie, EMV, Gewicht)?
21. Was passiert bei einem Bus-Off oder einem fehlerhaften Teilnehmer? Die Skripte erwähnen ACK- und Bus-Off-Probleme: Sind die am Kart tatsächlich aufgetreten?
22. Wer darf am Kart arbeiten? Gibt es Hochvolt-Regeln, einen Not-Aus und eine Einweisung, die wir brauchen?

## Testumgebung

23. ★ Gibt es einen CAN-Simulator oder Prüfstand? Können wir sonst am stehenden Kart testen, wie oft und unter wessen Aufsicht?
24. ★ Dürfen wir aktiv auf den Bus senden, oder am Anfang nur mitlesen? Die Skripte senden zum Beispiel einen Testframe auf 0x123.
25. Können wir früh ein CAN-Log einer echten Fahrt bekommen oder selbst aufzeichnen? Damit bauen wir den Simulator.
26. Gibt es schon fixe Termine für Testfahrten oder Bewerbe, an denen das Kart nicht verfügbar ist? Wie früh müssen wir Testfahrten anfragen?
27. Wo wird getestet, auch in Hallen (dort funktioniert kein GPS)? Wer fährt, und welche Geschwindigkeitsgrenzen gelten bei Tests?
