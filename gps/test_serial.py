from serial import Serial
from pyubx2 import UBXReader
from datetime import datetime, timezone, timedelta

stream = Serial('/dev/ttyACM0', 115200, timeout=3)
ubr = UBXReader(stream)

def get_gps_time(itow_ms):
    now = datetime.now(timezone.utc)
    epoch = datetime(1980, 1, 6, tzinfo=timezone.utc)
    difference = now - epoch
    epoch_weeks = int(difference.total_seconds() / 604800)
    gps_time = epoch + timedelta(weeks=epoch_weeks, milliseconds=itow_ms)
    
    return gps_time

index = 0

while index<20:
    raw_data, parsed_data = ubr.read()
    if parsed_data.identity == "NAV-PVT":
        print(parsed_data)
        valid_date = getattr(parsed_data, "validDate", 0) == 1
        valid_time = getattr(parsed_data, "validTime", 0) == 1
        fully_resolved = getattr(parsed_data, "fullyResolved", 0) == 1

        if valid_date and valid_time and fully_resolved:
            dt = f"{parsed_data.year:04d}-{parsed_data.month:02d}-{parsed_data.day:02d} {parsed_data.hour:02d}:{parsed_data.min:02d}:{parsed_data.second:02d}"
            print(f"GPS time: {dt}  (tAcc={getattr(parsed_data,'tAcc',None)} ns)")
            print("SYS time:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            print("tow time:", get_gps_time(parsed_data.iTOW))

    index += 1
