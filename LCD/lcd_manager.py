# -*- coding:utf-8 -*-
import subprocess
import time

from PIL import Image, ImageColor, ImageDraw, ImageFont

from . import LCD_1in44


class LCD:
    def __init__(self, state):
        self.state = state

        # 240x240 display with hardware SPI:
        self.disp = LCD_1in44.LCD()
        self.Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
        self.disp.LCD_Init(self.Lcd_ScanDir)
        self.disp.LCD_Clear()

        # Create blank image for drawing.
        self.image = Image.new("RGB", (self.disp.width, self.disp.height))
        self.image.rotate(180)

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()
        # self.font = ImageFont.truetype("DejaVuSans-Bold.ttf", 10)

        # Draw a black filled box to clear the image.
        self.draw.rectangle(
            (0, 0, self.disp.width, self.disp.height), outline=0, fill=0
        )
        self.disp.LCD_ShowImage(self.image, 0, 0)

        self.wifi_x_pos = 10
        self.wifi_y_pos = 110
        self.wifi_circle_width = 10

    def start(self):
        print("Starting LCD Thread...")

        while True:
            self.draw.text(
                (10, 10),
                "GPS",
                font=self.font,
                fill="green" if self.state.gps else "red",
            )

            self.draw.text(
                (40, 10),
                "CAM",
                font=self.font,
                fill="green" if self.state.camera else "red",
            )

            self.draw.text(
                (70, 10),
                "USB",
                font=self.font,
                fill="green" if self.state.media else "red",
            )

            log_status = "LOG: " + (
                self.state.db_log.filename[-10:] if self.state.db_log else "EN ESPERA"
            )
            print("LOG status", log_status)

            self.draw.text(
                (10, 30),
                log_status,
                font=self.font,
                fill="white",
            )

            self.draw.text(
                (self.wifi_x_pos, self.wifi_y_pos),
                "IP: " + self.state.wifi,
                font=self.font,
                fill="white",
            )

            color = "red" if self.state.db_log else "green"
            self.draw.ellipse(
                (110, 110, 120, 120),
                outline="black",
                fill=color if int(time.time()) % 2 else "black",
            )  # A button

            self.disp.LCD_ShowImage(self.image, 0, 0)
            time.sleep(0.1)

    def get_ip(self):
        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return IP


if __name__ == "__main__":
    lcd = LCD("")

    while True:
        # draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)
        lcd.draw.ellipse((110, 110, 120, 120), outline="red", fill="red")  # A button
        lcd.disp.LCD_ShowImage(lcd.image, 0, 0)
        time.sleep(0.5)

        # draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled
        lcd.draw.ellipse(
            (110, 110, 120, 120), outline="black", fill="black"
        )  # A button
        lcd.disp.LCD_ShowImage(lcd.image, 0, 0)
        time.sleep(0.5)
        lcd.draw.text(
            (lcd.wifi_x_pos, lcd.wifi_y_pos),
            "IP: " + lcd.get_ip(),
            font=lcd.font,
            fill="white",
        )
