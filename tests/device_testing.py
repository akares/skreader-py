"""
Stub implementations for testing the Device class.
"""

from unittest.mock import MagicMock

from skreader.device import Device, MeasConfig, DeviceInfo, CommandError
from skreader.const import (
    SKF_STATUS_DEVICE,
    SKF_REMOTE,
    SKF_STATUS_BUTTON,
    SKF_STATUS_RING,
)


class StubDevice(Device):
    """
    A stub implementation of Device that doesn't require actual USB hardware.
    """

    def __init__(self) -> None:
        """Initialize with predefined values, skipping USB connection."""
        # Initialize the basic properties without calling parent __init__
        self.model_name = "C-7000"
        self.fw_version = 27
        self.meas_config = MeasConfig()

        # Create a mock device object for the connected state
        self.device = MagicMock()
        self.device.manufacturer = "SEKONIC"

        self.out_endpoint = MagicMock()
        self.is_connected = True

    def __str__(self) -> str:
        """
        Return the string representation of the device.
        Override parent's method to avoid actual USB calls.
        """
        if not self.is_connected:
            return "Not connected"
        if self.device is None:
            return "Device not found"

        return (
            f"{self.device.manufacturer} "
            f"{self.model_name} "
            f"FW v{self.fw_version}"
        )

    @property
    def found(self) -> bool:
        """Return whether the device is found."""
        return self.device is not None

    def init_usb(self) -> None:
        """Mock implementation that does nothing."""
        self.is_connected = True

    def run_cmd_or_error(self, cmd: str, errmsg: str) -> bytes:
        """
        Mock implementation that returns predefined values for commands.

        This avoids the need for actual USB communication.
        """
        if cmd == "MN":
            return b"MN@@@C-7000"
        elif cmd == "FV":
            fw_data = b"FV@@@20,C36E,27,7881,11,B216,14,50CC,17,74EC"
            return fw_data
        elif cmd == "ST":
            # Status: IDLE, remote off, no button, LOW ring
            # This can be overridden in tests by patching run_cmd_or_error
            # The 0x20 sets the ring to LOW (bit 5)
            return bytes([83, 84, 0, 0, 0x20])
        elif cmd == "TEST":
            return b"RESPONSE"
        else:
            return b"DEFAULT"

    def cmd_get_device_info(self) -> DeviceInfo:
        """Return a device info based on the response from run_cmd_or_error."""
        data = self.run_cmd_or_error("ST", errmsg="cmd_get_device_info")
        if len(data[2:]) != 3:
            raise CommandError("cmd_get_device_info")

        sta_1 = data[2]
        sta_2 = data[3]
        key = data[4]

        status = SKF_STATUS_DEVICE.IDLE
        if sta_1 & 0x10 != 0:
            status = SKF_STATUS_DEVICE.ERROR_HW
        elif sta_1 & 1 != 0:
            if sta_2 & 1 != 0:
                status = SKF_STATUS_DEVICE.BUSY_INITIALIZING
            elif sta_2 & 4 != 0:
                status = SKF_STATUS_DEVICE.BUSY_DARK_CALIBRATION
            elif sta_2 & 0x10 != 0:
                status = SKF_STATUS_DEVICE.BUSY_FLASH_STANDBY
            elif sta_2 & 8 != 0:
                status = SKF_STATUS_DEVICE.BUSY_MEASURING
        elif sta_1 & 8 != 0:
            status = SKF_STATUS_DEVICE.IDLE_OUT_MEAS

        if (sta_1 & 2) == 0:
            remote = SKF_REMOTE.REMOTE_OFF
        else:
            remote = SKF_REMOTE.REMOTE_ON

        try:
            button = SKF_STATUS_BUTTON(key & 0x1F)
        except ValueError:
            button = SKF_STATUS_BUTTON.NONE

        try:
            ring = SKF_STATUS_RING((key & 0x60) >> 5)
        except ValueError:
            ring = SKF_STATUS_RING.UNPOSITIONED

        return DeviceInfo(
            status=status,
            remote=remote,
            button=button,
            ring=ring,
        )

    def close(self) -> None:
        """Close the connection."""
        self.is_connected = False
