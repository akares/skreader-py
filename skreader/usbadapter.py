"""
USB driver interface.

(to avoid pyusb specific calls spread through the main code)
"""

import usb.util
from usb import Device as _pyusbDevice
from usb import Endpoint as _pyusbEndpoint
from usb.core import NoBackendError as _pyusbNoBackendError
from usb.core import USBError as _pyusbUSBError
from usb.core import USBTimeoutError as _pyusbUSBTimeoutError


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
    )


def get_usb_out_endpoint(device: Device) -> Endpoint:
    cfg = device.get_active_configuration()

    if not cfg:
        # set the active configuration. With no arguments, the first
        # configuration will be the active one.
        # Do this only once because fail on second attempt (in Linux).
        device.set_configuration()
        cfg = device.get_active_configuration()

    # get an endpoint instance
    intf = cfg[(0, 0)]

    return usb.util.find_descriptor(
        intf,
        # match the first OUT endpoint
        custom_match=lambda e: (
            usb.util.endpoint_direction(e.bEndpointAddress)
            == usb.util.ENDPOINT_OUT
        ),
    )


def usb_write(out_endpoint: Endpoint, cmd: str) -> None:
    out_endpoint.write(cmd)


def usb_read(
    device: Device, buf_len: int = READ_BUF_LEN, timeout: int = READ_TIMEOUT_MS
) -> bytes:
    return device.read(0x81, buf_len, timeout)


def dispose_resources(device: Device) -> None:
    usb.util.dispose_resources(device)
