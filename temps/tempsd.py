import datetime
import json

import dateutil
from database import Rooms, SensorData, BatteryData
import arrow
import subprocess

OUTDOOR_SENSOR_ID = 5
OUTDOOR_SENSOR_NAME = "Prologue"
INDOOR_SENSOR_NAME = "Nexus"

LIVING_ROOM_SENSOR_ID = 94
OFFICE_SENSOR_ID = 45
BEDROOM_SENSOR_ID = 108

last_readouts = {}


def read_sensors():
    process = subprocess.Popen(["rtl_433", "-Fjson", "-R03", "-R19", "-q", "-Csi", "-U"], stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if line != '':
            process_sensor_line(line.decode('utf-8'))


def update_battery_status(sensor_id, timestamp, status):
    existing_status, _ = BatteryData.get_or_create(sensor_id=sensor_id)
    existing_status.timestamp = timestamp.datetime
    existing_status.last_seen_status = status
    existing_status.save()


def process_sensor_line(line):
    try:
        sensor_json = json.loads(line)
    except ValueError:
        return

    room = get_room_for_sensor_data(sensor_json)
    if not room:
        print("Unknown sensor line [%s]" % line)
        return

    sensor_id = sensor_json["id"]
    timestamp = arrow.get(sensor_json["time"], "YYYY-MM-DD HH:mm:ss").replace(tzinfo=dateutil.tz.tzutc())
    battery_status = sensor_json["battery"]

    update_battery_status(sensor_id, timestamp, battery_status)

    # We throttle the readouts to once per minute to save on data
    last_readout = last_readouts.get(sensor_id)

    if last_readout and (timestamp.datetime - last_readout.timestamp) < datetime.timedelta(minutes=1):
        print("Skipping readout for updated %s..." % (room, ))
        return

    sensor_data = SensorData(timestamp=timestamp.datetime,
                             temperature=sensor_json["temperature_C"],
                             humidity=sensor_json.get("humidity"),
                             sensor_name=sensor_json["model"],
                             sensor_id=sensor_id,
                             channel=sensor_json.get("channel"),
                             room=room.value)
    sensor_data.save()
    print(sensor_data)
    last_readouts[sensor_id] = sensor_data


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
