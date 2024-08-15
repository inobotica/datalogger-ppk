import datetime
import os
import threading
import time

from database.repository import Database
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

keypad = Keypad(db)
keypad_thread = ObjThread(obj=keypad, name="KeypadThread")
keypad_thread.start()

while True:
    time.sleep(0.01)
