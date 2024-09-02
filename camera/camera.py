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
        self.photo_count = None
        self.releaseCamera()
        self.camera = gp.Camera()
        self.camera.init()

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

    def trigger_capture(self):
        # ti = time.time()
        gp.gp_camera_trigger_capture(self.camera)
        # print("GPHOTO Ellapsed time(ms):", int(1000 * (time.time() - ti)))

    def trigger_capture_cmd(self):
        ti = time.time()

        try:
            fastCapture = ["gphoto2", "--trigger-capture"]
            subprocess.run(
                fastCapture, check=True, stdout=subprocess.PIPE, universal_newlines=True
            )
        except subprocess.CalledProcessError:
            print("Error")

        print("CMD Ellapsed time(ms):", int(1000 * (time.time() - ti)))

    def start(self):
        last_shot = int(1000 * time.time())
        print("Starting Camera Thread...")

        while True:
            delta = int(1000 * time.time()) - last_shot

            if self.state.camera and self.state.db_log and delta >= 2500:
                last_shot = int(1000 * time.time())
                self.trigger_capture()


if __name__ == "__main__":
    camera = Camera("")
    os.system("pkill -f gphoto2")
    os.system("pkill -f gvfsd-gph")
    # camera.releaseCamera()
    # camera.detect_camera()
    camera.trigger_capture()
    # camera.trigger_capture_cmd()
    # camera.capture_image()
