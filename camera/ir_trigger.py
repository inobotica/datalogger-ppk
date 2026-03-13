#!/usr/bin/env python3
"""
Example commands
python ir_trigger.py --gpio 4 --interval 3 --mode shutter
python ir_trigger.py --count 10
"""
import RPi.GPIO as GPIO
import time
import argparse

# ==========================
# CONFIG
# ==========================

CARRIER_FREQ = 40000  # 40 kHz
DUTY_CYCLE = 0.33     # 33%

# Sony timings (microseconds)
HEADER_MARK = 2320
HEADER_SPACE = 650
ONE_MARK = 1100
ZERO_MARK = 600
BIT_SPACE = 650
INTER_FRAME_GAP = 0.010  # 10ms
REPEATS = 3

# 20-bit sequences from your Arduino code
SHUTTER_NOW_20 = 0b10110100101110001111
SHUTTER_DELAY_20 = 0b11101100101110001111
VIDEO_TOGGLE_20 = 0b00010010101110001111
BITS = 20


# ==========================
# IR FUNCTIONS
# ==========================

class SonyIR:

    def __init__(self, gpio_pin):
        self.gpio = gpio_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.OUT)
        GPIO.output(self.gpio, GPIO.LOW)

        # carrier timing
        self.period = 1.0 / CARRIER_FREQ
        self.on_time = self.period * DUTY_CYCLE
        self.off_time = self.period - self.on_time

    def cleanup(self):
        GPIO.output(self.gpio, GPIO.LOW)
        GPIO.cleanup()

    def mark(self, duration_us):
        """Send carrier for duration_us microseconds"""
        end_time = time.perf_counter() + (duration_us / 1_000_000.0)

        while time.perf_counter() < end_time:
            GPIO.output(self.gpio, GPIO.HIGH)
            time.sleep(self.on_time)
            GPIO.output(self.gpio, GPIO.LOW)
            time.sleep(self.off_time)

    def space(self, duration_us):
        """LED off for duration_us"""
        GPIO.output(self.gpio, GPIO.LOW)
        time.sleep(duration_us / 1_000_000.0)

    def send_frame(self, value):
        # Header
        self.mark(HEADER_MARK)
        self.space(HEADER_SPACE)

        # 20 bits MSB-first
        for i in range(BITS):
            bit = (value >> (BITS - 1 - i)) & 1
            if bit:
                self.mark(ONE_MARK)
            else:
                self.mark(ZERO_MARK)
            self.space(BIT_SPACE)

    def send(self, value):
        for i in range(REPEATS):
            self.send_frame(value)
            if i < REPEATS - 1:
                time.sleep(INTER_FRAME_GAP)

    def shutter_now(self):
        start_time = time.time()
        self.send(SHUTTER_NOW_20)
        print("delta:", int(1000*(time.time()-start_time)))

    def shutter_delayed(self):
        self.send(SHUTTER_DELAY_20)

    def toggle_video(self):
        self.send(VIDEO_TOGGLE_20)


# ==========================
# MAIN
# ==========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpio", type=int, default=18)
    parser.add_argument("--interval", type=float, default=3.0)
    parser.add_argument(
        "--mode",
        choices=["shutter", "shutter_delay", "video"],
        default="shutter"
    )
    parser.add_argument("--count", type=int, default=0)
    args = parser.parse_args()

    ir = SonyIR(args.gpio)

    try:
        n = 0
        while True:
            if args.mode == "shutter":
                ir.shutter_now()
            elif args.mode == "shutter_delay":
                ir.shutter_delayed()
            else:
                ir.toggle_video()

            n += 1
            if args.count and n >= args.count:
                break

            time.sleep(args.interval)

    except KeyboardInterrupt:
        pass
    finally:
        ir.cleanup()


if __name__ == "__main__":
    main()