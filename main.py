import datetime
import os
import threading
import time

from LCD.lcd_manager import LCD
from watchdog.watchdog import Status


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

while True:
    print(status)
    time.sleep(0.5)
