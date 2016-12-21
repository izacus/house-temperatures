import datetime
from enum import Enum

import arrow
import peewee
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('temperatures.db')


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

db.connect()
db.create_tables([SensorData, BatteryData], safe=True)
