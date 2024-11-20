import os
import sys
import time

import numpy as np
import smbus
from imusensor.filters import kalman
from imusensor.MPU9250 import MPU9250


class IMUSensor:
    def __init__(self, status):
        self.status = status
        self.address = 0x68
        self.bus = smbus.SMBus(1)
        self.imu = MPU9250.MPU9250(self.bus, self.address)
        self.imu.begin()
        self.sensorfusion = kalman.Kalman()

    def start(self):
        print("Starting IMU Thread...")

        self.imu.readSensor()
        self.imu.computeOrientation()
        self.sensorfusion.roll = self.imu.roll
        self.sensorfusion.pitch = self.imu.pitch
        self.sensorfusion.yaw = self.imu.yaw

        self.count = 0
        self.currTime = time.time()

        while True:
            self.imu.readSensor()
            self.imu.computeOrientation()
            self.newTime = time.time()
            self.dt = self.newTime - self.currTime
            self.currTime = self.newTime

            self.sensorfusion.computeAndUpdateRollPitchYaw(
                self.imu.AccelVals[0],
                self.imu.AccelVals[1],
                self.imu.AccelVals[2],
                self.imu.GyroVals[0],
                self.imu.GyroVals[1],
                self.imu.GyroVals[2],
                self.imu.MagVals[0],
                self.imu.MagVals[1],
                self.imu.MagVals[2],
                self.dt,
            )

            if __name__ == "__main__":
                print(
                    "Kalmanroll:{0} KalmanPitch:{1} KalmanYaw:{2} ".format(
                        int(self.sensorfusion.roll),
                        int(self.sensorfusion.pitch),
                        int(self.sensorfusion.yaw),
                    )
                )
            else:
                self.status.imu = self.sensorfusion
                # print(
                #     "Kalmanroll:{0} KalmanPitch:{1} KalmanYaw:{2} ".format(
                #         int(self.sensorfusion.roll),
                #         int(self.sensorfusion.pitch),
                #         int(self.sensorfusion.yaw),
                #     )
                # )

            time.sleep(0.01)


if __name__ == "__main__":
    imu = IMUSensor("")
    imu.start()
