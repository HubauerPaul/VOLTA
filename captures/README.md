# CAN captures

Recorded on 2026-11-12 on the HTL e-kart (Rotax MAX Dome, Bosch inverter), kart jacked up, wheels free. Bus: 500 kbit/s, 11-bit IDs, no error frames. Recorded with `tools/can/sniff.py` (candleLight adapter in listen-only mode) unless stated otherwise.

| File | Condition | Duration | Frames | IDs |
|---|---|---|---|---|
| `01_idle_no_throttle.csv` | Key on, Drive, no throttle | 30 s | 65,570 | 81 |
| `02_throttle_sweep.csv` | Throttle pressed slowly to full and released, wheels free (peak about 6700 rpm, about 45 km/h shown) | 25 s | 54,729 | 81 |
| `03_probe_counter_vmax30.csv` | Write test: 2 s silent, 4 s life counter 0x7F7 every 100 ms with a vMax 30 request on 0x7F5, 3 s silent. The kart ignored it. | 9 s | 19,744 | 83 |
| `04_uds_scan.csv` | Answers to read-only diagnostic broadcasts on 0x7DF (not a bus log) | – | 19 | – |
| `05_idle_final_state.csv` | Same as 01 at the end of the session, drive selector in Neutral | 30 s | 65,674 | 81 |
| `config_backup_2026-11-12.json` | Decoded 0x7D1/0x7D2 at the start of the session (vMax 40, map 1 Eco, boost settings) | – | – | – |
| `config_backup_2026-11-12_final.json` | Same at the end; identical apart from Drive/Neutral | – | – | – |

## Columns

Bus logs 01, 02 and 05:

| Column | Meaning |
|---|---|
| `time` | PC receive time, Unix epoch in seconds |
| `hw_us` | Adapter hardware timestamp in µs (wraps around; use for exact frame spacing) |
| `id` | CAN ID, hex without `0x` |
| `ext`, `rtr`, `err` | Extended ID, remote frame, error frame (always 0 here) |
| `dlc` | Data length |
| `data` | Payload bytes, hex separated by spaces |

Capture 03 (`tools/can/probe.py`) has `time` (seconds since start), `phase` (`pre` / `tx` / `post`), `id`, `own` (1 = frame sent by us: 0x7F7 and 0x7F5), `dlc`, `data`.

## Notes for using the data

- Most cyclic IDs are E2E protected: byte 0 is a CRC, byte 1 bits 0-3 an alive counter. Replaying a capture keeps them valid. Generated frames need a correct CRC; how that is calculated is known for some IDs only (`docs/can-bus.md`, `tools/can/e2e.py`).
- What each ID contains, byte by byte: `docs/can-ids.md`.
