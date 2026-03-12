import os
import sys 
import time
import logging
import spidev as SPI
import subprocess
sys.path.append("..")
from lib import LCD_1inch69
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0 
device = 0 
logging.basicConfig(level = logging.DEBUG)

IMAGE_FOLDER = "/home/pi/Documents/oled/image/"

class Icon:
    def __init__(self, _x, _y, _name):
        self.position = (_x, _y)
        self.name = _name
        self.folder = Path(IMAGE_FOLDER)

    def set_on(self, _image)->Image:
        _icon = Image.open(self.folder / (self.name + "_on.png"))
        _image.paste(_icon, self.position)
        return _image

    def set_off(self, _image)->Image:
        _icon = Image.open(self.folder / (self.name + "_off.png"))
        _image.paste(_icon, self.position)
        return _image

class OledView:
    """Main class for oled view"""
    def __init__(self, state):
        self.width = 240
        self.height = 280
        self.header = 10
        
        self.log_pos = (20, 60)
        self.cam_pos = (20, 90)
        self.geotag_pos = (20, 120)
        self.time_pos = (20, 220)
        self.ip_pos = (70, 250)

        self.state = state
        self.camera_icon = Icon(50, self.header, "cam")
        self.gps_icon = Icon(90, self.header, "gps")
        self.usb_icon = Icon(130, self.header, "usb")
        self.wifi_icon = Icon(170, self.header, "wifi")

        try:
            # displaylay with hardware SPI:
            self.display = LCD_1inch69.LCD_1inch69()
            self.display.Init()
            self.display.clear()
            #Set the backlight to 100
            self.display.bl_DutyCycle(80)

            self.display_size = (self.display.width, self.display.height)
            self.font = ImageFont.truetype("/home/pi/Documents/oled/Font/Font02.ttf", 22)
            self.font_small = ImageFont.truetype("/home/pi/Documents/oled/Font/Font02.ttf", 18)
            self.image = Image.new("RGB", self.display_size, "BLACK")
            self.draw = ImageDraw.Draw(self.image)


        except IOError as e:
            logging.info(e)    
            
        except KeyboardInterrupt:
            self.display.module_exit()
            logging.info("quit:")
            exit()

    def clear_view(self):
        self.display.clear()
    
    def update_view(self):
        self.display.clear()
        self.image = Image.new("RGB", self.display_size, "BLACK")
        self.draw = ImageDraw.Draw(self.image)

        self.update_messages()
        self.update_icons()
        self.display.ShowImage(self.image)

    def update_messages(self):
        # Log status
        self.draw.text(self.log_pos, 'LOG: Grabando', fill = "WHITE", font=self.font)

        # Camera status
        self.draw.text(self.cam_pos, 'CAM: DSC0001.JPG', fill = "WHITE", font=self.font)

        # Time
        self.draw.text(
            self.time_pos,
            datetime.utcnow().strftime("%Y.%m.%d   %H:%M:%S"),
            font=self.font_small,
            fill="white",
        )

        # IP
        self.draw.text(self.ip_pos, self.get_ip(), fill = "GREEN", font=self.font_small)

    def update_icons(self):
        self.image = self.camera_icon.set_off(self.image)
        self.image = self.gps_icon.set_off(self.image)
        self.image = self.usb_icon.set_off(self.image)
        self.image = self.wifi_icon.set_off(self.image)

    def splashscreen(self):
        image = Image.open("/home/pi/Documents/oled_splashscreen.png")    
        self.display.ShowImage(image)

    def get_ip(self):
        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return IP
    
if __name__ == "__main__":
    oled_display = OledView({})
    oled_display.splashscreen()
    time.sleep(1)
    oled_display.update_view()