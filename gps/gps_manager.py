import os
import time
from datetime import datetime, timezone

from pyubx2 import NMEA_PROTOCOL, UBX_PROTOCOL, UBXReader
from serial import Serial


class GPS:
    def __init__(self, status):
        self.status = status
        self.serial_port = None
        self.ubr = None
        self.file = None  # open(self.filepath, "ab")
        # self.base_dir = "/home/pi/datalogger-ppk/logs"
        # self.filename = datetime.now(timezone.utc).strftime("%y%m%d_%H%M%S") + ".ubx"
        # self.filepath = os.path.join(self.base_dir, self.filename)

        # print(self.filepath)

    def read_line(self):
        self.serial_port = Serial("/dev/ttyACM0", 115200, timeout=3)
        self.ubr = UBXReader(self.serial_port, protfilter=NMEA_PROTOCOL | UBX_PROTOCOL)
        raw_data, parsed_data = self.ubr.read()

        if parsed_data is not None:
            print(parsed_data)

    def save_ubx_message(self):

        # Checks serial port availability
        if not self.status.gps:
            self.serial_port = None
            time.sleep(0.5)
            return None

        if self.status.gps and not self.serial_port:
            print("Opening serial port...")

            self.serial_port = Serial("/dev/ttyACM0", 115200, timeout=3)
            self.ubr = UBXReader(
                self.serial_port, protfilter=NMEA_PROTOCOL | UBX_PROTOCOL
            )

        self.filename = self.status.db_log.filename if self.status.db_log else None
        raw_data, parsed_data = self.ubr.read()

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
