import datetime
import os
import threading
import time

from camera.mapir_camera_ble import BLEConfig, ThreadedBleClient
from camera.camera_manager import Camera
from database.repository import Database
from gps.gps_manager import GPS
from imu.imu_manager import IMUSensor
from keypad.keypad_manager import Keypad
from LCD.lcd import OledView
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

gps = GPS(status)
gps_thread = ObjThread(obj=gps, name="GPSThread")
gps_thread.start()

lcd = OledView(status)
lcd_thread = ObjThread(obj=lcd, name="LCDThread")
lcd_thread.start()

# BLE setup
# cfg = BLEConfig()

# def on_notify(data: bytes):
#     pass
#     #print(f"[NOTIFY] {data.decode('utf-8', errors='replace')}")

# ble = ThreadedBleClient(cfg, on_notify=on_notify)
# ble.start()

# Camera setup
camera = Camera(db, status)
camera_thread = ObjThread(obj=camera, name="CameraThread")
camera_thread.start()

# Keypad setup
keypad = Keypad(db, status, camera, gps)
keypad_thread = ObjThread(obj=keypad, name="KeypadThread")
keypad_thread.start()

imu_sensor = IMUSensor(status)
imu_sensor = ObjThread(obj=imu_sensor, name="IMUThread")
imu_sensor.start()


while True:
    time.sleep(0.01)
