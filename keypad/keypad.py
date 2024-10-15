#!/usr/bin/env python3

import time
from threading import Thread

import RPi.GPIO as GPIO

from geotagger.geotag_manager import Geotagger


class Keypad:
    def __init__(self, database, status, camera) -> None:
        self.KEY_UP_PIN = 6
        self.KEY_DOWN_PIN = 19
        self.KEY_LEFT_PIN = 5
        self.KEY_RIGHT_PIN = 26
        self.KEY_PRESS_PIN = 13

        self.KEY1_PIN = 21
        self.KEY2_PIN = 20
        self.KEY3_PIN = 16
        self.BOUNCE_TIME = 500

        self.database = database
        self.status = status
        self.camera = camera
        self.geotagger = Geotagger(database, status)

        # Keys setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.KEY1_PIN,
            GPIO.FALLING,
            callback=self.keys_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        GPIO.setup(self.KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.KEY2_PIN,
            GPIO.FALLING,
            callback=self.keys_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        GPIO.setup(self.KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.KEY3_PIN,
            GPIO.BOTH,
            callback=self.keys_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        # Joystick setup
        GPIO.setup(self.KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.KEY_UP_PIN,
            GPIO.BOTH,
            callback=self.joystick_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        GPIO.setup(self.KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.KEY_DOWN_PIN,
            GPIO.BOTH,
            callback=self.joystick_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        GPIO.setup(self.KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.KEY_LEFT_PIN,
            GPIO.BOTH,
            callback=self.joystick_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        GPIO.setup(self.KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.KEY_RIGHT_PIN,
            GPIO.BOTH,
            callback=self.joystick_callback,
            bouncetime=self.BOUNCE_TIME,
        )

        GPIO.setup(self.KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.KEY_PRESS_PIN,
            GPIO.BOTH,
            callback=self.joystick_callback,
            bouncetime=self.BOUNCE_TIME,
        )

    def keys_callback(self, channel):
        """
        Callback for keys
        """

        if channel == self.KEY1_PIN:
            print("key1")

            if not self.status.db_log:
                self.status.db_log = self.database.insert_log()
                print("saving log into:", self.status.db_log.filename)
            else:
                print("updating log...")
                self.status.db_log.state = True
                self.database.session.commit()
                self.status.db_log = None

        elif channel == self.KEY2_PIN:
            print("key2")
        elif channel == self.KEY3_PIN:
            print("key3")
            self.camera.capture_image_cmd()

    def joystick_callback(self, channel):
        """
        Callback for joystick
        """
        if channel == self.KEY_UP_PIN:
            print("up")
        elif channel == self.KEY_DOWN_PIN:
            print("down")
        elif channel == self.KEY_LEFT_PIN:
            print("left")
        elif channel == self.KEY_RIGHT_PIN:
            print("right")
        elif channel == self.KEY_PRESS_PIN:
            print("press")
            print("Running Geotagger")
            self.geotagger.run()

    def start(self):
        print("Starting Keypad Thread...")

        while True:
            time.sleep(0.1)


if __name__ == "__main__":
    print("Starting keypad detection")
    keypad = Keypad("db")
    keypad.start()
