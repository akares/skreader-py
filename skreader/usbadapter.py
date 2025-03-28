"""
USB driver interface.

(to avoid pyusb specific calls spread through the main code)
"""

import usb

from usb import Device as _pyusbDevice, Endpoint as _pyusbEndpoint
from usb.core import (
    NoBackendError as _pyusbNoBackendError,
    USBError as _pyusbUSBError,
    USBTimeoutError as _pyusbUSBTimeoutError,
)


class NoBackendError(_pyusbNoBackendError): ...


class USBError(_pyusbUSBError): ...


class USBTimeoutError(_pyusbUSBTimeoutError): ...


class Device(_pyusbDevice): ...


class Endpoint(_pyusbEndpoint): ...


READ_BUF_LEN = 4160
READ_TIMEOUT_MS = 10000


def get_usb_device(vendor_id: int, product_id: int) -> Device:
    return usb.core.find(
        idVendor=vendor_id,
        idProduct=product_id,
    )  # type: ignore


def get_usb_out_endpoint(device: Device) -> Endpoint:
    cfg = device.get_active_configuration()  # type: ignore

    if not cfg:
        # set the active configuration. With no arguments, the first
        # configuration will be the active one.
        # Do this only once because fail on second attempt (in Linux).
        device.set_configuration()  # type: ignore
        cfg = device.get_active_configuration()  # type: ignore

    # get an endpoint instance
    intf = cfg[(0, 0)]

    return usb.util.find_descriptor(
        intf,
        # match the first OUT endpoint
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
        == usb.util.ENDPOINT_OUT,
    )  # type: ignore


def usb_write(out_endpoint: Endpoint, cmd: str) -> None:
    out_endpoint.write(cmd)  # type: ignore


def usb_read(
    device: Device, buf_len=READ_BUF_LEN, timeout=READ_TIMEOUT_MS
) -> bytes:
    return device.read(0x81, buf_len, timeout)  # type: ignore


def dispose_resources(device: Device) -> None:
    usb.util.dispose_resources(device)
