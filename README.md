# datalogger-ppk
Datalogger to control a camera and geotag photos


# Setup
First install this python packages

For pi Zero GPIOs:
sudo apt remove python3-rpi.gpio
sudo apt install python3-rpi-lgpio

for code styling
python -m pip install --user pre-commit

# linux libraries
sudo apt-get install sqlite3
sudo apt install gphoto2 -y

# python libraries
pip install sqlalchemy --break-system-packages
pip install pyubx2 --break-system-packages
pip install easydict --break-system-packages

# Create database
sqlite3 /home/pi/datalogger-ppk/database/datalogger.db

# clone imu library
```sh
git clone https://github.com/niru-5/imusensor.git
cd imusensor
pip install . --break-system-packages
```

# Check i2c port
sudo i2cdetect -y 1

# Install oled library
sudo wget https://files.waveshare.com/upload/8/8d/LCD_Module_RPI_code.zip
sudo unzip LCD_Module_RPI_code.zip 
cd LCD_Module_RPI_code/RaspberryPi/
python 1inch69_LCD_test.py

# Give pi user SPI access
sudo usermod -aG gpio $USER
sudo usermod -aG spi $USER

# RPi 5 config
sudo nano /boot/firmware/config.txt
usb_max_current_enable=1

sudo -E rpi-eeprom-config --edit
original
BOOT_ORDER=0xf461

new
BOOT_ORDER=0xf416
PSU_MAX_CURRENT=5000