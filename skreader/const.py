"""
Seconic SDK constants.

Based on original C-7000 SDK from Sekonic.
Names are kept as close as possible to the original SDK.
"""

from enum import Enum


class SKF_STATUS_DEVICE(Enum):
    IDLE = 0
    IDLE_OUT_MEAS = 1
    BUSY_FLASH_STANDBY = 2
    BUSY_MEASURING = 3
    BUSY_INITIALIZING = 4
    BUSY_DARK_CALIBRATION = 5
    ERROR_HW = 6


class SKF_STATUS_BUTTON(Enum):
    NONE = 0
    POWER = 1
    MEASURING = 2
    MEMORY = 4
    MENU = 8
    PANEL = 0x10


class SKF_STATUS_RING(Enum):
    UNPOSITIONED = 0
    CAL = 1
    LOW = 2
    HIGH = 3


class SKF_REMOTE(Enum):
    REMOTE_OFF = 0
    REMOTE_ON = 1


class SKF_MEASURING_MODE(Enum):
    AMBIENT = 0
    CORDLESS_FLASH = 1
    CORD_FLASH = 2


class SKF_FIELD_OF_VIEW(Enum):
    _2DEG = 0
    _10DEG = 1


class SKF_EXPOSURE_TIME(Enum):
    AUTO = 0
    _100MSEC = 1
    _1SEC = 2


class SKF_SHUTTER_SPEED(Enum):
    _1SEC = "01"
    _1_2SEC = "02"
    _1_4SEC = "03"
    _1_8SEC = "03"
    _1_15SEC = "05"
    _1_30SEC = "06"
    _1_60SEC = "07"
    _1_125SEC = "08"
    _1_250SEC = "09"
    _1_500SEC = "10"


class SKF_MEASURING_METHOD(Enum):
    SINGLE_MODE = 0
    CONTINUOUS_MODE = 1
