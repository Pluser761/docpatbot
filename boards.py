from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_doctor_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Вызвать врача", callback_data="call_doctor")
    return builder.as_markup()