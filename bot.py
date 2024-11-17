import threading
from datetime import datetime
from distutils.command.check import check

import telebot
from flask import jsonify, request, Flask
from flask_restful import Api, Resource
from peewee import Check
from telebot import StateMemoryStorage, types
from telebot.states.sync import StateContext

from fsm import Survey
from models import Patient, SymptomCheck

app = Flask(__name__)
api = Api(app)
bot = telebot.TeleBot("1188108218:AAGc9hbgoUf6ZAO-3mEn35g5SALMjmLqfnE", state_storage=StateMemoryStorage(), use_class_middlewares=True)


@bot.message_handler(commands=['start'])
def start(message: types.Message, state: StateContext):
    bot.send_message(message.chat.id, "Привет! Давайте начнем опрос. Какова ваша температура?")
    state.set(Survey.temp)


@bot.message_handler(state=Survey.temp)
def get_temp(message, state: StateContext):
    try:
        temp = float(message.text)
        state.add_data(temp=temp)
        bot.send_message(message.chat.id, f"Температура: {temp}°C. А какое у вас давление?")
        state.set(Survey.pressure)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное значение температуры.")


@bot.message_handler(state=Survey.pressure)
def get_pressure(message, state: StateContext):
    try:
        pressure = message.text.split()
        systolic, diastolic = map(int, pressure)
        state.add_data(pressure=(systolic, diastolic))
        bot.send_message(message.chat.id,
                         f"Давление: {systolic}/{diastolic} мм рт. ст. Какие у вас есть общие замечания?")
        state.set(Survey.common)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите давление в формате 'систолическое диастолическое'.")


@bot.message_handler(state=Survey.common)
def get_common(message, state: StateContext):
    common_feedback = message.text
    bot.send_message(message.chat.id,
                     f"Спасибо за информацию! Вот ваш отчет:\nТемпература: {state.get('temp')}°C\nДавление: {state.get('pressure')[0]}/{state.get('pressure')[1]} мм рт. ст.\nОбщие замечания: {common_feedback}")
    state.delete()


@bot.message_handler(func=lambda m: True)
def fallback_handler(message):
    bot.send_message(message.chat.id, "Please follow the flow of the survey.")


# Ресурсы API
class PatientList(Resource):
    def get(self):
        patients = Patient.select()
        return jsonify([
            {
                "id": patient.id,
                "tg_id": patient.tg_id,
                "doctor_id": patient.doctor_id,
                "checks": [
                    {
                        "id": check.id,
                        "date": check.date.strftime("%d-%m-%Y"),
                        "dayPart": check.dayPart,
                        "symptom": check.symptom.name,
                        "val": check.val,
                    }
                    for check in patient.symptoms
                ]
            } for patient in patients])

    def post(self):
        data = request.json
        skills = ','.join(data.get('skills', []))
        patient = Patient.create(title=data['title'], skills=skills)
        return jsonify({"id": patient.id, "name": patient.title, "skills": patient.skills.split(',')}), 201


api.add_resource(PatientList, '/patients')


def start_bot():
    bot.polling(non_stop=True)


def start_flask():
    app.run(debug=True, port=5000, use_reloader=False)


if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot)
    flask_thread = threading.Thread(target=start_flask)

    bot_thread.start()
    flask_thread.start()

    bot_thread.join()
    flask_thread.join()