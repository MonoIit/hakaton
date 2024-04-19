from aiogram.filters import StateFilter, Command
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import get_naprav_by_fac, get_program_by_naprav, get_ege_by_name, proccesing, preccesing
from handlers.aditional_data import *
from kbrd import reply, inline


root_1 = Router()

class viewer(StatesGroup):
    facultet = State()
    napravlenie = State()
    name = State()

    end = State()

    texts = {
        'viewer:facultet': 'Введите название факультета:',
        'viewer:napravlenie': 'Выберите направление подготовки',
        'viewer:name': 'Выберите программу подготовки'
    }

@root_1.message(StateFilter('*'), Command('назад'))
@root_1.message(StateFilter('*'), F.text.casefold() == 'назад')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    print(f"[INFO] {type(current_state)}")
    if current_state == viewer.facultet:
        await message.answer("Отступать некуда!")
        return


    previous = None
    for step in viewer.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            print(f"[INFO_root_1] {previous.state}")
            await message.answer(
                f"Один шаг назад - два вперёд! \n{viewer.texts[previous.state]}"
            )
            return
        previous = step



@root_1.message(viewer.facultet, F.text)
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(facultet=message.text)
    dt = set()
    btns = list()
    for napr in await proccesing(session, await get_naprav_by_fac(message.text)):
        if napr.mesta_b == 0:
            dt.add(f"{napr.napravlenie} (ком.)")
        else:
            dt.add(napr.napravlenie)
    for i in dt:
        btns.append(f"{i}\n")
    await message.answer("Выбирете какое направление вам нравиться:",
                         reply_markup=reply.get_keyboard(
                             btns+["назад", "отмена"],
                             placeholder="Выбирете какое направление вам нравиться:",
                             sizes=(*[1]*len(dt), 2)
                         ))

    await state.set_state(viewer.napravlenie)

@root_1.message(StateFilter("*"), F.text == "Вернуться в меню")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    await message.answer("Выберите действие", reply_markup=reply.menu_kb)

@root_1.message(StateFilter("*"), F.text == "Покажи мне направления")
async def handle_message(message: types.Message, state: FSMContext):
    await message.answer("На какой факультет хочешь поступить?",
                         reply_markup=reply.get_keyboard(
                             facultets,
                             placeholder="На какой факультет хочешь поступить?",
                             sizes=(*[1]*11, 2)
                         ))
    await state.set_state(viewer.facultet)


@root_1.message(viewer.napravlenie, F.text)
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    facultet = data['facultet']
    await state.update_data(napravlenie=message.text)
    btns = list()
    query = await get_program_by_naprav(message.text, facultet)
    huh = await preccesing(session, query)
    print(f"[INFO] {huh}")
    for prog in huh:
        btns.append(prog.name)
    await message.answer("Выбирете какая программа вам нравиться:",
                        reply_markup=reply.get_keyboard(
                             btns+["назад", "отмена"],
                             placeholder="Выбирете какая программа вам нравиться:",
                             sizes=(*[1]*len(btns), 2)
                         ))
    await state.set_state(viewer.name)


@root_1.message(viewer.name, F.text)
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    facultet = data['facultet']
    napr = data['napravlenie']
    await state.update_data(name=message.text)

    strs = ""
    balls = ""
    query = await get_ege_by_name(message.text, napr, facultet)
    huh = await preccesing(session, query)
    print(f"[INFO] {huh[0]}")
    for value, key in zip(huh[0]._data, huh[0]._fields):
        if isinstance(value, bool):
            if value == True:
                strs += f"{subjects[key][0]} - {subjects[key][1]} (обязательно)\n"
            elif value == False:
                strs += f"{subjects[key][0]} - {subjects[key][1]} (на выбор)\n"
        elif key in ("year_2021", "year_2022", "year_2023") and value != 0:
            balls += f"{years[key]} год: {value} баллов\n"

    await message.answer(f"Чтобы поступить на эту программу необходимо сдать:\n{strs}")
    await message.answer(f"Информации о местах\n"
                         f"Бюджетных мест: {huh[0].mesta_b}\n"
                         f"В том числе целевых: {huh[0].mesta_cel}\n"
                         f"Для граждан РФ: {huh[0].RF}\n"
                         f"Для иностранцев: {huh[0].nRF}")
    if len(balls) != 0:
        await message.answer(f"Прошлые проходные баллы на эту программу:\n{balls}")
    else:
        await message.answer(f"Информации о проходных баллах неизвестна")
    await message.answer("Что дальше?", reply_markup=reply.get_keyboard(
        ["назад", "Вернуться в меню"],
        placeholder="Что дальше:?",
        sizes=([2])
    ))
    await state.clear()




