# Kart CAN bus: reverse engineering notes

Status 2026-11-12: passive analysis plus the official interface spec. Nothing has been transmitted on the bus yet.

## Setup

- Kart: Bosch inverter, Proemion CANlink wireless gateway.
- PC: candleLight USB-CAN adapter (gs_usb, VID 1D50 PID 606F), opened in **listen-only** mode by `tools/can/sniff.py`.
- Bus: **500 kbit/s**, 11-bit IDs only, 0 error frames, about 2200 frames/s.

## Captures (baseline backup)

| File | Condition |
|---|---|
| `captures/01_idle_no_throttle.csv` | Kart on, jacked up, no throttle, 30 s |

## Official configuration interface (Rotax MAX Dome)

Source: `reference_docs/2020_12_04_MAXDome_InterfaceSpec (8).pdf` (REV05, draft). The Proemion CANlink is the "WLAN module" in the spec. A server sends configuration requests on dedicated IDs, and the kart reports its configuration cyclically. These IDs carry no E2E CRC, so writing is possible without spoofing protected frames.

| ID | Direction | Content |
|---|---|---|
| 0x7F7 | to kart, cyclic 100 ms | life counter, byte 7 bits 0-3, 0..15 ("Torque Lock" in the spec) |
| 0x7F3 | to kart | gear 0..2 (neutral only) |
| 0x7F4 | to kart | boost: enable, tBoostMax (0.5 s), tChgMax (0.5 s), nBoost int8 (-1 = unlimited), fMapBoost (raw × 0.01 + 1) |
| 0x7F5 | to kart | vMax, raw + 5 = km/h |
| 0x7F6 | to kart | map 0 Normal 5 kW, 1 Eco 3 kW, 2 Sport 8 kW (neutral only) |
| 0x7F8 | to kart | parity f (raw × 0.9/255 + 0.1, min. 0.7 is applied), f_Pwr (raw × 0.1) |
| 0x7D1 | from kart, 100 ms | drive status bits, vMax, map/gear, f, f_Pwr |
| 0x7D2 | from kart, 100 ms | boost status and timers |

`tools/can/config.py` implements this (`status` is listen-only; `set-vmax` and `restore` transmit and verify via 0x7D1).
Bug in `reference_docs/maxdome_can_tool.py`: it encodes fMapBoost as `f × 100`. The spec has offset 1, so 1.50 would be sent as raw 150, which means 2.50.
0x7F7 is not on the bus at the moment, so no server is connected.

### Write tests 2026-11-12 (kart jacked up, Drive, key position 1)

All frames were ACKed on the bus (adapter echo received), but the kart **did not apply vMax 30**. 0x7D1 kept reporting 40 km/h, and the drive status stayed at 0x43: no torque lock, no limp home.

| # | Sequence | Result |
|---|---|---|
| 1 | 0x7F7 counter once, 0x7F5 `19` (DLC 1), counter once (same as `set_speed_limit_rotax_max_dome.py`) | ignored |
| 2 | 0x7F7 cyclic 100 ms for 1 s, then 0x7F5 `19` (DLC 1), counter continued 3 s | ignored |
| 3 | as 2, with 0x7F5 padded to DLC 8 | ignored |
| 4 | as 2, with the whole bus logged (`tools/can/probe.py`, `captures/03_probe_counter_vmax30.csv`) | ignored; no ID and no byte on the bus reacts to the counter or the request |

`set_speed_limit_rotax_max_dome.py` never worked either (confirmed by the team).

The CANlink manual describes the device as a transparent CAN to WLAN/Bluetooth bridge, so it should not filter these IDs.

### Backup and restore

Nothing that was sent changed the kart's stored configuration. The snapshot taken at the end of the session (`captures/config_backup_2026-11-12_final.json`, bus snapshot `captures/05_idle_final_state.csv`) matches the initial backup exactly: same 81 IDs at the same rates, same vMax, map, gear, parity and boost values. The only difference is drive status 0x42 (Neutral) instead of 0x43 (Drive), which comes from the drive selector, not from a stored setting.

To return to the documented state:
1. Key off, then key on again (clears any open diagnostic session or counter state).
2. Check with `python config.py status` (listen-only) and compare against `captures/config_backup_2026-11-12.json`.
3. Only if a stored value differs: `python config.py restore ../../captures/config_backup_2026-11-12.json` (restores vMax, parity and boost through the official interface; map and gear are not touched because they were never changed).

Diagnostic responders found with read-only broadcast requests on 0x7DF (`tools/can/uds_scan.py`, `captures/04_uds_scan.csv`): 0x760 (probably the VCU, answers session requests, rejects data reads with NRC 0x22) and 0x281/0x283/0x285/0x287 (probably the four battery modules, return a serial number via 0x22 F18C).

### Configuration backup 2026-11-12

`captures/config_backup_2026-11-12.json`, restorable with `python config.py restore ../../captures/config_backup_2026-11-12.json`:

- Drive status 0x43: Drive, Enable Drive, key position 1
- **vMax 40 km/h**, **map 1 (Eco, 3 kW)**, gear 0, parity f 1.0, f_Pwr raw 0
- Boost enabled, tBoostMax 9 s, tChgMax 5 s, nBoost 0 (no boosts left), fMapBoost 1.40

## Message overview (idle)

81 IDs. Rates: 100 Hz, 10 Hz, 4 Hz, 2 Hz, 1 Hz.

| IDs | Rate | Notes |
|---|---|---|
| 0x001, 0x002, 0x004, 0x006, 0x007, 0x00D, 0x014, 0x200, 0x201, 0x215 | 100 Hz | fast control / status |
| 0x008, 0x010, 0x015, 0x028, 0x03C, 0x050, 0x064, 0x083 | 10 Hz | |
| 0x078 | 2 Hz | |
| 0x079 | 1 Hz | |
| 0x202 to 0x20F | 10 / 1 Hz | 0x208 to 0x20F all zero |
| 0x210, 0x211 | 10 Hz | |
| 0x220 to 0x23B | 100 / 10 / 1 Hz | four blocks of seven IDs (220-226, 227-22D, 22E-234, 235-23B) with identical structure: probably four battery modules or packs |
| 0x311 | 2 Hz | all zero |
| 0x401, 0x500, 0x510 to 0x513 | 4 Hz | constant, start with `01 03` |
| 0x700 to 0x707 | 100 / 10 Hz | no CRC, byte 0 or 1 is a counter or index |
| 0x7D1, 0x7D2 | 10 Hz | constant |

## Decoded signals

From `captures/02_throttle_sweep.csv` (pedal pressed slowly to full and released, wheels free). Byte numbers start at 0, multi-byte values are little endian.

| Signal | ID | Bytes | Encoding | Confidence |
|---|---|---|---|---|
| Throttle pedal | 0x083 | b5 | 0..200 = 0..100 % (0.5 %/bit) | high: clean ramp, plateau at exactly 200 |
| Motor speed | 0x03C | b4-b5 | signed 16 bit, rpm (peak 6700 with wheels free) | high |
| Motor speed (rev/s) | 0x010 | b4 | about rpm / 60 (peak 113) | medium |
| Vehicle speed | 0x015 | b2 (spec: 9 bit, 0.5 km/h, b2 plus the top bit of b3) | follows rpm exactly, peak about 45 km/h while vMax is 40 | medium; the spec's bit position collides with the E2E counter, so verify by changing vMax |
| DC current? | 0x050 | b6-b7 | signed 16 bit, negative under load (about -4000), positive spike when releasing the pedal (regen?) | medium, unit unknown |
| Current or power? | 0x008 | b0 | 0..47, rises under load | low |
| Event at pedal release | 0x007 b3, 0x028 b4, 0x001 b2-3 | | short change right after releasing the pedal: brake, regen or a limiter? | open |

0x050 b0-b1 is a sawtooth 0..4000 (about 1.5 s period): a counter or timestamp, not a physical signal.
0x002 and 0x006 change heavily under load but are bit packed; not decoded yet.

Next captures: brake, ignition off/on.

## E2E protection

Most cyclic frames carry AUTOSAR-style E2E protection:

- **Byte 0:** CRC8, polynomial 0x2F (CRC8H2F).
- **Byte 1, bits 0-3:** alive counter 0..15, incremented every frame.

Two variants, implemented in `tools/can/e2e.py` and verified on all three bus captures (01, 02, 05):

- **Simple:** init 0x00, no final XOR, over bytes 1..n. IDs 0x014, 0x200 to 0x205, 0x215 and the 0x22x/0x23x blocks.
- **Profile 2:** init 0xFF, final XOR 0xFF, over bytes 1..n plus a data ID chosen by the counter value (16 values per ID). IDs 0x001, 0x002, 0x006, 0x007, 0x010.

**Correction 2026-11-19:** 0x015, 0x028, 0x064, 0x078 and 0x083 were listed as profile 2 before, but their data ID tables were fitted on the idle capture only. There the payload never changes, so any table fits. They fail on the throttle sweep and on capture 05. Byte 0 is a CRC and byte 1 bits 0-3 the alive counter, but the scheme is unknown: profile 2 with a per-counter data ID (appended or prepended, with or without XOR), a constant 16-bit data ID with CRC8H2F or SAE J1850, and a plain CRC over bytes 1..n were all tried without success. The old tables are kept as `UNSOLVED_IDS` in `e2e.py`.

Not yet identified: 0x03C, 0x050 (byte 0 changes, but neither variant fits), 0x210/0x211, 0x700 to 0x706.

Per-ID details (rates, byte ranges, CRC results, leads from the throttle sweep): `docs/can-ids.md`, generated by `tools/can/catalogue.py`.

Consequence for writing: a frame sent by us under an existing ID needs a correct CRC and counter. On top of that, it collides with the original sender's counter sequence, so the receiver will most likely see E2E errors.
