import RPi.GPIO as GPIO
import time


def detection(channel):
    print(int(time.time()), "Photo detected!")

HOTSHOE_PIN = 17
GPIO.setmode(GPIO.BCM)

GPIO.setup(HOTSHOE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(
    HOTSHOE_PIN,
    GPIO.FALLING,
    callback=detection,
    bouncetime=100,
)

if __name__ == "__main__":
    while True:
        time.sleep(0.1)