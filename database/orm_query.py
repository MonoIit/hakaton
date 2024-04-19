from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from handlers.aditional_data import eng_subj, rus_subj

from database.models import Databaza, user_card

async def orm_create_user(session: AsyncSession, user: int):
    query = select(user_card)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([user_card(user_id=user)])
    await session.commit()

async def orm_get_user(session: AsyncSession, user: int):
    query = select(user_card).where(user_card.user_id==user)
    result = await session.execute(query)
    return result.scalar()


async def proccesing(session: AsyncSession, query):
    result = await session.execute(query)
    a = result.scalars().all()
    return a

async def preccesing(session: AsyncSession, query):
    result = await session.execute(query)
    a = result.all()
    return a

async def get_database(session: AsyncSession):
    query = select(Databaza)
    result = await session.execute(query)
    return result.scalars().all()

async def get_naprav_by_fac(facul: str):
    sel = select(Databaza).where(Databaza.facultet == facul)
    return sel

async def get_program_by_naprav(napr: str, facul: str):
    rez = await get_naprav_by_fac(facul)
    rez = rez.subquery()
    if napr.split()[-1] == '(ком.)':
        query = select(rez).where((rez.c.napravlenie == napr[:-7]) & (rez.c.mesta_b == 0))
    else:
        query = select(rez).where((rez.c.napravlenie == napr) & (rez.c.mesta_b != 0))
    return query

    """if napr.split()[-1] == '(ком.)':
        query = select(Databaza).where((Databaza.napravlenie == napr[:-7]) & (Databaza.facultet == facul) & (Databaza.mesta_b == 0))
    else:
        query = select(Databaza).where((Databaza.napravlenie == napr) & (Databaza.facultet == facul))
    result = await session.execute(query)
    return result.scalars().all()"""


async def get_ege_by_name(name: str, napr: str, facul: str):
    rez = await get_program_by_naprav(napr, facul)
    rez = rez.subquery()
    query = select(rez).where((rez.c.name == name))
    return query

async def delete_user(session, id: int) -> None:
    stmt = delete(user_card).where(user_card.user_id == id)
    await session.execute(stmt)
    await session.commit()

async def save_data(session, data: list) -> None:
    stmt = delete(user_card).where(user_card.user_id == data[0])
    await session.execute(stmt)
    stmt = insert(user_card).values(user_id = data[0])
    await session.execute(stmt)
    id = data[0]
    fac_1 = data[1]
    fac_2 = data[2]
    fac_3 = data[3]
    stmt = update(user_card).where(user_card.user_id == id).values(facultet_1=fac_1,
                                                                    facultet_2=fac_2,
                                                                    facultet_3=fac_3)
    await session.execute(stmt)
    for sub in data:
        if isinstance(sub, list):
            stmet = update(user_card).where(user_card.user_id == id).values(**{sub[0]: sub[1]})
            await session.execute(stmet)
    await session.commit()

