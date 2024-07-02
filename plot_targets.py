"""A script to plot the LD2450 sensor readings."""

import queue
import threading

import matplotlib.pyplot as plt
import serial
from matplotlib.animation import FuncAnimation

import serial_protocol


def serial_reader(port: str, baudrate: int, data_queue):
    """Put the serial port data in a queue."""
    with serial.Serial(port, baudrate, timeout=1) as ser:

        while True:
            data = ser.read_until(serial_protocol.REPORT_TAIL)
            data_queue.put(data)


def update_plot(_, scater_plot, data_queue):
    """Update the plot with"""

    # Check if there is data in the queue
    while not data_queue.empty():
        serial_protocol_line = data_queue.get()

        # Check if the frame header and tail are present
        if (
            serial_protocol.REPORT_HEADER in serial_protocol_line
            and serial_protocol.REPORT_TAIL in serial_protocol_line
        ):
            # Extract the target values
            all_target_values = serial_protocol.read_radar_data(serial_protocol_line)

            if all_target_values is None:
                continue

            (
                target1_x,
                target1_y,
                _,  # target1_speed,
                _,  # target1_distance_res,
                target2_x,
                target2_y,
                _,  # target2_speed,
                _,  # target2_distance_res,
                target3_x,
                target3_y,
                _,  # target3_speed,
                _,  # target3_distance_res,
            ) = all_target_values

            # current targets
            current_targets_x = [target1_x, target2_x, target3_x]
            current_targets_y = [target1_y, target2_y, target3_y]

            # Update target lists with current targets --> all timesteps are stored
            # targets_x.extend(current_targets_x)
            # targets_y.extend(current_targets_y)

            # Update the scatter plot
            scater_plot.set_offsets(list(zip(current_targets_x, current_targets_y)))

    return (scater_plot,)


def draw_and_update(port: str, baudrate: int):
    """Start the main routine and draw the first plot."""
    # Create a thread-safe queue to communicate between threads
    data_queue = queue.Queue()

    # Create and start the serial reader thread
    serial_thread = threading.Thread(
        target=serial_reader,
        kwargs={"port": port, "baudrate": baudrate, "data_queue": data_queue},
    )

    serial_thread.daemon = True
    serial_thread.start()

    # Initialize empty lists to store all target information
    targets_x = []
    targets_y = []

    # Set up the plot
    fig, ax = plt.subplots()
    sc = ax.scatter(targets_x, targets_y)
    ax.set_title("Position of each detected target")

    # Adjust the limits based on your scenario
    ax.set_xlim(-1000, 1000)
    ax.set_ylim(-6000, 0)

    # Create an animation
    _ = FuncAnimation(
        fig, update_plot, fargs=(sc, data_queue), blit=True, cache_frame_data=False
    )

    plt.xlabel("x [mm]")
    plt.ylabel("y [mm]")

    plt.grid()
    plt.show()


if __name__ == "__main__":
    draw_and_update(port="/dev/ttyUSB0", baudrate=256000)
