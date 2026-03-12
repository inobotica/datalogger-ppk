import os
import time
from datetime import datetime, timedelta, timezone

from pyubx2 import NMEA_PROTOCOL, UBX_PROTOCOL, UBXReader
from serial import Serial


class GPS:
    def __init__(self, state):
        self.BAUDRATE = [57600, 115200][1]
        self.state = state
        self.serial_port = None
        self.ubr = None
        self.file = None  # open(self.filepath, "ab")
        # self.base_dir = "/home/pi/datalogger-ppk/logs"
        # self.filename = datetime.now(timezone.utc).strftime("%y%m%d_%H%M%S") + ".ubx"
        # self.filepath = os.path.join(self.base_dir, self.filename)
        self.base_altitude = None
        self.altitude = None
        self.tow_time = None  # time of gps which is +18s ahead of UTC
        # print(self.filepath)

    def read_line(self):
        self.serial_port = Serial(self.state.gps_port, self.BAUDRATE, timeout=3)
        self.ubr = UBXReader(self.serial_port, protfilter=NMEA_PROTOCOL | UBX_PROTOCOL)
        raw_data, parsed_data = self.ubr.read()

        if parsed_data is not None and parsed_data.identity == "GNGGA":
            print(int(parsed_data.alt))

    def set_tow_time(self, parsed_data):
        """
        Sets tow time which is +18 seconds ahead of UTC time
        """
        valid_date = getattr(parsed_data, "validDate", 0) == 1
        valid_time = getattr(parsed_data, "validTime", 0) == 1
        fully_resolved = getattr(parsed_data, "fullyResolved", 0) == 1

        if valid_date and valid_time and fully_resolved:
            now = datetime.now(timezone.utc)
            epoch = datetime(1980, 1, 6, tzinfo=timezone.utc)
            difference = now - epoch
            epoch_weeks = int(difference.total_seconds() / 604800)
            gps_time = epoch + timedelta(
                weeks=epoch_weeks, milliseconds=parsed_data.iTOW
            )

            # print("sys time:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            # print("tow time:",gps_time.strftime("%Y-%m-%d %H:%M:%S"))

            self.tow_time = gps_time
            self.state.tow_time = gps_time

    def save_ubx_message(self):

        # Checks serial port availability
        if not self.state.gps:
            self.serial_port = None
            time.sleep(0.5)
            return None

        if self.state.gps and not self.serial_port:
            print("Opening serial port...")

            self.serial_port = Serial(self.state.gps_port, self.BAUDRATE, timeout=3)
            self.ubr = UBXReader(
                self.serial_port, protfilter=NMEA_PROTOCOL | UBX_PROTOCOL
            )

        self.filename = self.state.db_log.filename if self.state.db_log else None
        raw_data, parsed_data = self.ubr.read()

        # Updates tow time
        if parsed_data is not None and parsed_data.identity == "NAV-PVT":
            self.set_tow_time(parsed_data)

        # Updates altitude
        if parsed_data is not None and parsed_data.identity == "GNGGA":

            # Inits base altitude:
            if not self.base_altitude and parsed_data.alt:
                self.base_altitude = int(parsed_data.alt)

            if parsed_data.alt:
                self.altitude = int(parsed_data.alt)

        # Creates a new log file
        if not self.file and self.filename:
            print("Creating UBX file:", self.filename)
            self.file = open(self.filename, "ab")

        # Saves UBX message
        if self.file:
            self.file.write(raw_data)

        # Logging has endes, close file
        if self.file and not self.filename:
            print("Closing UBX file...")

            if self.state.path:
                print("Copying file to USB...")
                os.system("cp {} {}".format(self.file.name, self.state.path))

            self.file.close()
            self.file = None

    def start(self):
        print("Starting GPS Thread...")

        while True:
            self.save_ubx_message()


if __name__ == "__main__":
    gps = GPS("")

    while True:
        gps.read_line()
