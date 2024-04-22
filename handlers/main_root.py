from aiogram import types, Router, F
from aiogram.filters import StateFilter, or_f
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import get_naprav_by_fac, get_program_by_naprav, get_ege_by_name, proccesing, preccesing, \
    orm_get_user, orm_create_user, delete_user
from handlers.root_1 import root_1, viewer
from handlers.root_2 import root_2, filler

from kbrd.reply import start_kb, menu_kb, get_keyboard


main_root = Router()
main_root.include_router(root_1)
main_root.include_router(root_2)

dt_state = {"view": viewer,
            "fill": filler}

class stater(StatesGroup):
    bac = State()
    mag = State()
    spec = State()
    asp = State()



async def check_state(stater: StatesGroup, current_state: State) -> State:
    prev = None
    for step in stater.__all_states__:
        if not isinstance(step, list) and step.state == current_state:
            return prev
        prev = step


@main_root.message(Command("start"))
async def start(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer(f"""Привет, {message.from_user.full_name}!\nМогу помочь с выбором подходящей профессии.\nПоказать интересующие тебя направления\nИтак, чего ты хочешь?""", reply_markup=menu_kb)
    mod = await orm_get_user(session, message.from_user.id)
    print(f"[INFO main_root] {mod}")

@main_root.message(F.text == "Бакалавриат")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Выбери действие", reply_markup=start_kb)
    us = await orm_get_user(session, message.from_user.id)
    if us == None:
        await orm_create_user(session, message.from_user.id)
        await session.commit()
    await state.set_state(stater.bac)


@main_root.message(or_f(F.text == "Специалитет", F.text == "Магистратура", F.text == "Аспирантура"))
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Раздел находится в разработке", reply_markup=get_keyboard(["отмена"], placeholder="В разработке", sizes=([1])))
    await state.set_state(stater.mag)

@main_root.message(stater.bac, F.text == "Я уже знаю куда поступлю")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Поздравляем тебя")

@main_root.message(StateFilter('*'), Command('отмена'))
@main_root.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return


    await state.clear()
    await message.answer("Действия отменены", reply_markup=menu_kb)








