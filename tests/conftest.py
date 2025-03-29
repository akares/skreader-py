"""
Shared fixtures for pytest tests.
"""

from typing import Any, Dict, Generator

import pytest
from unittest.mock import MagicMock, patch

from skreader.testdata import ret_ok, ret_under_1, ret_under_2
from skreader.device import DeviceInfo, MeasConfig
from skreader.const import (
    SKF_STATUS_BUTTON,
    SKF_STATUS_DEVICE,
    SKF_STATUS_RING,
    SKF_REMOTE,
    SKF_MEASURING_MODE,
    SKF_FIELD_OF_VIEW,
    SKF_EXPOSURE_TIME,
    SKF_SHUTTER_SPEED,
)


@pytest.fixture
def mock_device() -> Generator[MagicMock, None, None]:
    """Fixture for mocking the Device class."""
    with patch("skreader.controller.Device") as mock:
        device_instance = mock.return_value

        # Set up default behaviors
        device_instance.model_name = "C-7000"
        device_instance.fw_version = 27
        device_instance.found = True
        device_instance.is_connected = True

        # Mock device info response for ready device
        device_instance.cmd_get_device_info.return_value = DeviceInfo(
            status=SKF_STATUS_DEVICE.IDLE,
            remote=SKF_REMOTE.REMOTE_OFF,
            button=SKF_STATUS_BUTTON.NONE,
            ring=SKF_STATUS_RING.LOW,
        )

        # Mock measurement result
        device_instance.cmd_get_measuring_result.return_value.return_value = (
            ret_ok
        )

        yield device_instance


@pytest.fixture
def mock_usb_device() -> Generator[Dict[str, Any], None, None]:
    """Fixture for mocking USB device operations."""
    with (
        patch("skreader.usbadapter.get_usb_device") as mock_get_device,
        patch("skreader.usbadapter.get_usb_out_endpoint") as mock_get_endpoint,
        patch("skreader.usbadapter.usb_write") as mock_write,
        patch("skreader.usbadapter.usb_read") as mock_read,
        patch("skreader.usbadapter.dispose_resources") as mock_dispose,
    ):

        # Set up default behaviors
        mock_device = MagicMock()
        mock_endpoint = MagicMock()

        mock_get_device.return_value = mock_device
        mock_get_endpoint.return_value = mock_endpoint

        # Set up the read values for successful command acknowledgement
        mock_read.side_effect = [
            bytes([6, 48]),  # Command acknowledge
            b"MN@@@C-7000",  # Model name
        ]

        yield {
            "device": mock_device,
            "endpoint": mock_endpoint,
            "get_device": mock_get_device,
            "get_endpoint": mock_get_endpoint,
            "write": mock_write,
            "read": mock_read,
            "dispose": mock_dispose,
        }


@pytest.fixture
def measurement_data() -> Dict[str, bytes]:
    """Fixture providing different measurement data samples."""
    return {"normal": ret_ok, "under_1": ret_under_1, "under_2": ret_under_2}


@pytest.fixture
def meas_config() -> MeasConfig:
    """Fixture providing a standard measurement configuration."""
    return MeasConfig(
        measuring_mode=SKF_MEASURING_MODE.AMBIENT,
        field_of_view=SKF_FIELD_OF_VIEW._2DEG,
        exposure_time=SKF_EXPOSURE_TIME.AUTO,
        shutter_speed=SKF_SHUTTER_SPEED._1_125SEC,
    )
