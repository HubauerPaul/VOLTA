"""Look for diagnostic (UDS / OBD) responders with read-only requests.

Only functional (broadcast) request IDs that are not used on the kart bus are sent,
so nothing collides with existing traffic. Services used: 0x10 01 (default session),
0x3E (tester present), 0x22 (read data by identifier), OBD mode 01 PID 00.
Every frame on an ID that is not part of the baseline traffic is reported.

Usage:
    python uds_scan.py -o ../../captures/04_uds_scan.csv
"""

import argparse
import csv
import time

from gs_usb.constants import CAN_EFF_FLAG
from gs_usb.gs_usb_frame import GS_USB_NONE_ECHO_ID, GsUsbFrame

from config import BITRATE
from sniff import close_device, open_device

BASELINE_IDS = {
    0x001, 0x002, 0x004, 0x006, 0x007, 0x008, 0x00D, 0x010, 0x014, 0x015, 0x028, 0x03C, 0x050,
    0x064, 0x078, 0x079, 0x083, 0x311, 0x401, 0x500, 0x510, 0x511, 0x512, 0x513, 0x7D1, 0x7D2,
    *range(0x200, 0x216), *range(0x220, 0x23C), *range(0x700, 0x708),
}

REQUESTS = [
    ("default session", [0x02, 0x10, 0x01]),
    ("tester present", [0x02, 0x3E, 0x00]),
    ("VIN F190", [0x03, 0x22, 0xF1, 0x90]),
    ("spare part F187", [0x03, 0x22, 0xF1, 0x87]),
    ("sw version F189", [0x03, 0x22, 0xF1, 0x89]),
    ("hw version F191", [0x03, 0x22, 0xF1, 0x91]),
    ("serial F18C", [0x03, 0x22, 0xF1, 0x8C]),
    ("OBD 01 00", [0x02, 0x01, 0x00]),
]

FUNCTIONAL_IDS = [0x7DF, CAN_EFF_FLAG | 0x18DB33F1]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-o", "--out", required=True)
    a = p.parse_args()

    dev = open_device(BITRATE, listen_only=False)
    hits = 0
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["request_id", "request", "resp_id", "ext", "dlc", "data"])
        try:
            for req_id in FUNCTIONAL_IDS:
                for name, payload in REQUESTS:
                    dev.send(GsUsbFrame(req_id, payload + [0x55] * (8 - len(payload))))
                    end = time.monotonic() + 0.3
                    while time.monotonic() < end:
                        f = GsUsbFrame()
                        if not dev.read(f, 20) or f.echo_id != GS_USB_NONE_ECHO_ID:
                            continue
                        if f.is_extended_id or f.arbitration_id not in BASELINE_IDS:
                            data = bytes(f.data[:f.can_dlc]).hex(" ").upper()
                            w.writerow([f"{req_id & 0x1FFFFFFF:X}", name, f"{f.arbitration_id:X}",
                                        int(f.is_extended_id), f.can_dlc, data])
                            print(f"{req_id & 0x1FFFFFFF:>8X} {name:<16} -> {f.arbitration_id:X}: {data}")
                            hits += 1
        finally:
            close_device(dev)
    print(f"{hits} responses on non-baseline IDs")


if __name__ == "__main__":
    main()
