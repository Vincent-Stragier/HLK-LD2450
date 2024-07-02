"""A driver module to communicate with the LD2450."""

import serial

COMMAND_HEADER = bytes.fromhex("FD FC FB FA")
COMMAND_TAIL = bytes.fromhex("04 03 02 01")

REPORT_HEADER = bytes.fromhex("AA FF 03 00")
REPORT_TAIL = bytes.fromhex("55 CC")

BYTES_FROM_HEX_EMPTY = bytes.fromhex("")

POSSIBLE_BAUDRATES = [
    9600,
    19200,
    38400,
    57600,
    115200,
    230400,
    256000,
    460800,
]


def _send_command(
    ser: serial.Serial,
    intra_frame_length: bytes,
    command_word: bytes,
    command_value: bytes,
) -> bytes:
    """
    Send a command to the radar (see docs 2.1.2)
    Parameters:
    - ser (serial.Serial): the serial port object
    - intra_frame_length (bytes): the intra frame length
    - command_word (bytes): the command word
    - command_value (bytes): the command value
    Returns:
    - response (bytes): the response from the radar
    """
    # Create the command
    command = (
        COMMAND_HEADER
        + intra_frame_length
        + command_word
        + command_value
        + COMMAND_TAIL
    )

    ser.write(command)
    return ser.read_until(COMMAND_TAIL)


def _get_command_success(response: bytes) -> bool:
    """
    Check if the command was sent successfully
    Parameters:
    - response (bytes): the response from the radar
    Returns:
    - success (bool): True if the command was sent successfully, False otherwise
    """
    return int.from_bytes(response[8:10], byteorder="little", signed=True) == 0


def send_command(
    ser: serial.Serial,
    intra_frame_length: bytes,
    command_word: bytes,
    command_value: bytes,
) -> tuple[bytes, bool]:
    """
    Send a command to the radar (see docs 2.1.2) and return success.

    Parameters:
    - ser (serial.Serial): the serial port object
    - intra_frame_length (bytes): the intra frame length
    - command_word (bytes): the command word
    - command_value (bytes): the command value

    Returns:
    - response (bytes, bool): the response from the radar and success (bool)
    """
    # Create the command
    command = (
        COMMAND_HEADER
        + intra_frame_length
        + command_word
        + command_value
        + COMMAND_TAIL
    )

    ser.write(command)
    response = ser.read_until(COMMAND_TAIL)

    success = int.from_bytes(
        response[8:10], byteorder="little", signed=True) == 0

    return response, success


def enable_configuration_mode(ser: serial.Serial) -> bool:
    """
    Set the radar to configuration mode (see docs 2.2.1)

    Parameters:
    - ser (serial.Serial): the serial port object

    Returns:
    - success (bool): True if the configuration mode was successfully enabled,
    False otherwise
    """
    _, command_success = send_command(
        ser,
        intra_frame_length=int(4).to_bytes(2, byteorder="little", signed=True),
        command_word=bytes.fromhex("FF 00"),
        command_value=bytes.fromhex("01 00"),
    )

    if command_success:
        print("Configuration mode enabled")

    else:
        print("Configuration enable failed")

    return command_success


def end_configuration_mode(ser: serial.Serial) -> bool:
    """
    End the configuration mode (see docs 2.2.2)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the configuration mode was successfully ended,
    False otherwise
    """
    _, command_success = send_command(
        ser,
        intra_frame_length=int(2).to_bytes(
            2, byteorder="little", signed=False),
        command_word=bytes.fromhex("FE 00"),
        command_value=BYTES_FROM_HEX_EMPTY,
    )

    if command_success:
        print("Configuration mode disabled")

    else:
        print("Configuration disable failed")

    return command_success


def single_target_tracking(ser: serial.Serial) -> bool:
    """
    Set the radar to single target tracking mode (see docs 2.2.3)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the single target tracking mode was
    successfully enabled, False otherwise
    """
    _, command_success = send_command(
        ser,
        intra_frame_length=int(2).to_bytes(2, byteorder="little", signed=True),
        command_word=bytes.fromhex("80 00"),
        command_value=BYTES_FROM_HEX_EMPTY,
    )
    if command_success:
        print("Single target tracking mode enabled")

    else:
        print("Single target tracking mode enable failed")

    return command_success


def multi_target_tracking(ser: serial.Serial) -> bool:
    """
    Set the radar to multi target tracking mode (see docs 2.2.4)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the multiple target tracking mode was
    successfully enabled, False otherwise
    """
    _, command_success = send_command(
        ser,
        intra_frame_length=int(2).to_bytes(2, byteorder="little", signed=True),
        command_word=bytes.fromhex("90 00"),
        command_value=BYTES_FROM_HEX_EMPTY,
    )

    if command_success:
        print("Multi target tracking mode enabled")

    else:
        print("Multi target tracking mode enable failed")

    return command_success


def query_target_tracking(ser: serial.Serial) -> int:
    """
    Query the target tracking mode, the default mode is multi target tracking (see docs 2.2.5)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - tracking mode (int): 1 for single target tracking, 2 for multi target tracking
    """
    response, command_success = send_command(
        ser,
        intra_frame_length=int(2).to_bytes(2, byteorder="little", signed=True),
        command_word=bytes.fromhex("91 00"),
        command_value=BYTES_FROM_HEX_EMPTY,
    )

    if not command_success:
        print("Query target tracking mode failed")
        return None

    tracking_type_int = int.from_bytes(
        response[10:12], byteorder="little", signed=True)

    print(f"Tracking mode: {tracking_type_int}")
    return tracking_type_int


def read_firmware_version(ser: serial.Serial, verbose: bool = True) -> str | None:
    """
    Read the firmware version of the radar (see docs 2.2.6)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - firmware_version (str): the firmware version of the radar
    """
    response, command_success = send_command(
        ser,
        intra_frame_length=int(2).to_bytes(2, byteorder="little", signed=True),
        command_word=bytes.fromhex("A0 00"),
        command_value=BYTES_FROM_HEX_EMPTY,
    )

    if not command_success:
        if verbose:
            print("Failed to read firmware version failed")

        return None

    firmware_type = int.from_bytes(
        response[10:12], byteorder="little", signed=True)

    major_version_number = int.from_bytes(
        response[12:14], byteorder="little", signed=True
    )

    minor_version_number = int.from_bytes(
        response[14:18], byteorder="little", signed=True
    )

    firmware_version = f"V{firmware_type}.{major_version_number}.{minor_version_number}"

    if verbose:
        print(f"Firmware version: {firmware_version}")

    return firmware_version


def set_serial_port_baud_rate(ser: serial.Serial, baud_rate: int = 256000) -> bool:
    """
    Set the serial port baud rate of the radar (see docs 2.2.7)
    Parameters:
    - ser (serial.Serial): the serial port object
    - baud_rate (int): the baud rate of the radar
    Returns:
    - success (bool): True if the baud rate was successfully set, False otherwise
    """
    if baud_rate not in POSSIBLE_BAUDRATES:
        raise ValueError(
            "The baud rate must be one of the following:\n"
            "9600, 19200, 38400, 57600, 115200, 230400, 256000, 460800"
        )

    baudrate_index = int(POSSIBLE_BAUDRATES.index(baud_rate))

    _, command_success = send_command(
        ser,
        intra_frame_length=int(4).to_bytes(2, byteorder="little", signed=True),
        command_word=bytes.fromhex("A1 00"),
        command_value=baudrate_index.to_bytes(
            2, byteorder="little", signed=False)
    )

    if command_success:
        print(f"Serial port baud rate set to {baud_rate}")

    else:
        print("Set serial port baud rate failed")

    return command_success


def restore_factory_settings(ser: serial.Serial) -> bool:
    """
    Restore the factory settings of the radar (see docs 2.2.8)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the factory settings were successfully restored, False otherwise
    """
    _, command_success = send_command(
        ser,
        intra_frame_length=int(2).to_bytes(
            2, byteorder="little", signed=False),
        command_word=bytes.fromhex("A2 00"),
        command_value=BYTES_FROM_HEX_EMPTY
    )

    if command_success:
        print("Factory settings restored")

    else:
        print("Restore factory settings failed")

    return command_success


def restart_module(ser: serial.Serial) -> bool:
    """
    Restart the radar module (see docs 2.2.9)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the radar module was successfully restarted,
    False otherwise
    """
    _, command_success = send_command(
        ser,
        intra_frame_length=int(2).to_bytes(
            2, byteorder="little", signed=False),
        command_word=bytes.fromhex("A3 00"),
        command_value=BYTES_FROM_HEX_EMPTY

    )

    if command_success:
        print("Module restarted")

    else:
        print("Module restart failed")

    return command_success


def bluetooth_setup(ser: serial.Serial, bluetooth_on: bool = True) -> bool:
    """
    Set up the bluetooth of the radar (see docs 2.2.10)
    Parameters:
    - ser (serial.Serial): the serial port object
    - bluetooth_on (bool): True if the bluetooth should be enabled, False otherwise
    Returns:
    - success (bool): True if the bluetooth was successfully set up, False otherwise
    """
    _, command_success = send_command(
        ser,
        intra_frame_length=int(4).to_bytes(
            2, byteorder="little", signed=False),
        command_word=bytes.fromhex("A4 00"),
        command_value=bytes.fromhex(
            "01 00") if bluetooth_on else bytes.fromhex("00 00")
    )

    if command_success:
        print(f'Bluetooth {"enabled" if bluetooth_on else "disabled"}')

    else:
        print("Bluetooth setup failed")

    return command_success


def get_mac_address(ser: serial.Serial) -> str:
    """Get the MAC address of the radar (see docs 2.2.11)

    Parameters:
    - ser (serial.Serial): the serial port object

    Returns:
    - mac_address (str): the MAC address of the radar
    """
    response, command_success = send_command(
        ser,
        intra_frame_length=int(4).to_bytes(
            2, byteorder="little", signed=False),
        command_word=bytes.fromhex("A5 00"),
        command_value=bytes.fromhex("01 00")
    )
    if not command_success:
        print("Get MAC address failed")
        return None

    mac_address = response[10:22].decode("utf-8")
    print(f"MAC address: {mac_address}")

    return mac_address


def query_zone_filtering(ser: serial.Serial) -> tuple[13]:
    """
    Query the current zone filtering mode of the radar (see docs 2.2.12)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - zone_filtering_mode (tuple[13):
        [0] zone_filtering_mode (int): 0 for no zone filtering,
        1 detect only set region, 2 do not detect set region
        [1-4] region 1 diagonal vertices coordinates (int): x1, y1, x2, y2
        [5-8] region 2 diagonal vertices coordinates (int): x1, y1, x2, y2
        [9-12] region 3 diagonal vertices coordinates (int): x1, y1, x2, y2
    """
    response, command_success = send_command(
        ser,
        intra_frame_length=int(2).to_bytes(
            2, byteorder="little", signed=False),
        command_word=bytes.fromhex("C1 00"),
        command_value=BYTES_FROM_HEX_EMPTY
    )

    if not command_success:
        print("Query zone filtering mode failed")
        return None

    zone_filtering_mode = int.from_bytes(
        response[10:12], byteorder="little", signed=True
    )

    print(f"Zone filtering mode: {zone_filtering_mode}")

    return (
        zone_filtering_mode,
        # Region 1
        # region1_x1
        int.from_bytes(response[12:14], byteorder="little", signed=True),
        # region1_y1
        int.from_bytes(response[14:16], byteorder="little", signed=True),
        # region1_x2
        int.from_bytes(response[16:18], byteorder="little", signed=True),
        # region1_y2
        int.from_bytes(response[18:20], byteorder="little", signed=True),
        # Region 2
        # region2_x1
        int.from_bytes(response[20:22], byteorder="little", signed=True),
        # region2_y1
        int.from_bytes(response[22:24], byteorder="little", signed=True),
        # region2_x2
        int.from_bytes(response[24:26], byteorder="little", signed=True),
        # region2_y2
        int.from_bytes(response[26:28], byteorder="little", signed=True),
        # Region 3
        # region3_x1
        int.from_bytes(response[28:30], byteorder="little", signed=True),
        # region3_y1
        int.from_bytes(response[30:32], byteorder="little", signed=True),
        # region3_x2
        int.from_bytes(response[32:34], byteorder="little", signed=True),
        # region3_y2
        int.from_bytes(response[34:36], byteorder="little", signed=True),
    )


def set_zone_filtering(
    ser: serial.Serial,
    zone_filtering_mode: int = 0,
    region1_x1: int = 0,
    region1_y1: int = 0,
    region1_x2: int = 0,
    region1_y2: int = 0,
    region2_x1: int = 0,
    region2_y1: int = 0,
    region2_x2: int = 0,
    region2_y2: int = 0,
    region3_x1: int = 0,
    region3_y1: int = 0,
    region3_x2: int = 0,
    region3_y2: int = 0,
) -> bool:
    """
    Set the zone filtering mode of the radar (see docs 2.2.13)
    Parameters:
    - ser (serial.Serial): the serial port object
    - zone_filtering_mode (int): 0 for no zone filtering,
    1 detect only set region, 2 do not detect set region
    - region1_x1 (int): x coordinate of the first diagonal vertex of region 1
    - region1_y1 (int): y coordinate of the first diagonal vertex of region 1
    - region1_x2 (int): x coordinate of the second diagonal vertex of region 1
    - region1_y2 (int): y coordinate of the second diagonal vertex of region 1
    - region2_x1 (int): x coordinate of the first diagonal vertex of region 2
    - region2_y1 (int): y coordinate of the first diagonal vertex of region 2
    - region2_x2 (int): x coordinate of the second diagonal vertex of region 2
    - region2_y2 (int): y coordinate of the second diagonal vertex of region 2
    - region3_x1 (int): x coordinate of the first diagonal vertex of region 3
    - region3_y1 (int): y coordinate of the first diagonal vertex of region 3
    - region3_x2 (int): x coordinate of the second diagonal vertex of region 3
    - region3_y2 (int): y coordinate of the second diagonal vertex of region 3
    Returns:
    - success (bool): True if the zone filtering mode was successfully set,
    False otherwise
    """
    _, command_success = send_command(
        ser,
        intra_frame_length=int(26).to_bytes(
            2, byteorder="little", signed=False),
        command_word=bytes.fromhex("C2 00"),
        command_value=bytes.fromhex(
            f"{zone_filtering_mode:04x} "
            # Region 1
            f"{region1_x1:04x} {region1_y1:04x} "
            f"{region1_x2:04x} {region1_y2:04x} "
            # Region 2
            f"{region2_x1:04x} {region2_y1:04x} "
            f"{region2_x2:04x} {region2_y2:04x} "
            # Region 3
            f"{region3_x1:04x} {region3_y1:04x} "
            f"{region3_x2:04x} {region3_y2:04x}"
        )
    )

    if command_success:
        print(f"Zone filtering mode set to {zone_filtering_mode}")

    else:
        print("Set zone filtering mode failed")

    return command_success


def read_radar_data(serial_port_line: bytes) -> tuple[12]:
    """
    Read the basic mode data from the serial port line (see docs 2.3)

    Parameters:
    - serial_port_line (bytes): the serial port line

    Returns:
    - radar_data (tuple[12]): the radar data
        - [0-3] x, y, speed, distance_resolution of target 1
        - [4-7] x, y, speed, distance_resolution of target 2
        - [8-11] x, y, speed, distance_resolution of target 3
    """
    # Check if the frame header and tail are present
    if REPORT_HEADER not in serial_port_line:
        print("Serial port line corrupted - report header missing")
        return None

    if REPORT_TAIL not in serial_port_line:
        print("Serial port line corrupted - report tail missing")
        return None

    if len(serial_port_line) != 30:
        print("Serial port line corrupted - not 30 bytes long")
        return None

    # Interpret the target data
    all_targets_bytes = [
        # target1_bytes
        serial_port_line[4:12],
        # target2_bytes
        serial_port_line[12:20],
        # target3_bytes
        serial_port_line[20:28],
    ]

    all_targets_data = []

    for target_bytes in all_targets_bytes:
        x = int.from_bytes(target_bytes[0:2], byteorder="little", signed=True)
        y = int.from_bytes(target_bytes[2:4], byteorder="little", signed=True)
        speed = int.from_bytes(
            target_bytes[4:6], byteorder="little", signed=True)
        distance_resolution = int.from_bytes(
            target_bytes[6:8], byteorder="little", signed=False
        )

        # Substract 2^15 depending if negative or positive
        x = x if x >= 0 else -(2**15) - x
        y = y if y >= 0 else -(2**15) - y
        speed = speed if speed >= 0 else -(2**15) - speed

        # Append target data to the list and flatten
        all_targets_data.extend([x, y, speed, distance_resolution])

    return tuple(all_targets_data)
