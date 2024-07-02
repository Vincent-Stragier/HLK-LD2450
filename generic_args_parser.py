"""Parsing module for the project."""

import argparse
import time

import serial
from serial.tools.list_ports import comports

from serial_protocol import read_firmware_version

VALID_BAUDRATES = (9600, 19200, 38400, 57600, 115200, 230400, 256000, 460800)


def parse_args() -> dict:
    """Main parser"""
    parser = argparse.ArgumentParser(
        description="Serial port communication for the LD2450."
    )

    # The arguments to parse are optional
    # (the port as a string and baudrate as a positive integer)
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="/dev/ttyUSB0",
        help="The serial port to connect to.",
    )

    parser.add_argument(
        "-b",
        "--baudrate",
        type=int,
        default=256000,
        choices=VALID_BAUDRATES,
        help=(
            "The baudrate of the serial port."
        ),
    )

    args = parser.parse_args()

    port = args.port
    current_ports = list(comport.device for comport in comports())

    if port not in current_ports:
        if len(current_ports) == 0:
            message = (
                "Currently no serial device is connected "
                "(check your connections)."
            )

        elif len(current_ports) == 1:
            message = (
                "Currently only one serial port is available: " f"{current_ports[0]}."
            )

        else:
            separator = "\n\t- "

            message = (
                f"Currently {len(current_ports)} serial ports are available:\n\n"
                f"\t- {(separator).join(current_ports)}"
            )

        raise ValueError(f'"{port}" is not a valid port.\n{message}')

    number_of_tries = 5

    with serial.Serial(
        port=port,
        baudrate=args.baudrate,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1,
    ) as serial_port:
        while number_of_tries > 0:
            try:
                version = read_firmware_version(serial_port, verbose=False)

                if version is not None and version != "V0.0.0":
                    break

                time.sleep(0.5)

            finally:
                number_of_tries -= 1

        if version is None or version == "V0.0.0":
            raise ConnectionError(
                f"Could not connect to the sensor (received {version = }). "
                "Please check the connections and try again."
            )

    return {"port": port, "baudrate": args.baudrate, "version": version}


if __name__ == "__main__":
    print(
        "This is a parsing module, "
        "it has no use alone (but debugging it).\n\n"
        f"Parsed arguments: {parse_args()}"
    )
