"""
Seconic spectral measurement result class.

Based on original C-7000 SDK from Sekonic.
Names are kept as close as possible to the original SDK.
"""

import array

from dataclasses import dataclass, field
from typing import NewType

from .conv import ParseFloat, ParseDouble, FloatToStr, LuxFloatToStr


@dataclass
class TristimulusValue:
    X: str
    Y: str
    Z: str


@dataclass
class CIE1931Value:
    x: str
    y: str
    z: str = field(init=False)

    def __post_init__(self) -> None:
        if self.x == "Under" or self.y == "Under":
            self.z = "Under"
        elif self.x == "Over" or self.y == "Over":
            self.z = "Over"
        else:
            z = 1.0 - float(self.x) - float(self.y)
            self.z = f"{z:.4f}"


@dataclass
class CIE1976Value:
    ud: str
    vd: str


@dataclass
class ColorRenditionIndexesValue:
    Ra: str
    Ri: list[str]


@dataclass
class IlluminanceValue:
    Lux: str
    FootCandle: str


@dataclass
class DominantWavelengthValue:
    Wavelength: str
    ExcitationPurity: str


@dataclass
class ColorTemperatureValue:
    Tcp: str
    Delta_uv: str


PhotosyntheticPhotonFluxDensityValue = NewType(
    "PhotosyntheticPhotonFluxDensityValue", str
)
PeakWavelengthValue = NewType("PeakWavelengthValue", str)


# TODO: Not implemented here but available for C-7000 FW > 25 extended data:
# TM30, SSI, TLCI


@dataclass(init=False)
class MeasurementResult:
    """
    MeasurementResult represents a measurement data from SEKONIC device.

    Data format is based on original C-7000 SDK from SEKONIC (distributed only
    as Windows DLL).
    """

    Tristimulus: TristimulusValue  # Tristimulus values in XYZ color space
    CIE1931: CIE1931Value  # CIE 1931 (x, y, z) chromaticity coordinates
    CIE1976: CIE1976Value  # CIE 1976 (u', v') chromaticity coordinates
    ColorTemperature: ColorTemperatureValue  # Correlated Color Temperature
    ColorRenditionIndexes: ColorRenditionIndexesValue  # Color Rendition Indexes
    Illuminance: IlluminanceValue  # Illuminance (LUX)
    DWL: DominantWavelengthValue  # Dominant Wavelength
    PPFD: PhotosyntheticPhotonFluxDensityValue  # Photosynthetic Photon Flux Density
    PeakWavelength: PeakWavelengthValue  # Peak Wavelength
    SpectralData_1nm: list[float]  # Spectral Data 380-780nm (1nm step)
    SpectralData_5nm: list[float]  # Spectral Data 380-780nm (5nm step)
    LimFlag: int  # 0 if no limits exceeded during measurement

    def __init__(self, data: array.array) -> None:
        if len(data) != 2380:
            raise ValueError(
                f"Invalid measurement data size {len(data)} != 2380"
            )

        # SKF_MEASURING_MODE.AMBIENT only!
        self.ColorTemperature = ColorTemperatureValue(
            Tcp=FloatToStr(ParseFloat(data, 50), 1563, 100000, 0),
            Delta_uv=FloatToStr(ParseFloat(data, 55), -0.1, 0.1, 4),
        )
        # Limit the CCT value (SK C-800 returns Tcp=50000 value instead of "Over" as C-7000 does)
        if self.ColorTemperature.Delta_uv in ["Under", "Over"]:
            self.ColorTemperature.Tcp = self.ColorTemperature.Delta_uv

        # SKF_MEASURING_MODE.AMBIENT only!
        self.Illuminance = IlluminanceValue(
            Lux=LuxFloatToStr(ParseFloat(data, 271), 100, 200000),
            FootCandle=LuxFloatToStr(
                ParseFloat(data, 276),
                0.093000002205371857,
                18580.607421875,
            ),
        )

        self.Tristimulus = TristimulusValue(
            X=FloatToStr(ParseDouble(data, 281), 0, 1000000, 4),
            Y=FloatToStr(ParseDouble(data, 290), 0, 1000000, 4),
            Z=FloatToStr(ParseDouble(data, 299), 0, 1000000, 4),
        )

        self.CIE1931 = CIE1931Value(
            x=FloatToStr(ParseFloat(data, 308), 0, 1, 4),
            y=FloatToStr(ParseFloat(data, 313), 0, 1, 4),
        )

        self.CIE1976 = CIE1976Value(
            ud=FloatToStr(ParseFloat(data, 328), 0, 1, 4),
            vd=FloatToStr(ParseFloat(data, 333), 0, 1, 4),
        )

        self.DWL = DominantWavelengthValue(
            Wavelength=FloatToStr(ParseFloat(data, 338), -780, 780, 0),
            ExcitationPurity=FloatToStr(ParseFloat(data, 343), 0, 100, 1),
        )

        self.ColorRenditionIndexes = ColorRenditionIndexesValue(
            Ra=FloatToStr(ParseFloat(data, 348), -100, 100, 1),
            Ri=[
                FloatToStr(ParseFloat(data, 353 + i * 5), -100, 100, 1)
                for i in range(14)
            ],
        )

        lux_under, lux_over = (
            self.Illuminance.Lux == "Under",
            self.Illuminance.Lux == "Over",
        )

        # Boundaries check

        self.PeakWavelength = PeakWavelengthValue("")
        if lux_under:
            self.SpectralData_5nm = [0.0] * 80
            self.SpectralData_1nm = [0.0] * 400
        elif lux_over:
            self.SpectralData_5nm = [9999.9] * 80
            self.SpectralData_1nm = [9999.9] * 400
        else:
            self.SpectralData_5nm = [
                ParseFloat(data, 428 + i * 4) for i in range(81)
            ]
            self.SpectralData_1nm = [
                ParseFloat(data, 753 + i * 4) for i in range(401)
            ]
            self.PeakWavelength = PeakWavelengthValue(
                str(
                    380
                    + self.SpectralData_1nm.index(max(self.SpectralData_1nm))
                )
            )

        self.PPFD = PhotosyntheticPhotonFluxDensityValue(
            FloatToStr(ParseFloat(data, 2376), 0, 9999.9, 1)
        )

        # Boundaries extra check

        if not lux_under and not lux_over and float(self.Illuminance.Lux) < 5:
            self.ColorTemperature.Tcp = "Under"
            self.ColorTemperature.Delta_uv = "Under"
            self.CIE1931.x = "Under"
            self.CIE1931.y = "Under"
            self.CIE1931.z = "Under"
            self.CIE1976.ud = "Under"
            self.CIE1976.vd = "Under"
            self.DWL.Wavelength = "Under"
            self.DWL.ExcitationPurity = "Under"
            self.ColorRenditionIndexes.Ra = "Under"
            self.ColorRenditionIndexes.Ri = ["Under"] * 14

        if (
            self.ColorTemperature.Tcp == "Under"
            or self.ColorTemperature.Tcp == "Over"
        ):
            self.ColorTemperature.Delta_uv = self.ColorTemperature.Tcp
            self.ColorRenditionIndexes.Ra = self.ColorTemperature.Tcp
            self.ColorRenditionIndexes.Ri = [self.ColorTemperature.Tcp] * 14

        if self.Tristimulus.X == "Under" or self.Tristimulus.X == "Over":
            self.PeakWavelength = PeakWavelengthValue(self.Tristimulus.X)

        self.LimFlag = 0
        if lux_under:
            self.LimFlag = 1
        elif lux_over:
            self.LimFlag = 2
        elif float(self.Illuminance.Lux) < 5:
            self.LimFlag = 3

    def __str__(self) -> str:
        return (
            f"lux={self.Illuminance.Lux} "
            f"x={self.CIE1931.x} "
            f"y={self.CIE1931.y} "
            f"CCT={self.ColorTemperature.Tcp}"
        )
