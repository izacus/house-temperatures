import datetime
from enum import Enum
import peewee
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('temperatures.db')


class Rooms(Enum):
    UNKNOWN = 0
    OUTSIDE = 1
    LIVING_ROOM = 2
    OFFICE = 3
    BEDROOM = 4


class SensorData(peewee.Model):
    class Meta:
        database = db

    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    temperature = peewee.FloatField(default=0)
    humidity = peewee.FloatField(default=0, null=True)
    sensor_id = peewee.IntegerField()
    channel = peewee.IntegerField(null=True)
    room = peewee.IntegerField()

db.connect()
db.create_tables([SensorData], safe=True)
