"""Passive CAN sniffer for the candleLight (gs_usb) adapter.

The adapter is always started in listen-only mode: it never transmits,
not even ACK bits, so it cannot disturb the kart's bus.

Usage:
    python sniff.py scan                      # try common bitrates, report which one works
    python sniff.py log -b 500000 -t 30 -o capture.csv
    python sniff.py summary capture.csv
"""

import argparse
import csv
import sys
import time
from collections import defaultdict

import libusb_package
import usb.backend.libusb1
import usb.util
from gs_usb.constants import CAN_ERR_FLAG, GS_CAN_MODE_HW_TIMESTAMP, GS_CAN_MODE_LISTEN_ONLY
from gs_usb.gs_usb import GsUsb
from gs_usb.gs_usb_frame import GsUsbFrame

# gs_usb looks up libusb through pyusb; point it at the DLL shipped with libusb-package.
_backend = libusb_package.get_libusb1_backend()
usb.backend.libusb1.get_backend = lambda *a, **kw: _backend

BITRATES = [500000, 250000, 1000000, 125000]
LISTEN_ONLY = GS_CAN_MODE_LISTEN_ONLY | GS_CAN_MODE_HW_TIMESTAMP


def close_device(dev):
    dev.stop()
    usb.util.dispose_resources(dev.gs_usb)


def open_device(bitrate, listen_only=True):
    devices = GsUsb.scan()
    if not devices:
        sys.exit("No gs_usb / candleLight adapter found.")
    dev = devices[0]
    dev.stop()
    if not dev.set_bitrate(bitrate):
        sys.exit(f"Adapter rejected bitrate {bitrate}.")
    if not listen_only:
        dev.start(GS_CAN_MODE_HW_TIMESTAMP)
        return dev
    dev.start(LISTEN_ONLY)
    if not dev.device_flags & GS_CAN_MODE_LISTEN_ONLY:
        close_device(dev)
        sys.exit("Adapter does not support listen-only mode; refusing to open the bus.")
    return dev


def read_frames(dev, seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        frame = GsUsbFrame()
        if dev.read(frame, 100):
            yield time.time(), frame


def scan(seconds):
    for bitrate in BITRATES:
        dev = open_device(bitrate)
        ok = err = 0
        ids = set()
        for _, f in read_frames(dev, seconds):
            if f.can_id & CAN_ERR_FLAG:
                err += 1
            else:
                ok += 1
                ids.add(f.arbitration_id)
        close_device(dev)
        print(f"{bitrate:>8} bit/s: {ok:5} frames, {err:4} error frames, {len(ids):3} IDs")


def log(bitrate, seconds, out):
    dev = open_device(bitrate)
    n = 0
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["time", "hw_us", "id", "ext", "rtr", "err", "dlc", "data"])
        try:
            for t, f in read_frames(dev, seconds):
                w.writerow([f"{t:.6f}", f.timestamp_us, f"{f.arbitration_id:X}", int(f.is_extended_id),
                            int(f.is_remote_frame), int(f.is_error_frame), f.can_dlc,
                            bytes(f.data[:f.can_dlc]).hex(" ").upper()])
                n += 1
        finally:
            close_device(dev)
    print(f"{n} frames written to {out}")


def summary(path):
    stats = defaultdict(lambda: {"n": 0, "t0": None, "t1": None, "dlc": set(), "vals": defaultdict(set), "last": ""})
    errors = 0
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            if row["err"] == "1":
                errors += 1
                continue
            s = stats[(row["id"], row["ext"])]
            t = float(row["time"])
            s["n"] += 1
            s["t0"] = s["t0"] or t
            s["t1"] = t
            s["dlc"].add(row["dlc"])
            s["last"] = row["data"]
            for i, b in enumerate(row["data"].split()):
                s["vals"][i].add(b)
    print(f"{'ID':>9} ext {'count':>6} {'Hz':>7}  dlc  changing bytes   last data")
    for (cid, ext), s in sorted(stats.items(), key=lambda kv: int(kv[0][0], 16)):
        span = s["t1"] - s["t0"]
        hz = (s["n"] - 1) / span if span > 0 else 0
        changing = [str(i) for i, v in sorted(s["vals"].items()) if len(v) > 1]
        print(f"{cid:>9}  {ext}  {s['n']:6} {hz:7.1f}  {','.join(sorted(s['dlc'])):>3}  "
              f"{(','.join(changing) or '-'):<15}  {s['last']}")
    print(f"\n{len(stats)} IDs, {errors} error frames")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("-t", "--seconds", type=float, default=2)
    l = sub.add_parser("log")
    l.add_argument("-b", "--bitrate", type=int, required=True)
    l.add_argument("-t", "--seconds", type=float, default=30)
    l.add_argument("-o", "--out", required=True)
    m = sub.add_parser("summary")
    m.add_argument("path")
    a = p.parse_args()
    if a.cmd == "scan":
        scan(a.seconds)
    elif a.cmd == "log":
        log(a.bitrate, a.seconds, a.out)
    else:
        summary(a.path)


if __name__ == "__main__":
    main()
