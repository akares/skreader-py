"""
Seconic USB device handler class.

Based on original C-7000 SDK from Sekonic.
"""

import array
from dataclasses import dataclass

from . import usbadapter
from .const import *
from .measurement import MeasurementResult

SK_VENDOR_ID = 0x0A41  # SEKONIC
SK_PRODUCT_ID = 0x7003  # SPECTROMASTER

RESP_OK = array.array("B", [6, 48])


class DeviceNotFoundError(Exception):
    pass


class USBEndpointNotFoundError(Exception):
    pass


class CommandError(Exception):
    pass


@dataclass
class MeasConfig:
    # the default values are optimal for automated measurement
    measuring_mode: SKF_MEASURING_MODE = SKF_MEASURING_MODE.AMBIENT
    field_of_view: SKF_FIELD_OF_VIEW = SKF_FIELD_OF_VIEW._2DEG
    exposure_time: SKF_EXPOSURE_TIME = SKF_EXPOSURE_TIME.AUTO
    shutter_speed: SKF_SHUTTER_SPEED = SKF_SHUTTER_SPEED._1_125SEC


@dataclass
class DeviceInfo:
    status: SKF_STATUS_DEVICE
    remote: SKF_REMOTE
    button: SKF_STATUS_BUTTON
    ring: SKF_STATUS_RING


class Device:
    device: usbadapter.Device
    out_endpoint: usbadapter.Endpoint

    model_name: str
    fw_version: int

    meas_config: MeasConfig

    is_connected: bool

    def __init__(self) -> None:
        self.init_usb()

        self.meas_config = MeasConfig()  # using default values set in dataclass
        self.model_name = self.cmd_get_device_model_name()
        self.fw_version = self.cmd_get_device_fw_version()

    def __str__(self) -> str:
        if not self.is_connected:
            return "Not connected"
        if self.device is None:
            return "Device not found"
        return f"{self.device.manufacturer} {self.model_name} FW v{self.fw_version}"  # type: ignore

    def init_usb(self) -> None:
        try:
            self.device = usbadapter.get_usb_device(SK_VENDOR_ID, SK_PRODUCT_ID)
        except usbadapter.NoBackendError as e:
            self.is_connected = False
            raise DeviceNotFoundError(str(e))

        if self.device is None:
            self.is_connected = False
            raise DeviceNotFoundError

        self.out_endpoint = usbadapter.get_usb_out_endpoint(self.device)
        if self.out_endpoint is None:
            self.is_connected = False
            raise USBEndpointNotFoundError

        self.is_connected = True

    @property
    def found(self) -> bool:
        return self.device is not None

    def close(self) -> None:
        if self.device:
            usbadapter.dispose_resources(self.device)
        self.is_connected = False

    def run_cmd_or_error(self, cmd: str, errmsg: str) -> bytes:
        if not self.is_connected:
            self.init_usb()

        assert self.device is not None
        assert self.out_endpoint is not None

        # send command to device
        try:
            usbadapter.usb_write(self.out_endpoint, cmd)
        except usbadapter.USBTimeoutError:
            raise CommandError(errmsg + " (timed out)")
        except usbadapter.USBError as e:
            raise CommandError(errmsg + f" ({str(e)})")

        # check command acknowledge response
        try:
            resp = usbadapter.usb_read(self.device)
            if resp != RESP_OK:
                raise CommandError(errmsg)
        except usbadapter.USBTimeoutError:
            raise CommandError(errmsg + " (timed out)")
        except usbadapter.USBError as e:
            raise CommandError(errmsg + f" ({str(e)})")

        # read main response
        try:
            data = usbadapter.usb_read(self.device)
        except usbadapter.USBTimeoutError:
            raise CommandError(errmsg + " (timed out)")
        except usbadapter.USBError as e:
            raise CommandError(errmsg + f" ({str(e)})")

        return data

    def cmd_get_device_model_name(self) -> str:
        resp = self.run_cmd_or_error("MN", errmsg="cmd_get_device_model_name")
        sret = "".join([chr(x) for x in resp[5:]])
        return sret.strip("\0")

    def cmd_get_device_fw_version(self) -> int:
        resp = self.run_cmd_or_error("FV", errmsg="cmd_get_device_fw_version")
        # full response (chars):
        # FV@@@20,C36E,27,7881,11,B216,14,50CC,17,74EC
        # fw version chars at pos 13 and 14:
        #              27
        sret = "".join([chr(x) for x in resp[13:15]])
        return int(sret.strip("\0"))

    def cmd_get_device_info(self) -> DeviceInfo:
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

    def cmd_set_remote_mode_on(self) -> None:
        self.run_cmd_or_error("RT1", errmsg="cmd_set_remote_mode_on")

    def cmd_set_remote_mode_off(self) -> None:
        self.run_cmd_or_error("RT0", errmsg="cmd_set_remote_mode_off")

    def cmd_set_measurement_configuration(self) -> None:
        if self.model_name != "C-7000":
            return

        # set FIELD_OF_VIEW
        self.run_cmd_or_error(
            f"AGw,{self.meas_config.field_of_view.value}",
            errmsg="cmd_set_measurement_configuration (FIELD_OF_VIEW)",
        )

        # set SKF_MEASURING_MODE
        self.run_cmd_or_error(
            f"MMw,{self.meas_config.measuring_mode.value}",
            errmsg="cmd_set_measurement_configuration (MEASURING_MODE)",
        )

        # set SKF_EXPOSURE_TIME
        self.run_cmd_or_error(
            f"AMw,{self.meas_config.exposure_time.value}",
            errmsg="md_set_measurement_configuration (EXPOSURE_TIME)",
        )

        if self.fw_version > 25:  # C-7000 FW > 25
            # set SKF_SHUTTER_SPEED
            self.run_cmd_or_error(
                f"SSw,0,{self.meas_config.shutter_speed.value}",
                errmsg="cmd_set_measurement_configuration (SHUTTER_SPEED)",
            )

        pass

    def cmd_start_measuring(self) -> None:
        self.run_cmd_or_error("RM0", errmsg="cmd_start_measuring")

    def cmd_get_measuring_result(self) -> MeasurementResult:
        data = self.run_cmd_or_error("NR", errmsg="cmd_get_measuring_result")
        try:
            return MeasurementResult(data)  # type: ignore
        except ValueError as e:
            raise CommandError("cmd_get_measuring_result: " + str(e))
