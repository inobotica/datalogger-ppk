import subprocess
import time


class Status:
    def __init__(self):
        self.camera = False
        self.media = False
        self.gps = False
        self.wifi = False

    def check_status(self):
        cmd = "lsusb | grep -i -v hub"
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        output = ps.communicate()[0].decode("utf-8").strip().lower()

        self.camera = True if "sony" in output else False
        self.media = True if "flash" in output else False
        self.gps = True if "u-blox" in output else False

        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        self.wifi = IP

    def start(self):
        while True:
            self.check_status()
            time.sleep(0.2)

    def __str__(self):
        return f"cam:{self.camera} | media:{self.media} | gps:{self.gps} | wifi:{self.wifi}"


if __name__ == "__main__":
    usb = Status()
    usb.check_status()
    print(usb)
