"""Read and change the kart configuration through the Rotax MAX Dome connectivity interface.

Implements reference_docs/2020_12_04_MAXDome_InterfaceSpec (REV05):
  requests  0x7F3 gear, 0x7F4 boost, 0x7F5 vMax, 0x7F6 map, 0x7F8 parity,
            each framed by the life counter 0x7F7 (byte 7, bits 0-3)
  feedback  0x7D1 kart status, 0x7D2 boost status (cyclic, 100 ms)

Usage:
    python config.py status [--save backup.json]   # listen-only
    python config.py set-vmax 30                   # transmits, then verifies via 0x7D1
    python config.py restore backup.json           # transmits saved vMax, boost and parity
"""

import argparse
import json
import sys
import time

from gs_usb.gs_usb_frame import GS_USB_NONE_ECHO_ID, GsUsbFrame

from sniff import close_device, open_device, read_frames

BITRATE = 500000

ID_GEAR, ID_BOOST, ID_VMAX, ID_MAP, ID_COUNTER, ID_PARITY = 0x7F3, 0x7F4, 0x7F5, 0x7F6, 0x7F7, 0x7F8
ID_STAT, ID_BOOST_STAT = 0x7D1, 0x7D2

# Send requests with DLC 8 (zero padded) instead of the minimal length from the spec.
PAD_DLC8 = False


def decode_stat(d):
    return {
        "drive": bool(d[0] & 0x01),
        "enable_drive": bool(d[0] & 0x02),
        "charging": bool(d[0] & 0x04),
        "limp_home": bool(d[0] & 0x08),
        "key_position": d[0] >> 6,
        "vmax_kmh": d[1] + 5,
        "map": d[2] & 0x03,
        "gear": (d[2] >> 2) & 0x03,
        "parity_f": round(0.1 + d[3] * 0.9 / 255, 3),
        "parity_f_pwr": min(d[4] / 10, 1.0),
        "raw": d.hex(" "),
    }


def decode_boost(d):
    return {
        "enabled": bool(d[0] & 0x01),
        "requested": bool(d[0] & 0x02),
        "active": bool(d[0] & 0x04),
        "ready": bool(d[0] & 0x08),
        "t_boost_max_s": d[1] * 0.5,
        "t_chg_max_s": d[2] * 0.5,
        "n_boost": d[3] - 256 if d[3] > 127 else d[3],
        "f_map_boost": round(1 + d[4] * 0.01, 2),
        "t_boost_s": d[5] * 0.5,
        "t_chg_s": d[6] * 0.5,
        "raw": d.hex(" "),
    }


def read_status(dev, seconds=1.0):
    stat = boost = None
    for _, f in read_frames(dev, seconds):
        data = bytes(f.data[:f.can_dlc])
        if f.arbitration_id == ID_STAT:
            stat = data
        elif f.arbitration_id == ID_BOOST_STAT:
            boost = data
    return stat, boost


def encode_vmax(kmh):
    if not 5 <= kmh <= 260:
        sys.exit("vMax must be within 5..260 km/h.")
    return [round(kmh) - 5]


def encode_boost(b):
    return [int(b["enabled"]), round(b["t_boost_max_s"] / 0.5), round(b["t_chg_max_s"] / 0.5),
            b["n_boost"] & 0xFF, round((b["f_map_boost"] - 1) / 0.01)]


def encode_parity(s):
    return [round((s["parity_f"] - 0.1) * 255 / 0.9), round(s["parity_f_pwr"] * 10)]


def send(dev, can_id, data):
    """Transmit one frame and wait for the adapter's echo, which only comes back once the frame was ACKed."""
    dev.send(GsUsbFrame(can_id, list(data)))
    for _, f in read_frames(dev, 0.5):
        if f.echo_id != GS_USB_NONE_ECHO_ID and f.arbitration_id == can_id:
            return
    raise RuntimeError(f"No echo for 0x{can_id:X}: frame was not acknowledged on the bus.")


def run_session(dev, requests, check, lead=1.0, timeout=3.0):
    """Send the life counter every 100 ms (spec 3.1), the requests after `lead` seconds,
    and keep the counter running until 0x7D1/0x7D2 confirm the change or `timeout` expires."""
    counter = 0
    start = next_tx = time.monotonic()
    sent_at = None
    stat = boost = None
    while True:
        now = time.monotonic()
        if now >= next_tx:
            send(dev, ID_COUNTER, [0] * 7 + [counter])
            counter = (counter + 1) & 0x0F
            next_tx += 0.1
        if sent_at is None and now - start >= lead:
            for can_id, data in requests:
                if PAD_DLC8:
                    data = list(data) + [0] * (8 - len(data))
                send(dev, can_id, data)
                print(f"  sent 0x{can_id:X}: {bytes(data).hex(' ')} (counter running)")
            sent_at = now
        for _, f in read_frames(dev, 0.02):
            if f.echo_id != GS_USB_NONE_ECHO_ID:
                continue
            if f.arbitration_id == ID_STAT:
                stat = bytes(f.data[:f.can_dlc])
            elif f.arbitration_id == ID_BOOST_STAT:
                boost = bytes(f.data[:f.can_dlc])
        if sent_at is not None and stat:
            st = decode_stat(stat)
            if check(st, decode_boost(boost) if boost else None):
                return True, st
            if now - sent_at > timeout:
                return False, st


def require_stat(stat):
    if stat is None:
        sys.exit("No 0x7D1 status frame received; is the kart on?")
    return decode_stat(stat)


def cmd_status(save):
    dev = open_device(BITRATE)
    try:
        stat, boost = read_status(dev)
    finally:
        close_device(dev)
    result = {"stat": require_stat(stat), "boost": decode_boost(boost) if boost else None}
    print(json.dumps(result, indent=2))
    if save:
        result["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(save, "w") as fh:
            json.dump(result, fh, indent=2)
        print(f"saved to {save}")


def apply(requests, check):
    dev = open_device(BITRATE, listen_only=False)
    try:
        before = require_stat(read_status(dev)[0])
        print(f"before: {before}")
        ok, after = run_session(dev, requests, check)
        print(f"{'confirmed' if ok else 'NOT confirmed within 3 s'}: {after}")
    finally:
        close_device(dev)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("--save")
    v = sub.add_parser("set-vmax")
    v.add_argument("kmh", type=int)
    r = sub.add_parser("restore")
    r.add_argument("path")
    p.add_argument("--dlc8", action="store_true", help="pad requests to 8 bytes")
    a = p.parse_args()
    global PAD_DLC8
    PAD_DLC8 = a.dlc8

    if a.cmd == "status":
        cmd_status(a.save)
    elif a.cmd == "set-vmax":
        apply([(ID_VMAX, encode_vmax(a.kmh))], lambda st, _: st["vmax_kmh"] == a.kmh)
    else:
        saved = json.load(open(a.path))
        st, bo = saved["stat"], saved["boost"]
        requests = [(ID_VMAX, encode_vmax(st["vmax_kmh"])), (ID_PARITY, encode_parity(st))]
        if bo:
            requests.append((ID_BOOST, encode_boost(bo)))

        def check(now, boost):
            return (now["vmax_kmh"] == st["vmax_kmh"] and now["parity_f"] == st["parity_f"]
                    and (bo is None or (boost and boost["raw"][:14] == bo["raw"][:14])))
        apply(requests, check)


if __name__ == "__main__":
    main()
