"""Build a per-ID catalogue of the kart's CAN bus from the captures.

For every CAN ID: frame rate, DLC, E2E variant and CRC check, and per byte whether it is
constant, a counter, or changing (with min/max and the number of distinct values).
For the throttle sweep it also lists bytes and 16-bit words that follow the throttle pedal
or the motor speed, as leads for decoding.

Usage:
    python catalogue.py ../../captures -o ../../docs/can-ids
writes can-ids.csv (one row per ID) and can-ids.md (readable catalogue).
"""

import argparse
import csv
import os
from collections import defaultdict

import numpy as np

from e2e import PROFILE2_DATA_IDS, SIMPLE_IDS, UNSOLVED_IDS, check

CAPTURES = {
    "01": "01_idle_no_throttle.csv",
    "02": "02_throttle_sweep.csv",
    "05": "05_idle_final_state.csv",
}

# Signals already decoded (docs/can-bus.md); used as references for the correlation search.
KNOWN = {
    0x083: {5: "throttle pedal (0.5 %/bit)"},
    0x03C: {(4, 5): "motor speed, int16 LE, rpm"},
    0x010: {4: "motor speed, rev/s"},
    0x015: {2: "vehicle speed (see can-bus.md)"},
    0x050: {(0, 1): "sawtooth counter 0..4000", (6, 7): "DC current?, int16 LE"},
    0x008: {0: "current or power?"},
}


def load(path):
    frames = defaultdict(list)
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("err") == "1" or row.get("rtr") == "1":
                continue
            data = bytes.fromhex(row["data"]) if row["data"] else b""
            frames[int(row["id"], 16)].append((float(row["time"]), data))
    return frames


def e2e_variant(can_id):
    if can_id in SIMPLE_IDS:
        return "simple"
    if can_id in PROFILE2_DATA_IDS:
        return "profile2"
    if can_id in UNSOLVED_IDS:
        return "unsolved"
    return ""


def byte_kind(values, is_e2e, index):
    if is_e2e and index == 0:
        return "CRC"
    v = np.array(values, dtype=int)
    if len(set(v)) == 1:
        return f"const {v[0]:02X}"
    nib = v & 0x0F
    if is_e2e and index == 1 and np.mean(np.diff(nib) % 16 == 1) > 0.95:
        hi = v >> 4
        return "counter (low nibble)" + ("" if len(set(hi)) == 1 else f", high nibble {min(hi)}..{max(hi)}")
    d = np.diff(v) % 256
    if len(v) > 20 and np.mean(d == 1) > 0.95:
        return "counter (+1)"
    return f"{v.min()}..{v.max()} ({len(set(v))})"


def rate(times):
    if len(times) < 2:
        return 0.0
    return (len(times) - 1) / (times[-1] - times[0])


def nice_rate(hz):
    for r in (100, 50, 20, 10, 5, 4, 2, 1):
        if abs(hz - r) / r < 0.15:
            return f"{r} Hz"
    return f"{hz:.1f} Hz"


def reference_series(frames):
    """Throttle and rpm as (times, values) from the sweep."""
    thr = [(t, d[5]) for t, d in frames[0x083] if len(d) > 5]
    rpm = [(t, int.from_bytes(d[4:6], "little", signed=True)) for t, d in frames[0x03C] if len(d) > 5]
    return {"throttle": np.array(thr, dtype=float), "rpm": np.array(rpm, dtype=float)}


def correlations(frames, refs, min_r=0.8):
    leads = defaultdict(list)
    for can_id, fr in frames.items():
        if len(fr) < 20:
            continue
        times = np.array([t for t, _ in fr])
        dlc = min(len(d) for _, d in fr)
        cols = {}
        for i in range(dlc):
            cols[f"b{i}"] = np.array([d[i] for _, d in fr], dtype=float)
        for i in range(dlc - 1):
            cols[f"b{i}-b{i + 1} LE"] = np.array([int.from_bytes(d[i:i + 2], "little", signed=True) for _, d in fr], dtype=float)
            cols[f"b{i}-b{i + 1} BE"] = np.array([int.from_bytes(d[i:i + 2], "big", signed=True) for _, d in fr], dtype=float)
        for name, ref in refs.items():
            r_vals = np.interp(times, ref[:, 0], ref[:, 1])
            if np.std(r_vals) == 0:
                continue
            for col, v in cols.items():
                if np.std(v) == 0:
                    continue
                r = np.corrcoef(v, r_vals)[0, 1]
                if abs(r) >= min_r:
                    leads[can_id].append((abs(r), col, name, r))
    out = {}
    for can_id, items in leads.items():
        best = {}
        for a, col, name, r in sorted(items, reverse=True):
            key = (col.split(" ")[0], name)
            best.setdefault(key, (col, name, r))
        out[can_id] = sorted(best.values(), key=lambda x: -abs(x[2]))[:4]
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("captures")
    p.add_argument("-o", "--out", required=True, help="output path without extension")
    a = p.parse_args()

    caps = {k: load(os.path.join(a.captures, f)) for k, f in CAPTURES.items()}
    leads = correlations(caps["02"], reference_series(caps["02"]))
    ids = sorted(set().union(*[set(c) for c in caps.values()]))

    rows = []
    for can_id in ids:
        var = e2e_variant(can_id)
        fr_all = [f for c in caps.values() for f in c.get(can_id, [])]
        dlcs = sorted({len(d) for _, d in fr_all})
        crc_ok = sum(check(can_id, d) for _, d in fr_all if len(d) > 1)
        idle = caps["01"].get(can_id, [])
        sweep = caps["02"].get(can_id, [])
        dlc = min(dlcs)
        bytes_idle = [byte_kind([d[i] for _, d in idle], bool(var), i) if idle else "" for i in range(dlc)]
        bytes_sweep = [byte_kind([d[i] for _, d in sweep], bool(var), i) if sweep else "" for i in range(dlc)]
        changes_under_load = [i for i in range(dlc) if bytes_idle[i] != bytes_sweep[i] and not bytes_sweep[i].startswith("counter")]
        known = KNOWN.get(can_id, {})
        rows.append({
            "id": f"0x{can_id:03X}",
            "rate": nice_rate(rate([t for t, _ in idle] or [t for t, _ in sweep])),
            "dlc": "/".join(map(str, dlcs)),
            "e2e": var,
            "crc_ok": f"{crc_ok}/{len(fr_all)}" if var in ("simple", "profile2") else "",
            "constant_all_captures": all(len({d for _, d in c.get(can_id, [])}) <= 1 for c in caps.values()),
            "idle_example": idle[0][1].hex(" ").upper() if idle else "",
            "bytes_idle": " | ".join(f"b{i}: {k}" for i, k in enumerate(bytes_idle)),
            "bytes_sweep": " | ".join(f"b{i}: {k}" for i, k in enumerate(bytes_sweep)),
            "changes_under_load": " ".join(f"b{i}" for i in changes_under_load),
            "leads_sweep": "; ".join(f"{c} ~ {n} (r={r:+.2f})" for c, n, r in leads.get(can_id, [])),
            "known": "; ".join(f"{('b' + str(k)) if isinstance(k, int) else 'b%d-b%d' % k}: {v}" for k, v in known.items()),
        })

    with open(a.out + ".csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    with open(a.out + ".md", "w", encoding="utf-8") as fh:
        fh.write("# CAN ID catalogue\n\n")
        fh.write("Generated by `tools/can/catalogue.py` from captures 01 (idle), 02 (throttle sweep) and 05 (idle, end of session). "
                 "Do not edit by hand; rerun the script after new captures.\n\n")
        fh.write("Byte notation: `const XX` = never changes, `a..b (n)` = range and number of distinct values, "
                 "`CRC` / `counter` = E2E protection (see docs/can-bus.md); E2E `unsolved` = byte 0 is a CRC and byte 1 a counter, but the CRC scheme is not known yet. Leads = bytes or 16-bit words whose value follows "
                 "the throttle pedal or the motor speed during the sweep (|r| ≥ 0.8); a lead is a hint, not a decoding.\n\n")
        fh.write("| ID | Rate | DLC | E2E | Known signals | Differs idle vs. sweep | Leads (sweep) |\n|---|---|---|---|---|---|---|\n")
        for r in rows:
            fh.write(f"| {r['id']} | {r['rate']} | {r['dlc']} | {r['e2e']} | {r['known']} | {r['changes_under_load']} | {r['leads_sweep']} |\n")
        fh.write("\n## Bytes per ID\n")
        for r in rows:
            fh.write(f"\n### {r['id']}  ({r['rate']}, DLC {r['dlc']}{', E2E ' + r['e2e'] + (', CRC ok ' + r['crc_ok'] if r['crc_ok'] else ', CRC scheme unknown') if r['e2e'] else ''})\n\n")
            fh.write(f"Example (idle): `{r['idle_example']}`\n\n")
            fh.write("| Byte | Idle | Throttle sweep |\n|---|---|---|\n")
            for bi, bs in zip(r["bytes_idle"].split(" | "), r["bytes_sweep"].split(" | ")):
                name, vi = bi.split(": ", 1)
                vs = bs.split(": ", 1)[1] if ": " in bs else ""
                fh.write(f"| {name} | {vi} | {vs} |\n")
    print(f"{len(rows)} IDs written to {a.out}.csv / .md")


if __name__ == "__main__":
    main()
