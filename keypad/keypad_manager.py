#!/usr/bin/env python3

import time
from threading import Thread

import RPi.GPIO as GPIO

from geotagger.geotag_manager import Geotagger


class Keypad:
    def __init__(self, database, status, camera, gps) -> None:
        """
        GPIO - Function
        23 - Geotag
        24 - start/stop log
        26 - USB button | Shutter
        19 - USB button | Stop log
        """
        self.GEOTAG_PIN = 26
        self.START_PIN = 19
        self.TRIGGER_PIN = 5
        self.BOUNCE_TIME = 500

        self.database = database
        self.status = status
        self.camera = camera
        self.gps = gps
        self.geotagger = Geotagger(database, status)

        # Keys setup
        GPIO.setmode(GPIO.BCM)

        # Geotag pin
        GPIO.setup(self.GEOTAG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.GEOTAG_PIN,
            GPIO.FALLING,
            callback=self.geotag_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        # Start pin
        GPIO.setup(self.START_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.START_PIN,
            GPIO.FALLING,
            callback=self.start_stop_log_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        # Stop pin
        GPIO.setup(self.TRIGGER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.TRIGGER_PIN,
            GPIO.FALLING,
            callback=self.start_stop_intervalometer_callback,
            bouncetime=self.BOUNCE_TIME,
        )

    def geotag_callback(self, channel):
        """
        Callback for joystick
        """
        print("Running Geotagger")
        self.geotagger.run()

    def start_stop_log_callback(self, channel):
        # Starts recording log and start/pauses camera trigger
        if not self.status.db_log:
            self.status.db_log = self.database.insert_log()
            print("saving log into:", self.status.db_log.filename)
        else:
            # Stops recording log
            print("closing log...")
            self.status.db_log.state = True
            self.database.session.commit()

            # Copies db data into USB
            if self.status.path:
                print("Copying file to USB...")
                rows = self.database.get_gps_points_cloud(
                    self.status.db_log.filename, is_full_path=True
                )
                file_path = (
                    self.status.path
                    + "/"
                    + self.status.db_log.filename.split("/")[-1].replace(".ubx", ".txt")
                )
                print("Dumping DB points to:", file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    data = [
                        f"{row.time}, {row.unix_time}, {row.photo}, {row.pitch}, {row.roll}"
                        for row in rows
                    ]
                    data.insert(0, "time, unix_time, photo, pitch, roll")
                    f.write("\n".join(data))

            # Resets log
            self.status.db_log = None

    def start_stop_intervalometer_callback(self, channel):
        self.camera.start_stop_intervalometer()

    def start(self):
        print("Starting Keypad Thread...")

        while True:
            time.sleep(0.1)


if __name__ == "__main__":
    print("Starting keypad detection")
    keypad = Keypad("db")
    keypad.start()
