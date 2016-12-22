import datetime
from enum import Enum

import arrow
import peewee
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('temperatures.db')

PRINTABLE_ROOM_NAMES = {
    0: "Unknown",
    1: "Outside",
    2: "Living room",
    3: "Office",
    4: "Bedroom"
}


class Rooms(Enum):
    UNKNOWN = 0
    OUTSIDE = 1
    LIVING_ROOM = 2
    OFFICE = 3
    BEDROOM = 4


class BatteryData(peewee.Model):
    class Meta:
        database = db

    sensor_id = peewee.IntegerField(primary_key=True)
    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    last_seen_status = peewee.TextField(default="UNKNOWN")


class SensorData(peewee.Model):
    class Meta:
        database = db

    timestamp = peewee.DateTimeField(default=datetime.datetime.now, index=True)
    temperature = peewee.FloatField(default=0)
    humidity = peewee.FloatField(default=0, null=True)
    sensor_id = peewee.IntegerField(default=-1)
    channel = peewee.IntegerField(null=True)
    room = peewee.IntegerField(index=True)

    def __str__(self):
        return "[%s][%s] - Temperature %f C, Humidity %f %%" % \
               (arrow.get(self.timestamp).format("YYYY-MM-DD HH:mm:ss"),
                Rooms(self.room), float(self.temperature), float(self.humidity) if self.humidity else 0.0)


def get_current_status():
    current_entries = {}
    for room in Rooms:
        try:
            entry = SensorData.select().where(SensorData.room == room.value).order_by(SensorData.timestamp.desc()).get()
        except peewee.DoesNotExist:
            continue

        current_entries[PRINTABLE_ROOM_NAMES[room.value]] = {"temperature": entry.temperature, "humidity": entry.humidity,
                                                             "time": arrow.get(entry.timestamp).format("HH:mm, DD.MM.YYYY")}

        # Check for battery status
        battery = BatteryData.select().where(BatteryData.sensor_id == entry.sensor_id).order_by(BatteryData.timestamp.desc()).get()
        current_entries[PRINTABLE_ROOM_NAMES[room.value]]["battery"] = battery.last_seen_status

    return current_entries


db.connect()
db.create_tables([SensorData, BatteryData], safe=True)
