"""A script to print the information extracted from the LD2450."""

import serial

import serial_protocol


def print_targets(port: str, baudrate: int, continuous: bool = True):
    """Print the information extracted from the LD2450.

    Args:
        port (str): serial port to connect to.
        baudrate (int): baudrate of the serial port.
        continuous (bool, optional): wether or not to measure continuously. Defaults to True.
    """
    try:
        # Open the serial port
        with serial.Serial(port, baudrate, timeout=1) as ser:
            while continuous:
                all_target_values = serial_protocol.read_radar_data(
                    # Read a line from the serial port
                    ser.read_until(serial_protocol.REPORT_TAIL)
                )

                if all_target_values is None:
                    continue

                # Print the interpreted information for all targets
                print(
                    f"Target 1 x-coordinate: {all_target_values[0]} mm\n"
                    f"Target 1 y-coordinate: {all_target_values[1]} mm\n"
                    f"Target 1 speed: {all_target_values[2]} cm/s\n"
                    f"Target 1 distance res: {all_target_values[3]} mm\n\n"
                    f"Target 2 x-coordinate: {all_target_values[4]} mm\n"
                    f"Target 2 y-coordinate: {all_target_values[5]} mm\n"
                    f"Target 2 speed: {all_target_values[6]} cm/s\n"
                    f"Target 2 distance res: {all_target_values[7]} mm\n\n"
                    f"Target 3 x-coordinate: {all_target_values[8]} mm\n"
                    f"Target 3 y-coordinate: {all_target_values[9]} mm\n"
                    f"Target 3 speed: {all_target_values[10]} cm/s\n"
                    f"Target 3 distance res: {all_target_values[11]} mm"
                )

                print("-" * 30)

    except KeyboardInterrupt:
        print("Serial port closed.")


if __name__ == "__main__":
    from generic_args_parser import parse_args

    args = parse_args()

    print_targets(port=args.get("port"), baudrate=args.get(
        "baudrate"), continuous=True)
