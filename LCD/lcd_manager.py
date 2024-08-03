# -*- coding:utf-8 -*-
import subprocess
import time

import LCD_1in44
from PIL import Image, ImageColor, ImageDraw, ImageFont

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("RGB", (disp.width, disp.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
disp.LCD_ShowImage(image, 0, 0)


def get_ip():
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    return IP


if __name__ == "__main__":
    while True:
        # draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)
        draw.ellipse((110, 10, 120, 20), outline="red", fill="red")  # A button
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(0.5)

        # draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled
        draw.ellipse((110, 10, 120, 20), outline="black", fill="black")  # A button
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(0.5)
        draw.text((10, 10), "IP: " + get_ip(), font=font, fill="white")
