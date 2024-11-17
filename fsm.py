from telebot.states import StatesGroup, State


class Survey(StatesGroup):
    temp = State()
    pressure = State()
    common = State()
