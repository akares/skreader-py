"""
Seconic spectrometer controller class.

This is the main library class used to interface with the Sekonic device.
"""

from __future__ import annotations

import time

from .const import SKF_STATUS_BUTTON, SKF_STATUS_DEVICE, SKF_STATUS_RING
from .device import (
    CommandError,
    DeviceNotFoundError,
    USBEndpointNotFoundError,
    MeasurementResult,
    Device,
    DeviceInfo,
)
from .testdata import ret_ok as FAKE_MEASUREMENT

FAKE_MEASUREMENT_DELAY_SEC = 0.1

MAX_CONN_WAIT_TIME_SEC = 5
CONN_WAIT_STEP_SEC = 0.05

MAX_MEAS_WAIT_TIME_SEC = 20
MEAS_WAIT_STEP_SEC = 0.05


class SekonicError(Exception):
    pass


class Sekonic:
    device: Device | None = None

    def measure(self, use_fake_data: bool) -> MeasurementResult:
        """
        Runs one measurement on the connected Sekonic device.
        Raises SekonicError if device is not ready.
        """
        if use_fake_data:
            time.sleep(FAKE_MEASUREMENT_DELAY_SEC)

            return MeasurementResult(FAKE_MEASUREMENT)

        self.ensure_connection()

        assert self.device is not None

        try:
            self.device.cmd_set_remote_mode_on()
            self.device.cmd_set_measurement_configuration()
        except CommandError as e:
            raise SekonicError(f"Error setting up device: {e}")

        try:
            self.device.cmd_start_measuring()
            self.wait_measurement_result()
            meas = self.device.cmd_get_measuring_result()
        except CommandError as e:
            raise SekonicError(f"Error getting measurement: {e}")

        try:
            self.device.cmd_set_remote_mode_off()
        except CommandError as e:
            # TODO: let the caller know that the device is in an unknown state
            pass

        return meas

    def info(self) -> DeviceInfo:
        """
        Returns information about the connected Sekonic device.
        Raises SekonicError if device is not ready.
        """
        if self.device is None:
            self.connect()

        if self.device is None:
            raise SekonicError("Sekonic device not connected")

        try:
            info = self.device.cmd_get_device_info()
        except CommandError as e:
            raise SekonicError(f"Error getting device info: {e}")

        return info

    def ensure_connection(self) -> None:
        """
        Ensures that the Sekonic device is connected.
        Raises SekonicError if device is not ready.
        """
        if self.device is None:
            self.connect()

        if self.device is None:
            raise SekonicError("Sekonic device not connected")

        try:
            self.wait_until_ready()
        except SekonicError as e:
            self.device.close()
            raise e
        except CommandError as e:
            self.device.close()
            raise SekonicError(e)
        except Exception as e:
            self.device.close()
            raise SekonicError(f"{type(e)}: {e}")

    def connect(self) -> None:
        """
        Find first connected to USB Sekonic device.
        """
        try:
            self.device = Device()
        except DeviceNotFoundError as e:
            raise SekonicError(
                "SEKONIC not found" + (f": {e}" if str(e) else "")
            )
        except USBEndpointNotFoundError as e:
            raise SekonicError(f"USB connection failed: {e}")

    def close(self) -> None:
        """
        Close connection to Sekonic device.
        Also switches off remote mode.
        """
        if self.device is None:
            return

        try:
            self.device.cmd_set_remote_mode_off()
        except CommandError:
            # TODO: let the caller know that the device is in an unknown state
            pass

        self.device.close()

    def wait_until_ready(self) -> None:
        """
        Waits for device to be ready for next measurement.
        """
        if self.device is None:
            raise SekonicError("Sekonic device not connected")

        for _ in range(int(MAX_CONN_WAIT_TIME_SEC / CONN_WAIT_STEP_SEC)):
            time.sleep(CONN_WAIT_STEP_SEC)
            try:
                info = self.device.cmd_get_device_info()
            except CommandError as e:
                raise SekonicError(f"Error getting device info: {e}")

            if info.ring != SKF_STATUS_RING.LOW:
                try:
                    self.device.cmd_set_remote_mode_off()
                except CommandError:
                    pass
                raise SekonicError("Ring is not set to LOW position!")

            if info.button == SKF_STATUS_BUTTON.MEASURING:
                try:
                    self.device.cmd_set_remote_mode_off()
                except CommandError:
                    pass
                raise SekonicError("Measuring button is pressed!")

            if info.status in (
                SKF_STATUS_DEVICE.IDLE,
                SKF_STATUS_DEVICE.IDLE_OUT_MEAS,
            ):
                break  # waiting succeeded
        else:
            try:
                self.device.cmd_set_remote_mode_off()
            except CommandError:
                pass

            raise SekonicError("Max connect time exceeded.")

    def wait_measurement_result(self) -> None:
        """
        Waits until device is finished measurement.
        """
        if self.device is None:
            raise SekonicError("Sekonic device not connected")

        for _ in range(int(MAX_MEAS_WAIT_TIME_SEC / MEAS_WAIT_STEP_SEC)):
            time.sleep(MEAS_WAIT_STEP_SEC)

            try:
                info = self.device.cmd_get_device_info()
            except CommandError:
                # ignore error in order to not complicate things
                # if the device is not ready, the loop will timeout anyway
                continue

            if info.status in (
                SKF_STATUS_DEVICE.IDLE,
                SKF_STATUS_DEVICE.IDLE_OUT_MEAS,
            ):
                break  # waiting succeeded
        else:
            try:
                self.device.cmd_set_remote_mode_off()
            except CommandError:
                pass

            raise SekonicError("Max wait time exceeded.")

    @property
    def model_name(self) -> str:
        if self.device is None:
            return ""
        return self.device.model_name

    @property
    def fw_version(self) -> int:
        if self.device is None:
            return 0
        return self.device.fw_version

    def __str__(self) -> str:
        if self.device is None:
            return "Not connected"

        return str(self.device)
