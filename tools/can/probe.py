"""Send the life counter (and optionally one request) while logging the whole bus.

Used to find out whether any node reacts to the configuration interface at all.
Phases in the log: pre (silent), tx (counter running), post (silent).

Usage:
    python probe.py -o ../../captures/03_probe.csv [--request 7F5:19] [--counter-data 00000000000000]
"""

import argparse
import csv
import time

from gs_usb.gs_usb_frame import GS_USB_NONE_ECHO_ID, GsUsbFrame

from config import BITRATE, ID_COUNTER
from sniff import close_device, open_device


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--request", action="append", default=[], help="ID:hexdata, sent 1 s into the tx phase")
    p.add_argument("--counter-data", default="00" * 7, help="hex for bytes 0-6 of 0x7F7")
    p.add_argument("--pre", type=float, default=2)
    p.add_argument("--tx", type=float, default=4)
    p.add_argument("--post", type=float, default=3)
    a = p.parse_args()

    requests = [(int(i, 16), list(bytes.fromhex(d))) for i, d in (r.split(":") for r in a.request)]
    head = list(bytes.fromhex(a.counter_data))
    dev = open_device(BITRATE, listen_only=False)
    start = time.monotonic()
    next_tx = start + a.pre
    counter = 0
    sent = False
    n = 0
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["time", "phase", "id", "own", "dlc", "data"])
        try:
            while True:
                t = time.monotonic() - start
                if t > a.pre + a.tx + a.post:
                    break
                phase = "pre" if t < a.pre else "tx" if t < a.pre + a.tx else "post"
                if phase == "tx" and time.monotonic() >= next_tx:
                    dev.send(GsUsbFrame(ID_COUNTER, head + [counter]))
                    counter = (counter + 1) & 0x0F
                    next_tx += 0.1
                if phase == "tx" and not sent and t >= a.pre + 1:
                    for can_id, data in requests:
                        dev.send(GsUsbFrame(can_id, data))
                    sent = True
                f = GsUsbFrame()
                if dev.read(f, 10):
                    own = int(f.echo_id != GS_USB_NONE_ECHO_ID)
                    w.writerow([f"{t:.4f}", phase, f"{f.arbitration_id:X}", own, f.can_dlc,
                                bytes(f.data[:f.can_dlc]).hex(" ").upper()])
                    n += 1
        finally:
            close_device(dev)
    print(f"{n} frames written to {a.out}")


if __name__ == "__main__":
    main()
