import os
import subprocess
import time
from pwd import getpwuid
from typing import Dict, Any

import serial
from serial.tools import list_ports

ESPRESSIF_VID = 0x303A
BAUDRATE = 115200

def _is_esp32_by_metadata(p) -> bool:
    """
    Fast, non-intrusive ESP32 detection via USB metadata.
    """
    if p.vid == ESPRESSIF_VID:
        return True

    text = " ".join(
        str(x).lower()
        for x in [p.manufacturer, p.product, p.description, p.hwid]
        if x
    )

    return "espressif" in text

def identify_ports() -> Dict[str, str]:
    """
    Returns a dict with keys:
      - 'mapir' → ESP32 port (if present)
      - 'gps'   → other serial device (if present)
    """
    ports = [
        p for p in list_ports.comports()
        if p.device.startswith("/dev/tty")
    ]

    esp32_port = None
    other_ports = []

    # 1) First pass: metadata-only (no side effects)
    for p in ports:
        if _is_esp32_by_metadata(p):
            esp32_port = p.device
        else:
            other_ports.append(p.device)

    result: Dict[str, str] = {"mapir": None, "gps": None}

    if esp32_port:
        result["mapir"] = esp32_port

    if other_ports:
        result["gps"] = other_ports[0]

    return result

class Photo:
    def __init__(self) -> None:
        self.name = ""
        self.count = 0
        self.is_busy = False

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, current_count):
        self._count = int(current_count)
        self.name = f"DSC{self._count:05}.JPG"

    def increase_count(self):
        self.count += 1
        self.count = int(self.count%10000)
        self.name = f"DSC{self._count:05}.JPG"
        return self.name


class Status:
    def __init__(self):
        self.db_log = None
        self.camera = False
        self.media = False
        self.gps = False
        self.wifi = False
        self.imu = None
        self.photo = Photo()
        self.usb_port = None
        self.geotag = None
        self.storage_name = None
        self.MASS_STORAGE_DIR = "/media/pi/"
        self.path = None
        self.gps_port = None
        self.mapir_port = None
        self.tow_time = None

    def get_usb_connected(self):
        is_there_folder = os.path.exists(self.MASS_STORAGE_DIR)

        if not is_there_folder:
            return None

        dir_list = self.find_owner(os.listdir(self.MASS_STORAGE_DIR))

        if not len(dir_list):
            return None
        else:
            # path = os.path.join(self.MASS_STORAGE_DIR, dir_list[-1])
            path = dir_list[-1]
            return path

    def find_owner(self, folders):
        filtered_folders = []

        for f in folders:
            folder_path = os.path.join(self.MASS_STORAGE_DIR, f)
            owner = getpwuid(os.stat(folder_path).st_uid).pw_name

            if owner == "pi":
                filtered_folders.append(f)

        return filtered_folders

    def check_status(self):
        self.storage_name = self.get_usb_connected()

        cmd = "lsusb | grep -i -v hub"
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        output = ps.communicate()[0].decode("utf-8").strip().lower()

        cmd = "ls /dev/ | grep -i ACM"
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        output2 = ps.communicate()[0].decode("utf-8").strip()

        self.camera = True if "sony" in output else False
        self.media = (
            True if self.storage_name else False
        )  # if "flash" in output else False
        self.gps = True if "u-blox" in output and "ACM" in output2 else False
        self.usb_port = os.path.join("/dev/", output2)

        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        self.wifi = IP
        self.is_there_usb_connected()

        serial_ports = identify_ports()
        self.gps_port = serial_ports.get("gps", None)
        self.mapir_port = serial_ports.get("mapir", None)

    def is_there_usb_connected(self):
        dir_list = os.listdir(self.MASS_STORAGE_DIR)

        if not len(dir_list):
            self.path = None
        else:
            self.path = os.path.join(self.MASS_STORAGE_DIR, dir_list[-1])

    def start(self):
        print("Starting Status Thread...")

        while True:
            self.check_status()
            time.sleep(0.2)

    def __str__(self):
        return f"cam:{self.camera} | media:{self.media} | gps:{self.gps} | wifi:{self.wifi}"


if __name__ == "__main__":
    usb = Status()
    usb.check_status()
    print("status", usb)
