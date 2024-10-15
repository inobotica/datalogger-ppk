import csv
import json
import os
from datetime import datetime, timezone
from pwd import getpwuid

MASS_STORAGE_DIR = "/media/pi/"
LOGS_FOLDER = "logs"
TIMESTAMP_FORMAT = "%Y/%m/%d %H:%M:%S.%f"


class Waypoint:
    def __init__(self, timestamp, epoch, lat, lon, alt):
        self.time = timestamp
        self.unix_time = epoch
        self.lat = lat
        self.lon = lon
        self.alt = alt


class PhotoPoint(Waypoint):
    def __init__(self, pitch, roll, photo, **kwargs):
        super().__init__(**kwargs)
        self.pitch = pitch
        self.roll = roll
        self.photo = photo


def is_there_usb_connected():
    is_there_folder = os.path.exists(MASS_STORAGE_DIR)

    if not is_there_folder:
        return None

    dir_list = find_owner(os.listdir(MASS_STORAGE_DIR))

    if not len(dir_list):
        return None
    else:
        path = os.path.join(MASS_STORAGE_DIR, dir_list[-1])
        return path


def find_owner(folders):
    filtered_folders = []

    for f in folders:
        folder_path = os.path.join(MASS_STORAGE_DIR, f)
        owner = getpwuid(os.stat(folder_path).st_uid).pw_name

        if owner == "pi":
            filtered_folders.append(f)

    return filtered_folders


def get_pos_files(filepath):
    # files = [file for file in os.listdir(os.path.join(filepath, LOGS_FOLDER)) if file.endswith("rover.pos")]
    files = [file for file in os.listdir(filepath) if file.endswith("rover.pos")]
    return files


def convert_to_waypoint(line):
    line = [col for col in line if col]

    if len(line) >= 5:
        timestamp = datetime.strptime(line[0] + " " + line[1], TIMESTAMP_FORMAT)
        timestamp = timestamp.replace(tzinfo=timezone.utc)
        epoch = timestamp.timestamp()
        lat = float(line[2])
        lon = float(line[3])
        alt = float(line[4])

        wp_object = Waypoint(
            timestamp=timestamp, epoch=epoch, lat=lat, lon=lon, alt=alt
        )
        return wp_object

    return None


def parse_file(filepath):
    file_data = open(filepath, "r").readlines()
    file_data = [line.split(" ") for line in file_data if not line.startswith("%")]
    waypoints = [convert_to_waypoint(line) for line in file_data]

    return waypoints


def match_points(gps_points, log_points):
    csv_points = []

    for log_point in log_points:
        deltas = []

        for gps_point in gps_points:
            delta = abs(log_point.unix_time - gps_point.unix_time) if gps_point else 99
            deltas.append(delta)

        min_delta = min(deltas)
        min_delta_index = deltas.index(min_delta)

        if min_delta < 1:
            log_point.lat = gps_points[min_delta_index].lat
            log_point.lon = gps_points[min_delta_index].lon
            log_point.time = gps_points[min_delta_index].time
            log_point.alt = gps_points[min_delta_index].alt
            csv_points.append(log_point)

            # Remove gps point to avoid relating it to another photo
            gps_points[min_delta_index] = None

    return csv_points


def save_csv_file(filepath, csv_points):
    fields = [
        "time",
        "lat",
        "lon",
        "alt",
        "pitch",
        "roll",
        "photo",
        "id",
        "unix_time",
        "_sa_instance_state",
        "datalog_id",
    ]
    filepath = filepath.replace(".pos", ".csv")
    csv_data = [csv_row.__dict__ for csv_row in csv_points]

    print("Saving CSV file...", filepath)

    with open(filepath, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(csv_data)

    print("CSV Saved!")


class Geotagger:
    def __init__(self, database, state):
        self.database = database
        self.state = state

    def run(self):
        # Get UB path
        filepath = is_there_usb_connected()

        if not filepath:
            print("No USB connected!")
            return None

        print("USB path:", filepath)

        # Get POS files on USB path
        self.state.geotag = "Leyendo .POS"
        files = get_pos_files(filepath)

        for file in files:

            # file_path = os.path.join(filepath, LOGS_FOLDER, file)
            file_path = os.path.join(filepath, file)
            file_waypoints = parse_file(file_path)
            print("Reading POS file...", file_path)

            # Get database information
            self.state.geotag = "Leyendo DB..."
            db_filename = "_".join(file.split("_")[:2])
            log_points = self.database.get_gps_points_cloud(db_filename)
            print("Reading DB data...", db_filename)

            if len(log_points) < 1:
                continue

            csv_points = match_points(gps_points=file_waypoints, log_points=log_points)
            self.state.geotag = "Guardando .CSV"
            save_csv_file(filepath=file_path, csv_points=csv_points)

        self.state.geotag = None


if __name__ == "__main__":
    filepath = is_there_usb_connected()

    if not filepath:
        print("No USB connected!")
        exit(0)

    print("USB:", filepath)
    files = get_pos_files(filepath)

    for file in files:

        file_path = os.path.join(filepath, LOGS_FOLDER, file)
        print(file_path)
        parse_file(file_path)
