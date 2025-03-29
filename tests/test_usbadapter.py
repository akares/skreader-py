"""
Tests for the usbadapter module.
"""

from unittest.mock import MagicMock, patch

from skreader import usbadapter
from skreader.usbadapter import (
    NoBackendError,
    USBError,
    USBTimeoutError,
    get_usb_device,
    get_usb_out_endpoint,
    usb_write,
    usb_read,
    dispose_resources,
)


class TestUSBAdapter:
    """Tests for the usbadapter module."""

    def test_get_usb_device(self) -> None:
        """Test get_usb_device function."""
        with patch("usb.core.find") as mock_find:
            # Mock the usb.core.find call
            device = MagicMock()
            mock_find.return_value = device

            # Call the function
            result = get_usb_device(0x0123, 0x4567)

            # Verify the function called usb.core.find with correct parameters
            mock_find.assert_called_once_with(idVendor=0x0123, idProduct=0x4567)
            assert result == device

    def test_get_usb_out_endpoint_with_active_config(self) -> None:
        """Test get_usb_out_endpoint function when configuration is active."""
        # Mock objects
        device = MagicMock()
        cfg = MagicMock()
        intf = MagicMock()
        endpoint = MagicMock()

        # Set up the mocks
        device.get_active_configuration.return_value = cfg
        cfg.__getitem__.return_value = intf

        with patch("usb.util.find_descriptor", return_value=endpoint):
            # Call the function
            result = get_usb_out_endpoint(device)

            # Verify results
            assert result == endpoint
            # Should not be called since config is active
            device.set_configuration.assert_not_called()
            cfg.__getitem__.assert_called_once_with((0, 0))

    def test_get_usb_out_endpoint_without_active_config(self) -> None:
        """Test get_usb_out_endpoint function when config is not active."""
        # Mock objects
        device = MagicMock()
        cfg = MagicMock()
        intf = MagicMock()
        endpoint = MagicMock()

        # Set up the mocks - first return None to simulate no active config
        device.get_active_configuration.side_effect = [None, cfg]
        cfg.__getitem__.return_value = intf

        with patch("usb.util.find_descriptor", return_value=endpoint):
            # Call the function
            result = get_usb_out_endpoint(device)

            # Verify results
            assert result == endpoint
            # Should be called to set the configuration
            device.set_configuration.assert_called_once()
            cfg.__getitem__.assert_called_once_with((0, 0))

    def test_usb_write(self) -> None:
        """Test usb_write function."""
        # Mock endpoint
        endpoint = MagicMock()

        # Call the function
        usb_write(endpoint, "TEST")

        # Verify endpoint.write was called with the command
        endpoint.write.assert_called_once_with("TEST")

    def test_usb_read(self) -> None:
        """Test usb_read function."""
        # Mock device
        device = MagicMock()
        device.read.return_value = b"DATA"

        # Test with default parameters
        result = usb_read(device)
        device.read.assert_called_once_with(
            0x81, usbadapter.READ_BUF_LEN, usbadapter.READ_TIMEOUT_MS
        )
        assert result == b"DATA"

        # Test with custom parameters
        device.read.reset_mock()
        result = usb_read(device, 1000, 5000)
        device.read.assert_called_once_with(0x81, 1000, 5000)
        assert result == b"DATA"

    def test_dispose_resources(self) -> None:
        """Test dispose_resources function."""
        # Mock device
        device = MagicMock()

        with patch("usb.util.dispose_resources") as mock_dispose:
            # Call the function
            dispose_resources(device)

            # Verify usb.util.dispose_resources was called with the device
            mock_dispose.assert_called_once_with(device)

    def test_exception_classes(self) -> None:
        """Test exception classes are properly subclassed."""
        assert issubclass(NoBackendError, Exception)
        assert issubclass(USBError, Exception)
        assert issubclass(USBTimeoutError, Exception)
