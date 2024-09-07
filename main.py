import datetime
import os
import threading
import time

from camera.camera import Camera
from database.repository import Database
from gps.gps_manager import GPS
from imu.imu_manager import IMUSensor
from keypad.keypad import Keypad
from LCD.lcd_manager import LCD
from watchdog.watchdog import Status

db = Database()


# Status thread class
class ObjThread(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(ObjThread, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        self.obj.start()


status = Status()
status_thread = ObjThread(obj=status, name="StatusThread")
status_thread.start()

lcd = LCD(status)
lcd_thread = ObjThread(obj=lcd, name="LCDThread")
lcd_thread.start()

gps = GPS(status)
gps_thread = ObjThread(obj=gps, name="GPSThread")
gps_thread.start()

camera = Camera(status)
camera_thread = ObjThread(obj=camera, name="CameraThread")
camera_thread.start()

keypad = Keypad(db, status, camera)
keypad_thread = ObjThread(obj=keypad, name="KeypadThread")
keypad_thread.start()

imu_sensor = IMUSensor(status)
imu_sensor = ObjThread(obj=imu_sensor, name="IMUThread")
imu_sensor.start()

while True:
    time.sleep(0.01)
