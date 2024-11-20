import os
import subprocess
import time
from pwd import getpwuid


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
        self.media = True if "flash" in output else False
        self.gps = True if "u-blox" in output and "ACM" in output2 else False
        self.usb_port = os.path.join("/dev/", output2)

        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        self.wifi = IP

        self.storage_name = self.get_usb_connected()

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
