# datalogger-ppk
Datalogger to control a camera and geotag photos


# Setup
First install this python packages

For pi Zero GPIOs:
sudo apt remove python3-rpi.gpio
sudo apt install python3-rpi-lgpio

for code styling
pip install git+https://github.com/psf/black --break-system-packages
pip install isort --break-system-packages

# linux libraries
sudo apt-get install sqlite3

# python libraries
pip install sqlalchemy --break-system-packages
pip install pyubx2 --break-system-packages

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