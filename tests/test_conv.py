"""
Tests for the conv module.
"""

import struct
from unittest import TestCase

from skreader.conv import (
    FloatToStr,
    LuxFloatToStr,
    ParseDouble,
    ParseFloat,
)


class TestConv(TestCase):
    """Test conversion functions from skreader.conv."""

    def test_parse_float(self) -> None:
        """Test the ParseFloat function."""
        # Create a bytes object containing a float in big-endian format
        test_float = 123.456
        data = struct.pack(">f", test_float)
        # Add extra data to test position parameter
        full_data = b"prefix" + data + b"suffix"
        result = ParseFloat(full_data, 6)
        # Use assertAlmostEqual because floating point comparisons
        self.assertAlmostEqual(result, test_float, places=5)

    def test_parse_double(self) -> None:
        """Test the ParseDouble function."""
        # Create a bytes object containing a double in big-endian format
        test_double = 123.456789
        data = struct.pack(">d", test_double)
        # Add extra data to test position parameter
        full_data = b"prefix" + data + b"suffix"
        result = ParseDouble(full_data, 6)
        self.assertAlmostEqual(result, test_double, places=8)

    def test_float_to_str(self) -> None:
        """Test the FloatToStr function with various inputs."""
        # Test normal case
        self.assertEqual(FloatToStr(123.456, 0.0, 1000.0, 2), "123.46")

        # Test with different precision
        self.assertEqual(FloatToStr(123.456, 0.0, 1000.0, 1), "123.5")
        self.assertEqual(FloatToStr(123.456, 0.0, 1000.0, 3), "123.456")

        # Test under limit
        self.assertEqual(FloatToStr(10.0, 20.0, 1000.0, 2), "Under")

        # Test over limit
        self.assertEqual(FloatToStr(2000.0, 0.0, 1000.0, 2), "Over")

    def test_lux_float_to_str(self) -> None:
        """Test the LuxFloatToStr function with various inputs."""
        # Test under limit
        self.assertEqual(LuxFloatToStr(10.0, 20.0, 1000.0), "Under")

        # Test over limit
        self.assertEqual(LuxFloatToStr(2000.0, 0.0, 1000.0), "Over")

        # Test different ranges with their formatting
        # < 9.95 (2 decimal places in original rounding)
        self.assertEqual(LuxFloatToStr(9.25, 0.0, 1000.0), "9.2")

        # 9.95 - 99.95 (1 decimal place)
        self.assertEqual(LuxFloatToStr(54.321, 0.0, 1000.0), "54.3")

        # 99.95 - 999.5 (0 decimal places)
        self.assertEqual(LuxFloatToStr(500.6, 0.0, 1000.0), "501")

        # 999.5 - 9995 (round to nearest 10)
        self.assertEqual(LuxFloatToStr(1234.5, 0.0, 10000.0), "1230")

        # 9995 - 99950 (round to nearest 100)
        self.assertEqual(LuxFloatToStr(12345.6, 0.0, 100000.0), "12300")

        # >= 99950 (round to nearest 1000)
        self.assertEqual(LuxFloatToStr(123456.7, 0.0, 1000000.0), "123000")
