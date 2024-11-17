import asyncio
import base64

from aiogram import Bot, Dispatcher, Router
import psycopg2
from aiogram.filters import Command, CommandObject

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message


from boards import get_doctor_keyboard


API_TOKEN = '7591185961:AAFP-6N5aKUxsKEY6iLl9tuDraVxpvo7xc4'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()


conn = psycopg2.connect("dbname=doc_pat_db user=doc_pat password=27lodima host=192.168.1.111 port=5433")
cur = conn.cursor()


# Состояния для сбора данных
class SymptomStates(StatesGroup):
    temperature = State()
    pressure = State()
    # temp = State()
    condition = State()


# Начало общения с ботом
@router.message(Command(commands=["start"]))
async def start(message: Message, command: CommandObject, state: FSMContext):
    doctor_id = str(base64.b64decode(command.args)).split(':')[0][2:]
    await state.update_data(doctor_id=doctor_id)
    await state.set_state(SymptomStates.temperature)
    await message.answer("Введите температуру (36.6):")


# Сбор температуры
@router.message(SymptomStates.temperature)
async def get_temperature(message: Message, state: FSMContext):

    await state.update_data(temperature=message.text)
    await state.set_state(SymptomStates.pressure)
    await message.answer("Введите артериальное давление (120 80):")


# Сбор частоты сердечных сокращений
#@router.message(SymptomStates.temperature)
async def get_temp(message: Message, state: FSMContext):
    await state.update_data(temperature=message.text)
    await state.set_state(SymptomStates.pressure)
    await message.answer("Введите частоту сердечных сокращений (70):")


# Сбор давления
@router.message(SymptomStates.pressure)
async def get_pressure(message: Message, state: FSMContext):
    await state.update_data(pressure=message.text)
    await state.set_state(SymptomStates.condition)
    await message.answer("Как вы оцениваете ваше самочувствие?")


# Сбор общего состояния
@router.message(SymptomStates.condition)
async def get_condition(message: Message, state: FSMContext):
    # Сохраняем данные в БД
    data = await state.get_data()
    patient_id = message.from_user.id  # ID пользователя как идентификатор пациента
    doctor_id = data["doctor_id"]  # Условный ID врача
    cur.execute("""
        INSERT INTO symptom_check (patient_id, doctor_id, temperature, pressure, condition)
        VALUES (%s, %s, %s, %s, %s)
    """, (patient_id, doctor_id, data["temperature"], data["pressure"], message.text))
    conn.commit()

    # Завершаем состояние
    await state.clear()
    await message.answer("Данные успешно сохранены!", reply_markup=get_doctor_keyboard())


# Регистрация маршрутов
dp.include_router(router)


# Запуск бота
async def main():
    # await bot.send_message(chat_id=205482813, text="""Рекомендации по заболеванию: 25 ноября на приём""")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())