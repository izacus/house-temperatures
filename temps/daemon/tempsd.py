import json

import dateutil
from temps.database import Rooms, SensorData
import arrow
import subprocess

OUTDOOR_SENSOR_ID = 5
OUTDOOR_SENSOR_NAME = "Prologue"
INDOOR_SENSOR_NAME = "Nexus"

LIVING_ROOM_SENSOR_ID = 94
OFFICE_SENSOR_ID = 45
BEDROOM_SENSOR_ID = 108


def read_sensors():
    process = subprocess.Popen(["rtl_433", "-Fjson", "-R03", "-R19", "-q", "-Csi", "-U"], stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if line != '':
            process_sensor_line(line)


def process_sensor_line(line):
    try:
        sensor_json = json.loads(line)
    except json.JSONDecodeError:
        return

    room = get_room_for_sensor_data(sensor_json)
    if not room:
        print("Unknown sensor line [%s]" % line)
        return

    # 2016-12-20 21:56:36
    timestamp = arrow.get(sensor_json["time"], "YYYY-MM-DD HH:mm:ss").replace(tzinfo=dateutil.tz.tzutc())
    sensor_data = SensorData(timestamp=timestamp.datetime,
                             temperature=sensor_json["temperature_C"],
                             humidity=sensor_json.get("humidity"),
                             sensor_name=sensor_json["model"],
                             sensor_id=sensor_json["id"],
                             channel=sensor_json.get("channel"),
                             room=room.value)
    sensor_data.save()
    print(sensor_data)


def get_room_for_sensor_data(sensor_json):
    if "temperature_C" not in sensor_json or \
       "id" not in sensor_json or \
       "model" not in sensor_json or \
       "time" not in sensor_json:
        return None

    if OUTDOOR_SENSOR_NAME in sensor_json["model"] and OUTDOOR_SENSOR_ID == sensor_json["id"]:
        return Rooms.OUTSIDE

    if INDOOR_SENSOR_NAME in sensor_json["model"]:
        if LIVING_ROOM_SENSOR_ID == sensor_json["id"]:
            return Rooms.LIVING_ROOM
        elif OFFICE_SENSOR_ID == sensor_json["id"]:
            return Rooms.OFFICE
        elif BEDROOM_SENSOR_ID == sensor_json["id"]:
            return Rooms.BEDROOM

    return None

if __name__ == "__main__":
    print("Starting tempsd....")
    read_sensors()
