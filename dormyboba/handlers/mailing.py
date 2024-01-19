from typing import cast
from datetime import datetime
from vkbottle import Keyboard, Text, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from ..config import api, state_dispenser, ALCHEMY_SESSION_KEY
from .common import KEYBOARD_START, KEYBOARD_EMPTY
from ..model.generated import Mailing, Institute, AcademicType

mailing_labeler = BotLabeler()

class MailingState(BaseStateGroup):
    PENDING_THEME = "pending_theme"
    PENDING_TEXT = "pending_text"
    PENDING_DATE = "pending_date"
    PENDING_TIME = "pending_time"

KEYBOARD_MAILING = (
    Keyboard()
    .add(Text("Задать тему рассылки", payload={"command": "mailing_theme"}))
    .row()
    .add(Text("Задать сообщение", payload={"command": "mailing_text"}))
    .row()
    .add(Text("Задать дату рассылки", payload={"command": "mailing_date"}))
    .row()
    .add(Text("Задать время рассылки", payload={"command": "mailing_time"}))
    .row()
    .add(Text("Задать фильтры", payload={"command": "mailing_filters"}))
    .row()
    .add(Text("Готово", payload={"command": "mailing_done"}))
    .row()
    .add(Text("Назад", payload={"command": "help"}))
    .get_json()
)

@mailing_labeler.message(payload={"command": "mailing"})
async def mailing(message: Message) -> None:
    CtxStorage().set(message.peer_id, {})
    await message.answer("Начат процесс создания рассылки", keyboard=KEYBOARD_MAILING)

@mailing_labeler.message(payload={"command": "mailing_theme"})
async def mailing_theme(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_THEME)
    await message.answer("Задайте тему сообщения", keyboard=KEYBOARD_EMPTY)

@mailing_labeler.message(state=MailingState.PENDING_THEME)
async def pending_theme(message: Message) -> None:
    mailing: dict = CtxStorage().get(message.peer_id)
    mailing["theme"] = message.text
    await state_dispenser.delete(message.peer_id)
    await message.answer("Тема сообщения сохранена", keyboard=KEYBOARD_MAILING)

@mailing_labeler.message(payload={"command": "mailing_text"})
async def mailing_text(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_TEXT)
    await message.answer("Задайте текст сообщения", keyboard=KEYBOARD_EMPTY)

@mailing_labeler.message(state=MailingState.PENDING_TEXT)
async def pending_text(message: Message) -> None:
    mailing: dict = CtxStorage().get(message.peer_id)
    mailing["mailing_text"] = message.text
    await state_dispenser.delete(message.peer_id)
    await message.answer("Текст сообщения сохранен", keyboard=KEYBOARD_MAILING)

@mailing_labeler.message(payload={"command": "mailing_date"})
async def mailing_date(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_DATE)
    await message.answer("Задайте дату отправки в формате 2022-12-31", keyboard=KEYBOARD_EMPTY)

@mailing_labeler.message(state=MailingState.PENDING_DATE)
async def pending_date(message: Message) -> None:
    at = None
    try:
        at = datetime.strptime(message.text, '%Y-%m-%d')
    except ValueError as ve1:
        print('ValueError 1:', ve1)
        await state_dispenser.set(message.peer_id, MailingState.PENDING_DATE)
        await message.answer("Задайте дату отправки в формате 2022-12-31", keyboard=KEYBOARD_EMPTY)
        return
    
    at = cast(datetime, at)
    mailing: dict = CtxStorage().get(message.peer_id)
    
    if not("at" in mailing):
        mailing["at"] = at
    else:
        old_at: datetime = mailing["at"]
        mailing["at"] = old_at.replace(
            year=at.year,
            month=at.month,
            day=at.day
        )
    
    await state_dispenser.delete(message.peer_id)
    await message.answer("Дата отправки сохранена", keyboard=KEYBOARD_MAILING)

@mailing_labeler.message(payload={"command": "mailing_time"})
async def mailing_time(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_TIME)
    await message.answer("Задайте время отправки в формате 23:59:59", keyboard=KEYBOARD_EMPTY)

@mailing_labeler.message(state=MailingState.PENDING_TIME)
async def pending_time(message: Message) -> None:
    at = None
    try:
        at = datetime.strptime(message.text, '%H:%M:%S')
    except ValueError as ve1:
        print('ValueError 1:', ve1)
        await state_dispenser.set(message.peer_id, MailingState.PENDING_TIME)
        await message.answer("Задайте время отправки в формате 23:59:59", keyboard=KEYBOARD_EMPTY)
        return
    
    at = cast(datetime, at)
    mailing: dict = CtxStorage().get(message.peer_id)

    if not("at" in mailing):
        mailing["at"] = at
    else:
        old_at: datetime = mailing["at"]
        mailing["at"] = old_at.replace(
            hour=at.hour,
            minute=at.minute,
            second=at.second,
        )

    await state_dispenser.delete(message.peer_id)
    await message.answer("Время отправки сохранено", keyboard=KEYBOARD_MAILING)

KEYBOARD_FILTERS = (
    Keyboard()
    .add(Text("Выбрать институт", payload={"command": "mailing_filter_institute"}))
    .row()
    .add(Text("Выбрать тип программы", payload={"command": "mailing_filter_academic_type"}))
    .row()
    .add(Text("Выбрать курс", payload={"command": "mailing_filter_course"}))
    .row()
    .add(Text("Назад", payload={"command": "mailing_filter_back"}))
    .get_json()
)

@mailing_labeler.message(payload={"command": "mailing_filters"})
async def mailing_filters(message: Message) -> None:
    await message.answer("Выберите необходимые фильтры", keyboard=KEYBOARD_FILTERS)

@mailing_labeler.message(payload={"command": "mailing_filter_back"})
async def mailing_filter_back(message: Message) -> None:
    await message.answer("Выберите параметры рассылки", keyboard=KEYBOARD_MAILING)

@mailing_labeler.message(payload={"command": "mailing_filter_institute"})
async def mailing_filter_institute(message: Message) -> None:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = select(Institute.institute_name)
    institute_names = session.execute(stmt).all()
    keyboard = Keyboard()
    for i, row in enumerate(institute_names):
        name = row[0]
        keyboard = keyboard.add(Text(name, payload={"command": "mailing_filter_institute_got"}))
        if i != (len(institute_names) - 1):
            keyboard = keyboard.row()

    await message.answer("Выберите институт", keyboard=keyboard.get_json())

@mailing_labeler.message(payload={"command": "mailing_filter_institute_got"})
async def mailing_filter_institute_got(message: Message) -> None:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = select(Institute.institute_id).where(Institute.institute_name == message.text)
    insitute_id = session.execute(stmt).first()[0]
    mailing: dict = CtxStorage().get(message.peer_id)
    mailing["institute_id"] = insitute_id
    await message.answer("Институт сохранён", keyboard=KEYBOARD_FILTERS)

@mailing_labeler.message(payload={"command": "mailing_filter_academic_type"})
async def mailing_filter_academic_type(message: Message) -> None:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = select(AcademicType.type_name)
    type_names = session.execute(stmt).all()
    keyboard = Keyboard()
    for i, row in enumerate(type_names):
        name = row[0]
        keyboard = keyboard.add(Text(name, payload={"command": "mailing_filter_academic_type_got"}))
        if i != (len(type_names) - 1):
            keyboard = keyboard.row()

    await message.answer("Выберите тип образовательной программы", keyboard=keyboard.get_json())

@mailing_labeler.message(payload={"command": "mailing_filter_academic_type_got"})
async def mailing_filter_academic_type_got(message: Message) -> None:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = select(AcademicType.type_id).where(AcademicType.type_name == message.text)
    type_id = session.execute(stmt).first()[0]
    mailing: dict = CtxStorage().get(message.peer_id)
    mailing["academic_type_id"] = type_id
    await message.answer("Сохранено", keyboard=KEYBOARD_FILTERS)

KEYBOARD_COURSE = (
    Keyboard()
    .add(Text("1", payload={"command": "mailing_filter_course_got"}))
    .row()
    .add(Text("2", payload={"command": "mailing_filter_course_got"}))
    .row()
    .add(Text("3", payload={"command": "mailing_filter_course_got"}))
    .row()
    .add(Text("4", payload={"command": "mailing_filter_course_got"}))
    .row()
    .add(Text("5", payload={"command": "mailing_filter_course_got"}))
    .get_json()
)

@mailing_labeler.message(payload={"command": "mailing_filter_course"})
async def mailing_filter_course(message: Message) -> None:
    await message.answer("Выберите курс", keyboard=KEYBOARD_COURSE)

@mailing_labeler.message(payload={"command": "mailing_filter_course_got"})
async def mailing_filter_course_got(message: Message) -> None:
    try:
        year = (datetime.now().year % 10) - int(message.text)
    except ValueError:
        await message.answer("Выберите курс", keyboard=KEYBOARD_COURSE)
        return
    else:
        mailing = CtxStorage().get(message.peer_id)
        mailing["year"] = year
        await message.answer("Сохранено", keyboard=KEYBOARD_FILTERS)

@mailing_labeler.message(payload={"command": "mailing_done"})
async def mailing_time(message: Message) -> None:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    mailing: dict = CtxStorage().get(message.peer_id)
    
    if not ("mailing_text" in mailing):
        await message.answer("Не задан текст рассылки!", keyboard=KEYBOARD_MAILING)
        return

    stmt = insert(Mailing).values(mailing)
    session.execute(stmt)
    session.commit()

    await message.answer("Рассылка успешно создана!", keyboard=KEYBOARD_START)