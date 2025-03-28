#!/usr/bin/env python

import argparse
import importlib.metadata
import sys

from rich_argparse import RichHelpFormatter

version = importlib.metadata.version("skreader")

import skreader


def cmd_info(args: argparse.Namespace, sk: skreader.Sekonic) -> None:
    if args.fake_device:
        print("Fake device")
        return

    info = sk.info()

    print("Device:", str(sk))
    print("Model:", sk.model_name)
    print("Firmware:", sk.fw_version)
    print("Status:", info.status.name)
    print("Remote:", info.remote.name)
    print("Button:", info.button.name, info.ring.name)
    print("Ring:", info.ring.name)


def cmd_measure(args: argparse.Namespace, sk: skreader.Sekonic) -> None:
    meas = sk.measure(use_fake_data=args.fake_device)

    show_illuminance = args.illuminance or args.all or args.simple
    show_color_temperature = args.color_temperature or args.all or args.simple
    show_tristimulus = args.tristimulus or args.all or args.simple
    show_cie1931 = args.cie1931 or args.all or args.simple
    show_cie1976 = args.cie1976 or args.all or args.simple
    show_dwl = args.dwl or args.all or args.simple
    show_cri = args.cri or args.all
    show_spectra1nm = args.spectra1nm or args.all
    show_spectra5nm = args.spectra5nm or args.all
    show_ldi = (
        args.ldi
        or args.all
        or (
            not show_illuminance
            and not show_color_temperature
            and not show_tristimulus
            and not show_cie1931
            and not show_cie1976
            and not show_dwl
            and not show_cri
            and not show_spectra1nm
            and not show_spectra5nm
        )
    )

    if show_illuminance:
        if args.verbose:
            print("------------")
            print("Illuminance:")
        print("LUX:", meas.Illuminance.Lux)
        print("Fc:", meas.Illuminance.FootCandle)

    if show_color_temperature:
        if args.verbose:
            print("------------")
            print("ColorTemperature:")
        print("CCT:", meas.ColorTemperature.Tcp)
        print("CCT DeltaUv:", meas.ColorTemperature.Delta_uv)

    if show_tristimulus:
        if args.verbose:
            print("------------")
            print("Tristimulus:")
        print("X:", meas.Tristimulus.X)
        print("Y:", meas.Tristimulus.Y)
        print("Z:", meas.Tristimulus.Z)

    if show_cie1931:
        if args.verbose:
            print("------------")
            print("CIE1931:")
        print("X:", meas.CIE1931.x)
        print("Y:", meas.CIE1931.y)

    if show_cie1976:
        if args.verbose:
            print("------------")
            print("CIE1976:")
        print("Ud:", meas.CIE1976.ud)
        print("Vd:", meas.CIE1976.vd)

    if show_dwl:
        if args.verbose:
            print("------------")
            print("DominantWavelength:")
        print("DominantWavelength:", meas.DWL.Wavelength)
        print("ExcitationPurity:", meas.DWL.ExcitationPurity)

    if show_cri:
        if args.verbose:
            print("------------")
            print("CRI:")
        print("RA:", meas.ColorRenditionIndexes.Ra)
        for i, ri in enumerate(meas.ColorRenditionIndexes.Ri):
            print(f"R{i+1}:", ri)

    if show_spectra1nm:
        if args.verbose:
            print("------------")
            print("SpectralData 1nm:")
        for i, sd in enumerate(meas.SpectralData_1nm):
            wavelength = 380 + i
            print(f"{wavelength},{sd}")

    if show_spectra5nm:
        if args.verbose:
            print("------------")
            print("SpectralData 5nm:")
        for i, sd in enumerate(meas.SpectralData_5nm):
            wavelength = 380 + (i * 5)
            print(f"{wavelength},{sd}")

    if show_ldi:
        if args.verbose:
            print("------------")
        print("LUX:", meas.Illuminance.Lux)
        print("CCT:", meas.ColorTemperature.Tcp)
        print("CCT DeltaUv:", meas.ColorTemperature.Delta_uv)
        print("RA:", meas.ColorRenditionIndexes.Ra)
        print("R9:", meas.ColorRenditionIndexes.Ri[8])


def run():
    parser = argparse.ArgumentParser(
        description="Command line tool for SEKONIC spectrometers remote control.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument(
        "-fake",
        "--fake-device",
        action="store_true",
        help="use fake device for testing",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    subparsers.add_parser(
        "info",
        help="Shows info about the connected device",
        formatter_class=parser.formatter_class,
    )

    meas_parser = subparsers.add_parser(
        "measure",
        help="Runs one measurement and outputs selected data as plain text",
        formatter_class=parser.formatter_class,
    )

    meas_parser.add_argument(
        "-l",
        "--ldi",
        action="store_true",
        help="include the most interesting data for LDs",
    )
    meas_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="include all measurement data",
    )
    meas_parser.add_argument(
        "-s",
        "--simple",
        action="store_true",
        help="include all simple measurement data (excluding spectra and CRI)",
    )
    meas_parser.add_argument(
        "-i",
        "--illuminance",
        action="store_true",
        help="include illuminance values in Lux and foot-candle units",
    )
    meas_parser.add_argument(
        "-c",
        "--color-temperature",
        action="store_true",
        help="include color temperature values in Kelvin and delta-uv units",
    )
    meas_parser.add_argument(
        "-t",
        "--tristimulus",
        action="store_true",
        help="include tristimulus values in XYZ color space",
    )
    meas_parser.add_argument(
        "-x",
        "--cie1931",
        action="store_true",
        help="include CIE1931 (x, y) chromaticity coordinates",
    )
    meas_parser.add_argument(
        "-u",
        "--cie1976",
        action="store_true",
        help="include CIE1976 (u', v') chromaticity coordinates",
    )
    meas_parser.add_argument(
        "-d",
        "--dwl",
        action="store_true",
        help="include dominant wavelength value",
    )
    meas_parser.add_argument(
        "-r",
        "--cri",
        action="store_true",
        help="include CRI (Ra, Ri) values",
    )
    meas_parser.add_argument(
        "-1",
        "--spectra1nm",
        action="store_true",
        help="include spectral data for 1nm wavelength",
    )
    meas_parser.add_argument(
        "-5",
        "--spectra5nm",
        action="store_true",
        help="include spectral data for 5nm wavelength",
    )
    meas_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print more messages",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    sk = skreader.Sekonic()

    try:
        if args.command == "info":
            cmd_info(args, sk)
        elif args.command == "measure":
            cmd_measure(args, sk)

    except skreader.SekonicError as e:
        print("SEKONIC error:", str(e))
        exit(1)

    except KeyboardInterrupt:
        print("\rInterrupted...")
        print("Bye!")

        sk.close()

        exit(130)


if __name__ == "__main__":
    run()
