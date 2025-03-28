"""
Helper utils for Seconic specific measurements conversions.

Based on original C-7000 SDK from Sekonic.
Names are kept as close as possible to the original SDK.
"""

import struct


def ParseFloat(data, pos):
    return struct.unpack(">f", data[pos : pos + 4])[0]


def ParseDouble(data, pos):
    return struct.unpack(">d", data[pos : pos + 8])[0]


def FloatToStr(val, low_limit, high_limit, ndigits):
    if val < low_limit:
        return "Under"

    if val > high_limit:
        return "Over"

    return f"{val:.{ndigits}f}"


def LuxFloatToStr(val, low_limit, high_limit):
    if val < 9.9499998092651367:
        val = round(val, 2)
    elif val < 99.949996948242188:
        val = round(val, 1)
    elif val < 999.5:
        val = round(val, 0)
    elif val < 9995.0:
        val = round(val / 10.0, 0) * 10.0
    elif val < 99950.0:
        val = round(val / 100.0, 0) * 100.0
    else:
        val = round(val / 1000.0, 0) * 1000.0

    if val < low_limit:
        return "Under"

    if val > high_limit:
        return "Over"

    if val < 100.0:
        return f"{val:.1f}"

    return f"{val:.0f}"
