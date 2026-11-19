"""E2E protection used on the kart's CAN bus (reverse engineered, see docs/can-bus.md).

Byte 0 is a CRC8 (polynomial 0x2F), byte 1 bits 0-3 an alive counter (0..15).
Two variants exist:
  * simple:    CRC8H2F, init 0x00, no final XOR, over bytes 1..n
  * profile 2: CRC8H2F, init 0xFF, final XOR 0xFF, over bytes 1..n followed by
               a data ID that depends on the counter value (AUTOSAR E2E profile 2)
"""

SIMPLE_IDS = {
    0x014, 0x200, 0x201, 0x202, 0x203, 0x204, 0x205, 0x215,
    0x220, 0x221, 0x222, 0x223, 0x224, 0x227, 0x228, 0x229, 0x22A, 0x22B,
    0x22E, 0x22F, 0x230, 0x231, 0x232, 0x235, 0x236, 0x237, 0x238, 0x239,
}

# Data ID per counter value 0..15, verified on all captures (01, 02, 05).
PROFILE2_DATA_IDS = {
    0x001: bytes.fromhex("4C A3 A1 2C A4 21 06 98 97 49 58 13 28 8F 68 DB"),
    0x002: bytes.fromhex("F0 76 F7 83 8D C0 6A 9C 40 72 A9 A6 24 9A A5 D6"),
    0x006: bytes.fromhex("A9 95 4F B2 55 30 89 1B 63 1D BC B9 73 11 A3 CB"),
    0x007: bytes.fromhex("55 1D A3 44 1C 2C 9D 1F 21 08 C4 98 0F 01 49 38"),
    0x010: bytes.fromhex("F8 EC 53 C4 30 58 86 F6 37 B9 41 DA 62 E9 94 23"),
}

# CRC scheme NOT known. These tables were fitted on the idle capture only, where the payload
# never changes, so any data ID fits; they fail on the throttle sweep and on capture 05.
# Byte 0 is still a CRC and byte 1 bits 0-3 the alive counter. Kept for reference only.
UNSOLVED_IDS = {
    0x015: bytes.fromhex("90 42 1B C9 A9 7B 22 F0 E2 30 69 BB DB 09 50 82"),
    0x028: bytes.fromhex("FA 88 1E 6C 1D 6F F9 8B 1B 69 FF 8D FC 8E 18 6A"),
    0x064: bytes.fromhex("CA B8 2E 5C 2D 5F C9 BB 2B 59 CF BD CC BE 28 5A"),
    0x078: bytes.fromhex("2B 59 CF BD CC BE 28 5A CA B8 2E 5C 2D 5F C9 BB"),
    0x083: bytes.fromhex("A9 DB 4D 3F 4E 3C AA D8 48 3A AC DE AF DD 4B 39"),
}


def _table(poly):
    t = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = ((c << 1) ^ poly) & 0xFF if c & 0x80 else (c << 1) & 0xFF
        t.append(c)
    return t


_T = _table(0x2F)


def crc8h2f(data, init=0x00, xorout=0x00):
    c = init
    for b in data:
        c = _T[c ^ b]
    return c ^ xorout


def expected_crc(can_id, data):
    """CRC byte for a frame, or None if the ID is not known to be E2E protected."""
    if can_id in SIMPLE_IDS:
        return crc8h2f(data[1:])
    if can_id in PROFILE2_DATA_IDS:
        data_id = PROFILE2_DATA_IDS[can_id][data[1] & 0x0F]
        return crc8h2f(bytes(data[1:]) + bytes([data_id]), 0xFF, 0xFF)
    return None


def check(can_id, data):
    exp = expected_crc(can_id, data)
    return exp is None or exp == data[0]
