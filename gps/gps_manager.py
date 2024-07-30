from serial import Serial
from pyubx2 import UBXReader, NMEA_PROTOCOL, UBX_PROTOCOL
from datetime import datetime, timezone

import os


class GPS:
    def __init__(self):
        self.serial_port = Serial('/dev/ttyACM0', 38400, timeout=3)
        self.ubr = UBXReader(self.serial_port, protfilter=NMEA_PROTOCOL | UBX_PROTOCOL)
        self.base_dir = '/home/pi/datalogger-ppk/logs'
        self.filename = datetime.now(timezone.utc).strftime("%y%m%d_%H%M%S") + '.ubx'
        self.filepath = os.path.join(self.base_dir, self.filename)
        self.file = open(self.filepath, 'ab')

        print(self.filepath)

    def read_line(self):
        raw_data, parsed_data = self.ubr.read()

        if parsed_data is not None:
            print(parsed_data)
            self.file.write(raw_data)


if __name__ == '__main__':
    gps = GPS()

    while True:
        gps.read_line()
