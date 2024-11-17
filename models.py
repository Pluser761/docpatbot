from datetime import date
from enum import Enum

from flask_restful.fields import Boolean
from peewee import Model, PostgresqlDatabase, CharField, ForeignKeyField, DateField, SqliteDatabase, BooleanField

db = PostgresqlDatabase(
    'doc_pat_db',
    user='doc_pat',
    password='27lodima',
    host='localhost',
    port=5432
)

class BaseModel(Model):
    class Meta:
        database = db


class Patient(BaseModel):
    tg_id = CharField(unique=True)
    doctor_id = CharField()


class DayPart(Enum):
    Morning = 'm'
    Evening = 'e'


class Severity(Enum):
    High = 'h'
    Medium = 'm'
    Low = 'l'


class Symptom(BaseModel):
    name = CharField(unique=True)


class SymptomCheck(BaseModel):
    patient = ForeignKeyField(Patient, related_name='symptoms', backref='symptoms')
    date = DateField()
    dayPart = CharField(choices=DayPart)
    symptom = ForeignKeyField(Symptom, related_name='checks', backref='checks')
    val = CharField()
    # severity = CharField(choices=Severity)


db.connect()
db.create_tables([Patient, SymptomCheck, Symptom])


p, b = Patient.get_or_create(
    tg_id=123,
    doctor_id=321,
)

s, b = Symptom.get_or_create(
    name = "Temp"
)

SymptomCheck.get_or_create(
    patient=p,
    symptom=s,
    date=date(2024, 12, 25),
    dayPart=DayPart.Morning.value,
    val="good mood"
    #severity=Severity.High.value,
)