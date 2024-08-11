import datetime
import os
import threading
import time

from LCD.lcd_manager import LCD
from watchdog.watchdog import Status


# Status thread class
class StatusThread(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(StatusThread, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        self.obj.start()


class LCDThread(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(StatusThread, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        self.obj.start()


status = Status()
status_thread = StatusThread(obj=status, name="StatusThread")
status_thread.start()

lcd = LCD(status)
lcd_thread = LCDThread(obj=lcd, name="LCDThread")
lcd_thread.start()

while True:
    print(status)
    time.sleep(0.5)
