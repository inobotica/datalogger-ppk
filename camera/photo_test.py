import subprocess


class Photo:
    def __init__(self) -> None:
        self.name = ""
        self.count = 0

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


f = open("/home/pi/datalogger-ppk/camera/image.log", "w")
f.close()

cmd = [
    "gphoto2",
    "--debug",
    "--debug-loglevel=data",
    "--debug-logfile=/home/pi/datalogger-ppk/camera/image.log",
    "--wait-event=3s",
    "--capture-image",
]

ps = subprocess.run(cmd, capture_output=True, text=True)

lines = open("image.log").readlines()
name = None

for index in range(10000, len(lines)):
    line = lines[index].strip()

    if "D.S.C." in line:
        name = line
        break

if name:
    print(name)
    photo = Photo()
    count = name[name.index("D.S.C.") + 6 :].replace(".", "")
    print(count)
    photo.count = count
    print(photo.name)
    print(photo.increase_count())
