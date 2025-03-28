# skreader

Python library and command line tool for SEKONIC spectrometers remote control.

Based on original C# SDK for Windows from SEKONIC.

<img src="https://raw.githubusercontent.com/akares/skreader-py/main/doc/Sekonic-C-7000.jpg" width="640" alt="SEKONIC C-7000" />

## Supported (tested) models

- Sekonic C-700
- Sekonic C-800
- Sekonic C-800-U (US Version. Basically the same as C-800)
- Sekonic C-7000 (supports extended measurement configuration: FOV and Exposure Time)

## Supported (tested) platforms

- Darwin
- Windows
- Linux

## Known limitations

Currently **only ambient** measuring mode is supported.

TM-30, SSI and TLCI measurements are available for Sekonic C-7000 with FW version > 25 but parsing of these fields is **not implemented yet**.

## Requirements and platform support

### USB driver

Default implementation uses [pyusb](https://github.com/pyusb/pyusb) wrapper for the libusb library.

You must have [libusb-1.0](https://github.com/libusb/libusb/wiki) installed on your target system to be able to communicate with USB devices.

Installation for different platforms is covered in
[pyusb documentation](https://github.com/pyusb/pyusb?tab=readme-ov-file#requirements-and-platform-support).

_If you use Linux, you probably already have it._\
_If you use Mac or Windows and was using USB devices that needed custom driver, you also probably have it._

## Installation

```sh
pip install skreader
```

## Usage

### Shell command

Info command:

```sh
> skreader info
Device: SEKONIC CORPORATION C-800 FW v12
Model: C-800
Firmware: 12
Status: IDLE
Remote: REMOTE_OFF
Button: NONE LOW
Ring: LOW
```

Measure command:

```sh
> skreader measure --help
Usage: skreader measure [-h] [-l] [-a] [-s] [-i] [-c] [-t] [-x] [-u] [-d] [-r] [-1] [-5] [-v]

Optional Arguments:
  -h, --help            show this help message and exit
  -l, --ldi             include the most interesting data for LDs
  -a, --all             include all measurement data
  -s, --simple          include all simple measurement data (excluding spectra and CRI)
  -i, --illuminance     include illuminance values in Lux and foot-candle units
  -c, --color-temperature
                        include color temperature values in Kelvin and delta-uv units
  -t, --tristimulus     include tristimulus values in XYZ color space
  -x, --cie1931         include CIE1931 (x, y) chromaticity coordinates
  -u, --cie1976         include CIE1976 (u', v') chromaticity coordinates
  -d, --dwl             include dominant wavelength value
  -r, --cri             include CRI (Ra, Ri) values
  -1, --spectra1nm      include spectral data for 1nm wavelength
  -5, --spectra5nm      include spectral data for 5nm wavelength
  -v, --verbose         print more messages
```

Default output:

```sh
> skreader measure
LUX: 179
CCT: 5499
CCT DeltaUv: 0.0021
RA: 96.9
R9: 91.2
```

Only illuminance is printed:

```sh
> skreader measure --illuminance
LUX: 179
Fc: 16.7
```

Combining options:

```sh
> skreader measure --illuminance --color-temperature --cie1931
```

Short version of previous command:

```sh
> skreader measure -icx
```

### Library

```python
import skreader

# Create Sekonic handle (does nothing yet).
sk = skreader.Sekonic()

try:
    # Run one measurement.
    # Raises SekonicError if Sekonic device is not connected or not behaving.
    # Use use_fake_data=True for testing without the device (False is default).
    meas = sk.measure(use_fake_data=False)
    print("Measurement result:", meas)  # lux=132 x=0.3178 y=0.3339 CCT=6205

except skreader.SekonicError as e:
    print("Sekonic error:", str(e))
    exit(1)

except KeyboardInterrupt:
    print("\rInterrupted...")
    sk.close() # Turn off remote control mode before unexpected exit.
    exit(130)
```

## Contribution

### Development setup

As 3.9 is the minimum supported by the library version of Python, it is recommended to use it during development to avoid backward compatibility issues introduced by newer versions.

Poetry is used for dependency management and virtual environment creation. It is recommended to use it for library development.

```sh
poetry env use 3.9
poetry install
poetry run ./skreader/cli.py
```

## License

This project is licensed under the terms of the MIT license.

## Legal notices

All product names, logos, and brands are property of their respective owners. All company, product and service names used in this package are for identification purposes only. Use of these names, logos, and brands does not imply endorsement.

- SEKONIC is a registered trademark of SEKONIC CORPORATION.
- Google is a registered trademark of Google LLC.
- Windows is a registered trademark of Microsoft Corporation.
- Linux is the registered trademark of Linus Torvalds.
