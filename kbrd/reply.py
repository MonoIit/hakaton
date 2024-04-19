from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
    btns: list[str],
    placeholder: str = None,
    sizes: tuple[int] = (2,),
):
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона",
            placeholder="Что вас интересует?",,
            sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
            resize_keyboard=True, input_field_placeholder=placeholder)

menu_kb = get_keyboard(["Бакалавриат", "Специалитет", "Магистратура", "Аспирантура"],
                       placeholder="Куда поступаем?", sizes=(1, 1, 1, 1))
start_kb = get_keyboard(["Покажи мне направления", "Куда поступить?", "Я уже знаю куда поступлю", "Загрузить данные"], placeholder="Что вас интересует?", sizes=(1, 1, 1, 1))