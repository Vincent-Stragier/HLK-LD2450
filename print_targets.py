"""A script to print the information extracted from the LD2450."""

import serial

import serial_protocol


def print_targets(port: str, baudrate: int, continuous: bool = True):
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

                (
                    target1_x,
                    target1_y,
                    target1_speed,
                    target1_distance_res,
                    target2_x,
                    target2_y,
                    target2_speed,
                    target2_distance_res,
                    target3_x,
                    target3_y,
                    target3_speed,
                    target3_distance_res,
                ) = all_target_values

                # Print the interpreted information for all targets
                print(
                    f"Target 1 x-coordinate: {target1_x} mm\n"
                    f"Target 1 y-coordinate: {target1_y} mm\n"
                    f"Target 1 speed: {target1_speed} cm/s\n"
                    f"Target 1 distance res: {target1_distance_res} mm\n\n"
                    f"Target 2 x-coordinate: {target2_x} mm\n"
                    f"Target 2 y-coordinate: {target2_y} mm\n"
                    f"Target 2 speed: {target2_speed} cm/s\n"
                    f"Target 2 distance res: {target2_distance_res} mm\n\n"
                    f"Target 3 x-coordinate: {target3_x} mm\n"
                    f"Target 3 y-coordinate: {target3_y} mm\n"
                    f"Target 3 speed: {target3_speed} cm/s\n"
                    f"Target 3 distance res: {target3_distance_res} mm"
                )

                print("-" * 30)

    except KeyboardInterrupt:
        print("Serial port closed.")


if __name__ == "__main__":
    print_targets(port="/dev/ttyUSB0", baudrate="256000", continuous=True)
