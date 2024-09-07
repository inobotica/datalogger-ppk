import os
import subprocess
import sys
import time

import gphoto2 as gp


class Camera:
    def __init__(self, state) -> None:
        self.state = state
        self.camera_name = None
        self.settings = None
        # self.releaseCamera()
        # self.camera = gp.Camera()
        # self.camera.init()

    def get_summary(self) -> None:
        text = self.camera.get_summary()
        print("Summary")
        print("=======")
        print(str(text))

    def detect_camera(self):
        cameras = gp.check_result(gp.gp_camera_autodetect())

        if cameras:
            for name, addr in cameras:
                print(f"Camera name:{name}")
                self.camera_name = name
                return True

        return False

    def releaseCamera(self):
        print("Releasing camera...")
        errorTrace = "kill gphoto"

        cmd = "pkill -f gphoto2"
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        cmd = "gphoto2 --set-config capturetarget=1"
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        try:
            killGphoto = ["pkill", "-f", "gphoto2"]
            subprocess.run(
                killGphoto, check=True, stdout=subprocess.PIPE, universal_newlines=True
            )
            print(" - Gphoto2 killed")
            errorTrace = "kill kernel"

            killKernel = ["pkill", "-f", "gvfsd-gph"]
            subprocess.run(
                killKernel, check=True, stdout=subprocess.PIPE, universal_newlines=True
            )
            print(" - Kernel killed")
            errorTrace = "target"

            setTarget = ["gphoto2", "--set-config", "capturetarget=1"]
            subprocess.run(
                setTarget, check=True, stdout=subprocess.PIPE, universal_newlines=True
            )
            print(" - Targed setted")

        except subprocess.CalledProcessError:
            print(errorTrace, "Camera already released")

    def capture_image(self):
        ti = time.time()
        file_path = gp.check_result(
            gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE)
        )

        print("Camera file path: {0}/{1}".format(file_path.folder, file_path.name))
        print("GPHOTO Ellapsed time(ms):", int(1000 * (time.time() - ti)))

    def capture_image_cmd(self):
        if not self.state.camera:
            return False

        print("Taking photo...")

        image_path = "/home/pi/datalogger-ppk/camera/image.log"
        f = open(image_path, "w")
        f.close()

        cmd = [
            "gphoto2",
            "--debug",
            "--debug-loglevel=data",
            f"--debug-logfile={image_path}",
            "--wait-event=3s",
            "--capture-image",
        ]
        subprocess.run(cmd, capture_output=True, text=True)

        lines = open(image_path).readlines()
        name = None

        for index in range(10000, len(lines)):
            line = lines[index].strip()

            if "D.S.C." in line:
                name = line
                break

        if name:
            print("PTP line", name)
            count = name[name.index("D.S.C.") + 6 :].replace(".", "")
            self.state.photo.count = count
            print("Photo taken:", self.state.photo.name)
            return True

        return False

    def trigger_capture(self):
        if not self.state.photo.count:
            self.capture_image_cmd()
            time.sleep(10)

        if self.state.camera:
            self.state.photo.increase_count()
            gp.gp_camera_trigger_capture(self.camera)
            print("photo", self.state.photo.name)

    def trigger_capture_cmd(self):
        if self.state.camera:
            self.state.photo.increase_count()
            cmd = ["gphoto2", "--trigger-capture"]
            subprocess.run(cmd, capture_output=True, text=True)
            print("photo", self.state.photo.name)

    def start(self):
        last_shot = int(1000 * time.time())
        print("Starting Camera Thread...")

        while True:
            delta = int(1000 * time.time()) - last_shot

            if self.state.camera and self.state.db_log and delta >= 2500:
                print("delta", delta)
                last_shot = int(1000 * time.time())
                self.trigger_capture_cmd()


if __name__ == "__main__":
    camera = Camera("")
    os.system("pkill -f gphoto2")
    os.system("pkill -f gvfsd-gph")
    # camera.releaseCamera()
    # camera.detect_camera()
    camera.trigger_capture()
    # camera.trigger_capture_cmd()
    # camera.capture_image()
