"""
Tests for the MeasurementResult class.
"""

import pytest
from typing import Dict

from skreader.measurement import MeasurementResult


class TestMeasurementResult:
    def test_measurement_result_initialization(
        self, measurement_data: Dict[str, bytes]
    ) -> None:
        """Test that MeasurementResult can be initialized with valid data."""
        result = MeasurementResult(measurement_data["normal"])

        # Basic validation of parsed data
        assert result is not None
        assert hasattr(result, "ColorTemperature")
        assert hasattr(result, "Illuminance")
        assert hasattr(result, "CIE1931")
        assert hasattr(result, "SpectralData_1nm")
        assert hasattr(result, "SpectralData_5nm")

        # Check that spectral data has the expected length
        assert len(result.SpectralData_1nm) == 401  # 380-780nm, 1nm steps
        assert (
            len(result.SpectralData_5nm) == 81
        )  # 380-780nm, 5nm steps (including 780)

    def test_measurement_result_initialization_with_under_data(
        self, measurement_data: Dict[str, bytes]
    ) -> None:
        """Test that MeasurementResult handles 'Under' conditions correctly."""
        result = MeasurementResult(measurement_data["under_1"])

        # Check that we can parse this data without errors
        assert result is not None

        # For this specific test data (under_1), verify the expected values
        # The actual values from dumping the object show:
        # Illuminance=IlluminanceValue(Lux='Under', FootCandle='4.7')
        # ColorTemperature=ColorTemperatureValue(Tcp='4007', Delta_uv='0.0066')
        assert result.Illuminance.Lux == "Under"
        assert result.Illuminance.FootCandle == "4.7"

        # Even when Lux is "Under", other values may still be valid
        assert result.ColorTemperature.Tcp == "4007"
        assert result.ColorTemperature.Delta_uv == "0.0066"

        # Test with under_2 to see if it behaves differently
        result2 = MeasurementResult(measurement_data["under_2"])
        assert result2 is not None

    def test_cie1931_post_init_calculation(self) -> None:
        """Test that CIE1931Value calculates z correctly in __post_init__."""
        from skreader.measurement import CIE1931Value

        # Normal case: z should be calculated as 1.0 - x - y
        value = CIE1931Value(x="0.3127", y="0.3290")
        assert value.z == "0.3583"  # 1.0 - 0.3127 - 0.3290 = 0.3583

        # Under case: z should be "Under"
        value = CIE1931Value(x="Under", y="0.3290")
        assert value.z == "Under"

        value = CIE1931Value(x="0.3127", y="Under")
        assert value.z == "Under"

        # Over case: z should be "Over"
        value = CIE1931Value(x="Over", y="0.3290")
        assert value.z == "Over"

        value = CIE1931Value(x="0.3127", y="Over")
        assert value.z == "Over"

    def test_invalid_measurement_data_size(self) -> None:
        """Test that MeasurementResult raises an error for invalid data size."""
        with pytest.raises(ValueError, match="Invalid measurement data size"):
            MeasurementResult(bytes([0, 1, 2, 3]))  # Too small data

    def test_measurement_result_string_representation(
        self, measurement_data: Dict[str, bytes]
    ) -> None:
        """Test the string representation of MeasurementResult."""
        result = MeasurementResult(measurement_data["normal"])

        # Test that __str__ produces a non-empty string
        str_repr = str(result)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
