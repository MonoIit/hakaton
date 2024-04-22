from aiogram.filters import StateFilter, or_f
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import get_naprav_by_fac, get_program_by_naprav, get_ege_by_name, proccesing, preccesing, \
    get_database, save_data, orm_get_user, delete_user, orm_create_user
from handlers.aditional_data import *
from kbrd import reply, inline

root_2 = Router()

class filler(StatesGroup):

    facultet_1 = State()
    facultet_2 = State()
    facultet_3 = State()
    verifier = State()
    verifiered = False
    sub = {}
    sub_check = []
    end_sub = State()
    jobs = []
    napr = State()
    promezh = State()
    finish = State()
    chose = State()
    dont_chose = State()
    change = State()
    facultet_1_again = State()
    facultet_2_again = State()
    facultet_3_again = State()
    verifier_again = State()

    texts = {

    }

async def get_napravleniya(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    facultets_chosen = [data.get("facultet_1", False),
                        data.get("facultet_2", False),
                        data.get("facultet_3", False)]

    for i in range(len(facultets_chosen)):
        fac = facultets_chosen[i]
        if isinstance(fac, bool):
            break
        napravs = await proccesing(session, await get_naprav_by_fac(fac))
        print(f"[INFO!!!] {napravs}")
        string = set()
        for naprav in napravs:
            print(f"[INFO] {naprav}")
            print(f"[INFO] {naprav.__dict__}")
            print(f"[INFO] {naprav.napravlenie}")
            if get_recommend(naprav.napravlenie, filler.jobs):
                programes = []
                for prog in await preccesing(session, await get_program_by_naprav(naprav.napravlenie, fac)):
                    # print(f"[INFO] {prog}")
                    c_obz = 0
                    c_dop = 0
                    for key, value in zip(prog._fields, prog._data):
                        if isinstance(value, bool) and subjects[key][0] in filler.sub_check:
                            if value == True:
                                c_obz += 1
                            elif value == False:
                                c_dop += 1
                    if (c_obz >= 2 and c_dop >= 1) or (c_obz >= 3):
                        programes.append(prog.name)
                        # break
                if len(programes) != 0:
                    string.add(f"{naprav.napravlenie}\n")

        if len(string) != 0:
            st = f"{i + 1}) {fac}:\n\n"
            for strin in string:
                st += f"{strin}\n"
            await message.answer(st)
        else:
            await message.answer(f"{i + 1}) {fac}\nподходящик направлений не найдено\n")
        await message.answer("Вот список подобранных для вас направлений", reply_markup=reply.get_keyboard(
            ["Я выбрал", "Я не определился"],
            placeholder="Выбрал?",
            sizes=([2])
        ))


@root_2.message(StateFilter("*"), F.text.lower() == "загрузить данные")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    mod = await orm_get_user(session, message.from_user.id)
    print(f"[INFO_root_2] {mod}")
    if mod == None:
        await message.answer("Ваших данных ещё нет, сохраните данные")
        return
    await message.answer("Данные загружены!")
    await message.answer("Хочешь ввести профессию?", reply_markup=
                         reply.get_keyboard(["Да", "Нет"],
                                            placeholder="продолжить",
                                            sizes=([2])))

    print(f"[INFO] {mod.__dict__}")
    if mod.facultet_1 != None:
        data = [mod.__dict__.get("facultet_1", None), mod.__dict__.get("facultet_2", None), mod.__dict__.get("facultet_3", None), mod.user_id,
                ("Math", mod.Math), ("Infa", mod.Infa), ("Chemistry", mod.Chemistry),
                ("Obschestvo", mod.Obschestvo), ("Foreingh", mod.Foreingh),
                ("Physic", mod.Physic), ("Russian", mod.Russian),
                ("Geography", mod.Geography), ("History", mod.History)]
        print(f"[INFO] {data}")
        if data[0] != None:
            await state.update_data(facultet_1=data[0])
            if data[1] != None:
                await state.update_data(facultet_2=data[1])
                if data[2] != None:
                    await state.update_data(facultet_3=data[2])
        for dat in data[4:]:
            if dat[1] != None:
                filler.sub_check.append(subjects[dat[0]][0])
                filler.sub[dat[0]] = dat[1]
        if len(filler.sub_check) >= 3:
            filler.verifiered = True
            await state.set_state(filler.promezh)
        datas = await state.get_data()
        print(f"[INFO] {datas}")
        print(f"[INFO] {filler.sub_check}")
        print(f"[INFO] {filler.sub}")


@root_2.message(StateFilter("*"), F.text == "Куда поступить?")
async def handle_message(message: types.Message, state: FSMContext):
    await message.answer("Окес, Для начала тебе нужно раставить факультеты по приоритетам\n"
                         #"Ты можешь узнать о каждом факультете перейдя по соответстующей ссылке.\n"
                         "Выбери самый интересный для тебя факультет\n",
                         reply_markup=reply.get_keyboard(
                             facultets[:-2],
                             placeholder="На какой факультет тебя интересует?",
                             sizes=(*[1]*(len(facultets)-2),)
                         ))
    await state.set_state(filler.facultet_1)


@root_2.message(StateFilter(filler.facultet_1, filler.facultet_2, filler.facultet_3), F.text == "Я расставил проиритеты")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    facultets = [data.get("facultet_1", False),
                 data.get("facultet_2", False),
                 data.get("facultet_3", False)]
    print(f"[INFO] {facultets}")
    string = ""
    for i in range(1, len(facultets) + 1):
        if not isinstance(facultets[i-1], bool):
            string += f"{i}) {facultets[i-1]}\n\n"
    if string != "":
        await message.answer(f"Круто! Теперь проверь, те ли факультеты ты указал:\n\n{string}",
                             reply_markup=reply.get_keyboard(
                                 ["Да, всё верно", "Нет, я хочу поменять"],
                                 placeholder="Проверь данные",
                                 sizes=(1, 1)
                             ))
        if filler.verifiered != True:
            await state.set_state(filler.verifier)
        else:
            await state.set_state(filler.napr)
    else:
        await message.answer("Ты не выбрал ни одного приоритета!")
        await state.set_state(filler.facultet_1)

@root_2.message(filler.facultet_1, F.text)
async def handle_message(message: types.Message, state: FSMContext):
    await state.update_data(facultet_1=message.text)
    data = await state.get_data()
    facultet_1 = data["facultet_1"]
    mas = without(facultets.copy(), facultet_1)
    await message.answer("Замечательный выбор!\n"
                         "Куда ещё?",
                         reply_markup=reply.get_keyboard(
                             mas[:-2],
                             placeholder="Какой факультет тебя интересует?",
                             sizes=(*[1] * (len(mas) - 2),)
                         ))
    await state.set_state(filler.facultet_2)

@root_2.message(filler.facultet_2, F.text)
async def handle_message(message: types.Message, state: FSMContext):
    await state.update_data(facultet_2=message.text)
    data = await state.get_data()
    facultet_1 = data["facultet_1"]
    facultet_2 = data["facultet_2"]
    mas = without(facultets.copy(), facultet_1)
    mas = without(mas, facultet_2)
    await message.answer("А ты разбираешься!\n"
                         "Куда-нибудь ещё хочешь?",
                         reply_markup=reply.get_keyboard(
                             mas[:-2],
                             placeholder="Какой факультет тебя интересует?",
                             sizes=(*[1] * (len(mas) - 2),)
                         ))
    await state.set_state(filler.facultet_3)


@root_2.message(filler.facultet_3, F.text)
async def handle_message(message: types.Message, state: FSMContext):
    await state.update_data(facultet_3=message.text)
    data = await state.get_data()
    facultets = [data.get("facultet_1", False),
                 data.get("facultet_2", False),
                 data.get("facultet_3", False)]
    string = ""
    for i in range(1, len(facultets)+1):
        string += f"{i}) {facultets[i-1]}\n\n"

    await message.answer(f"Круто! Теперь проверь, те ли факультеты ты указал:\n\n{string}",
                         reply_markup=reply.get_keyboard(
                             ["Да, всё верно", "Нет, я хочу поменять"],
                             placeholder="Проверь данные",
                             sizes=(1, 1)
                         ))
    if filler.verifiered != True:
        await state.set_state(filler.verifier)
    else:
        await state.set_state(filler.napr)


@root_2.message(filler.napr, F.text == "Да, всё верно")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    if filler.verifiered:
        await message.answer("Желаете изменить ещё и професию?",
                             reply_markup=reply.get_keyboard(
                                 ["да", "нет"],
                                 placeholder="меняем професию?",
                                 sizes=([2])
                             ))
        await state.set_state(filler.promezh)
    else:
        await get_napravleniya(message, session, state)

        await state.set_state(filler.chose)


@root_2.message(filler.promezh, F.text.lower() == "нет")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await get_napravleniya(message, session, state)

    await state.set_state(filler.chose)



@root_2.message(filler.verifier, F.text == "Да, всё верно")
async def handle_message(message: types.Message, state: FSMContext):
    if not filler.verifiered:
        await message.answer("Супер, теперь нам нужно узнать какие предметы ты сдавал\n\n"
                             "Напиши предмет и укажи свои баллы\n\n"
                             "Например:\n"
                             "Математика 120")
        filler.verifiered = True
    else:
        await message.answer("Ну что ж, теперь напиши кем ты хочешь быть?\n"
                             "Например, свою будущую профессию или должность\n"
                             "Если же ты ещё не определился с будущей профессией\n"
                             "и хочешь посмотеть все доступные направления, нажми 'продолжить'",
                             reply_markup=reply.get_keyboard(
                                 ["Продолжить"],
                                 placeholder="продолжить?",
                                 sizes=([1])
                             )
                             )
        print(f"[INFO!!] {filler.sub_check}")
        print(f"[INFO!!] {filler.sub}")
        await state.set_state(filler.napr)
    await state.set_state(filler.end_sub)

@root_2.message(StateFilter(filler.verifier, filler.napr), F.text == "Нет, я хочу поменять")
async def handle_message(message: types.Message, state: FSMContext):
    await message.answer("Окей, попробуй ещё раз", reply_markup=reply.get_keyboard(
                             facultets,
                             placeholder="На какой факультет тебя интересует?",
                             sizes=(*[1]*(len(facultets)-2), 2)
                         ))
    await state.clear()
    await state.set_state(filler.facultet_1)

@root_2.message(StateFilter(filler.end_sub, filler.napr), F.text.lower() == "да")
async def handle_message(message: types.Message, state: FSMContext):
    await message.answer("И что же?")

@root_2.message(filler.end_sub, F.text.lower() == "нет")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    if len(filler.sub_check) <= 2:
        await message.answer("Увы, но для поступления в ВУЗ необходимо сдать минимум три экзамена")
        await state.clear()
        await message.answer("Мы вернулись туда, откуда начали", reply_markup=reply.start_kb)
        filler.verifiered = False
        filler.jobs.clear()
        filler.sub_check.clear()
        filler.sub.clear()
        await state.clear()
        return
    if "Русский язык" not in filler.sub_check:
        await message.answer("Вы не сможете поступить в ВУЗ, не сдав русский язык")
        await state.clear()
        await message.answer("Мы вернулись туда, откуда начали", reply_markup=reply.start_kb)
        filler.verifiered = False
        filler.jobs.clear()
        filler.sub_check.clear()
        filler.sub.clear()
        await state.clear()
        return
    await message.answer("Ну что ж, теперь напиши кем ты хочешь быть?\n"
                         "Например, свою будущую профессию или должность\n"
                         "Если же ты ещё не определился с будущей профессией\n"
                         "и хочешь посмотеть все доступные направления, нажми 'продолжить'",
                         reply_markup=reply.get_keyboard(
                             ["Продолжить"],
                             placeholder="продолжить?",
                             sizes=([1])
                         )
                         )
    print(f"[INFO!!] {filler.sub_check}")
    print(f"[INFO!!] {filler.sub}")
    await state.update_data(end_sub=message.text)
    await state.set_state(filler.napr)

@root_2.message(filler.napr, or_f(F.text.lower() == "продолжить", F.text.lower() == "нет"))
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await get_napravleniya(message, session, state)

    await state.set_state(filler.chose)


@root_2.message(filler.chose, F.text == "Я выбрал")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Рад, что смог тебе помочь\n"
                         "Выбери следующее действие", reply_markup=
                         reply.get_keyboard(
                        ["Cохранить данные и выйти",
                              "Не сохранять данные и выйти"],
                         placeholder="что дальше?",
                         sizes=(1, 1)
                        ))

    await state.set_state(filler.finish)

@root_2.message(filler.finish, F.text == "Не сохранять данные и выйти")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("До новых встреч!", reply_markup=
                         reply.get_keyboard(["Вернуться в меню"],
                                            placeholder="далее",
                                            sizes=([1]))
                         )
    filler.sub_check.clear()
    filler.sub.clear()
    filler.verifiered = False
    filler.jobs.clear()
    await delete_user(session, message.from_user.id)
    await state.clear()


@root_2.message(StateFilter("*"), F.text == "Вернуться в меню")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    filler.sub.clear()
    filler.sub_check.clear()
    filler.verifiered = False
    filler.jobs.clear()
    await message.answer("Выберите действие", reply_markup=reply.start_kb)


@root_2.message(filler.finish, F.text == "Cохранить данные и выйти")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    facults = await state.get_data()
    facults = [facults.get("facultet_1", None),
                 facults.get("facultet_2", None),
                 facults.get("facultet_3", None)]
    data = []
    data.append(message.from_user.id)
    for i in facults:
        data.append(i)
    subjs = filler.sub
    for key, value in subjs.items():
        data.append([key, value])
    await save_data(session, data)
    await session.commit()
    mod = await orm_get_user(session, message.from_user.id)
    print(f"[INFO] {mod.__dict__}")
    await message.answer("Данные сохранены, до новых встреч!", reply_markup=
                         reply.get_keyboard(["Вернуться в меню"],
                                            placeholder="далее",
                                            sizes=([1]))
                         )
    await state.clear()
    filler.sub.clear()
    filler.sub_check.clear()
    filler.verifiered = False
    filler.jobs.clear()



@root_2.message(filler.chose, F.text == "Я не определился")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Выберите следующее действие", reply_markup=
                         reply.get_keyboard(
                             ["Показать все доступные направления", "указать другие данные", "вернуться позже"],
                             placeholder="что сделать?",
                             sizes=([2])
                         ))

    await state.set_state(filler.dont_chose)




@root_2.message(filler.dont_chose, F.text == "вернуться позже")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Выбери следующее действие", reply_markup=
                         reply.get_keyboard(
                             ["Cохранить данные и выйти",
                              "Не сохранять данные и выйти"],
                             placeholder="что дальше?",
                             sizes=(1, 1)
                         ))

    await state.set_state(filler.finish)

@root_2.message(filler.dont_chose, F.text == "Показать все доступные направления")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    filler.jobs.clear()
    await get_napravleniya(message, session, state)

    await state.set_state(filler.chose)

@root_2.message(filler.dont_chose, F.text == "указать другие данные")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Что хотите изменить", reply_markup=
                         reply.get_keyboard(
                             ["Изменить приоритет", "Изменить профессию"],
                             placeholder="Что хотите изменить",
                             sizes=(1, 1)
                         ))

    await state.set_state(filler.change)

@root_2.message(filler.change, F.text == "Изменить приоритет")
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Окей, попробуй выбрать приоритет ещё раз", reply_markup=reply.get_keyboard(
        facultets,
        placeholder="На какой факультет тебя интересует?",
        sizes=(*[1] * (len(facultets) - 2), 2)
    ))
    await state.clear()
    await state.set_state(filler.facultet_1)

@root_2.message(StateFilter(filler.change, filler.promezh), or_f(F.text == "Изменить профессию", F.text.lower() == "да"))
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    filler.jobs.clear()
    await message.answer("Укажи ещё раз, кем ты хочешь быть?\n"
                         "Например, свою будущую профессию или должность\n"
                         "Если же ты ещё не определился с будущей профессией\n"
                         "и хочешь посмотеть все доступные направления, нажми 'продолжить'",
                         reply_markup=reply.get_keyboard(
                             ["Продолжить"],
                             placeholder="продолжить?",
                             sizes=([1])
                         )
                         )
    await state.set_state(filler.napr)


@root_2.message(filler.napr, F.text)
async def handle_message(message: types.Message, session: AsyncSession, state: FSMContext):
    mes = message.text.lower().strip()
    for i in mes.split():
        filler.jobs.append(i)
    print(filler.jobs)
    await message.answer("Что-нибудь ещё?", reply_markup=
                         reply.get_keyboard(
                             ["Да", "Нет"],
                             placeholder="Что-нибудь ещё?",
                             sizes=(1, 1)
                         ))

@root_2.message(filler.end_sub, F.text)
async def handle_message(message: types.Message, state: FSMContext):
    mes = message.text
    if mes == "Да, всё верно" or mes == "Нет, я хочу поменять":
        return
    ans = check_ege(mes)
    if ans == 0:
        await message.answer("Проверьте данные!")
        return
    mes = mes.lower().split()
    sub = rus_subj[mes[0][:3]]
    if ans == 0:
        await message.answer("Проверьте данные!")
    elif ans == 2:
        await message.answer("Ты задолжал быллы?")
    elif ans == 4:
        await message.answer("Фига ты крутой! А если быть честным")
    elif ans == 3:
        await message.answer("Увы, но с таким баллом к нам не поступить. Приходите через год!")
    elif ans == 1 and sub[1] not in filler.sub_check:
        filler.sub_check.append(sub[1])
        await message.answer("Супер! Ещё что-нибудь сдавал?", reply_markup=
                             reply.get_keyboard(
                                 ["да", "нет"],
                                 placeholder="что-то ещё?",
                                 sizes=([2])
                             ))
        print(f"[INFO!] {eng_subj[rus_subj[mes[0]][1]]}")
        filler.sub[eng_subj[rus_subj[mes[0]][1]]] = int(mes[-1])
    else:
        await message.answer("Вы уже вводили данные по этому предмету!")


