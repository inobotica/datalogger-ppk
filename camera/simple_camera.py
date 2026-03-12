import os
import subprocess
import sys
import time

import gphoto2 as gp
import RPi.GPIO as GPIO

from camera.mapir_camera_serial import MapirCamera

"""
In case of having issues with the GPIO add event function do:

- Remove deprecated library
sudo apt remove python3-rpi.gpio
pip uninstall RPi.GPIO --break-system-packages

- Add new library
sudo apt install python3-rpi-lgpio
pip install rpi-lgpio --break-system-packages

"""


class Camera:
    def __init__(self, database, state) -> None:
        self.database = database
        self.state = state
        self.camera = None
        self.LED_PIN = 13  # Pin to signal that a trigger was detected
        self.SHUTTER_PIN = 17  # Pin to detect shutting of camera throgh hotshoe
        self.TRIGGER_PIN = 27  # Pin to send IO to IR remote
        self.CAPTURE_PIN = 25  # Pin to capture an image and sync seq ID
        self.TRIGGER_BOUNCE_TIME = 20
        self.CAPTURE_BOUNCE_TIME = 300
        self.intervalometer_state = False
        self.PHOTO_THRESHOLD = 5
        self.PHOTO_COUNT = 0
        self.mapir_camera = MapirCamera(state)
        # self.ble = ble

        GPIO.setmode(GPIO.BCM)

        # Shutter input setup
        GPIO.setup(self.SHUTTER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.SHUTTER_PIN,
            GPIO.FALLING,
            callback=self.shutter_detection,
            bouncetime=self.TRIGGER_BOUNCE_TIME,
        )

        # Capture input setup
        GPIO.setup(self.CAPTURE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.CAPTURE_PIN,
            GPIO.FALLING,
            callback=self.capture_callback,
            bouncetime=self.CAPTURE_BOUNCE_TIME,
        )

        # Trigger pin setup
        GPIO.setup(self.TRIGGER_PIN, GPIO.OUT)

        # Led pin setup
        GPIO.setup(self.LED_PIN, GPIO.OUT)

        self.releaseCamera()
        self.camera = None

    def capture_callback(self, channel):
        self.capture_image_cmd()

    def start_stop_intervalometer(self) -> None:
        self.intervalometer_state = not self.intervalometer_state

        msg = "Starting" if self.intervalometer_state else "Stoping"
        msg = msg + " intervalometer..."
        print(msg)

        GPIO.output(self.TRIGGER_PIN, True)
        time.sleep(0.05)
        GPIO.output(self.TRIGGER_PIN, False)

        self.mapir_camera.trigger_camera("on" if self.intervalometer_state else "off")

        # self.ble.capture()
        # self.trigger_capture_cmd()
        # self.trigger_capture()

    def shutter_detection(self, channel) -> None:
        print("Shutter detected!")

        if self.state.camera and not self.state.photo.is_busy:
            self.state.photo.increase_count()
            print("photo", self.state.photo.name)

        if self.state.db_log:
            self.database.insert_position(self.state)
        else:
            print("No log being recorded")

        GPIO.output(self.LED_PIN, True)
        time.sleep(0.05)
        GPIO.output(self.LED_PIN, False)

        # This validation helps to stop camera intervalometer when stop button was pressed without pausing before
        # if not self.state.db_log:
        #     self.PHOTO_COUNT += 1

        #     if self.PHOTO_COUNT > self.PHOTO_THRESHOLD:
        #         self.trigger_capture_cmd()
        #         self.PHOTO_COUNT = 0
        # else:
        #     self.PHOTO_COUNT = 0

    def releaseCamera(self):
        print("Releasing camera...")
        errorTrace = "kill gphoto"

        cmd = "pkill -f gphoto2"
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        cmd = "gphoto2 --set-config capturetarget=1"
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        try:
            killGphoto = ["pkill", "-f", "gphoto2"]
            subprocess.run(
                killGphoto, check=True, stdout=subprocess.PIPE, universal_newlines=True
            )
            print(" - Gphoto2 killed")
            errorTrace = "kill kernel"

            killKernel = ["pkill", "-f", "gvfsd-gph"]
            subprocess.run(
                killKernel, check=True, stdout=subprocess.PIPE, universal_newlines=True
            )
            print(" - Kernel killed")
            errorTrace = "target"

            setTarget = ["gphoto2", "--set-config", "capturetarget=1"]
            subprocess.run(
                setTarget, check=True, stdout=subprocess.PIPE, universal_newlines=True
            )
            print(" - Targed setted")

        except subprocess.CalledProcessError:
            print(errorTrace, "Camera already released")

    def capture_image_cmd(self):

        if self.state.mapir_port:
            print("Mapir trigger...")
            os.system('echo "on"  > ' + self.state.mapir_port)

        if not self.state.camera:
            return False

        print("Taking photo...")

        self.state.photo.is_busy = True
        image_path = "/home/pi/datalogger-ppk/camera/image.log"
        f = open(image_path, "w")
        f.close()

        cmd = [
            "gphoto2",
            "--debug",
            "--debug-loglevel=data",
            f"--debug-logfile={image_path}",
            "--wait-event=3s",
            "--capture-image",
        ]
        subprocess.run(cmd, capture_output=True, text=True)

        lines = open(image_path).readlines()
        name = None

        for index in range(10000, len(lines)):
            line = lines[index].strip()

            if "D.S.C." in line:
                name = line
                break

        self.state.photo.is_busy = False

        # Test mapir
        # self.mapir_camera.trigger_camera("on")
        # time.sleep(10)
        # self.mapir_camera.trigger_camera("off")

        if name:
            print("PTP line", name)
            count = name[name.index("D.S.C.") + 6 :].replace(".", "")
            self.state.photo.count = str(
                int(count) - 1
            )  # -1 porque el hotshoe incrementa 1
            print("Photo taken:", self.state.photo.name)
            return True

        return False

    def trigger_capture_cmd(self):
        if self.state.camera:
            cmd = ["gphoto2", "--trigger-capture"]
            subprocess.run(cmd, capture_output=True, text=True)

    def trigger_capture(self):
        if self.state.camera:
            if not self.camera:
                print("Initializing camera...")
                self.camera = gp.Camera()
                self.camera.init()

            gp.check_result(gp.gp_camera_trigger_capture(self.camera))
            print("Trigger capture!")

    def start(self):
        print("Starting Camera Thread...")

        while True:
            time.sleep(0.05)


if __name__ == "__main__":
    camera = Camera("", "")
    os.system("pkill -f gphoto2")
    os.system("pkill -f gvfsd-gph")
    camera.capture_image_cmd()
