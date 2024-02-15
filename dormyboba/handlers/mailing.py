from typing import cast, Optional, Iterator, Generator, Sequence
import logging
import datetime
import time
import re
from vkbottle import Keyboard, Text, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp
import dormyboba_api.v1api_pb2 as apiv1
import dormyboba_api.v1api_pb2_grpc as apiv1grpc
from ..config import api, state_dispenser, STUB_KEY
from .common import KEYBOARD_START, KEYBOARD_EMPTY
from .random import random_id

mailing_labeler = BotLabeler()

class MailingState(BaseStateGroup):
    PENDING_THEME = "pending_theme"
    PENDING_TEXT = "pending_text"
    PENDING_DATE = "pending_date"
    PENDING_TIME = "pending_time"
    PENDING_GROUP = "pending_group"

KEYBOARD_MAILING = (
    Keyboard()
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
    .add(Text("Назад", payload={"command": "start"}))
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
    send_date = None
    try:
        send_date = datetime.datetime.strptime(message.text, '%Y-%m-%d')
    except ValueError as ve1:
        await state_dispenser.set(message.peer_id, MailingState.PENDING_DATE)
        await message.answer("Задайте дату отправки в формате 2022-12-31", keyboard=KEYBOARD_EMPTY)
        return

    send_date = cast(datetime.datetime, send_date)
    mailing: dict = CtxStorage().get(message.peer_id)
    mailing["send_date"] = send_date

    await state_dispenser.delete(message.peer_id)
    await message.answer("Дата отправки сохранена", keyboard=KEYBOARD_MAILING)

@mailing_labeler.message(payload={"command": "mailing_time"})
async def mailing_time(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_TIME)
    await message.answer("Задайте время отправки в формате 23:59:59", keyboard=KEYBOARD_EMPTY)

@mailing_labeler.message(state=MailingState.PENDING_TIME)
async def pending_time(message: Message) -> None:
    send_time = None
    try:
        send_time = time.strptime(message.text, '%H:%M:%S')
    except ValueError as ve1:
        print('ValueError 1:', ve1)
        await state_dispenser.set(message.peer_id, MailingState.PENDING_TIME)
        await message.answer("Задайте время отправки в формате 23:59:59", keyboard=KEYBOARD_EMPTY)
        return

    send_time = cast(time.struct_time, send_time)
    mailing: dict = CtxStorage().get(message.peer_id)
    mailing["send_time"] = send_time

    await state_dispenser.delete(message.peer_id)
    await message.answer("Время отправки сохранено", keyboard=KEYBOARD_MAILING)

KEYBOARD_FILTERS = (
    Keyboard()
    .add(Text("Выбрать институт", payload={"command": "mailing_filter_institute"}))
    .row()
    .add(Text("Выбрать курс", payload={"command": "mailing_filter_course"}))
    .row()
    .add(Text("Выбрать группу", payload={"command": "mailing_filter_group"}))
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
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.GetAllInstitutesResponse = await stub.GetAllInstitutes(Empty())
    institute_names = [i.institute_name for i in res.institutes]
    logging.debug(f"Got institute names {institute_names}")
    keyboard = Keyboard()
    for i, name in enumerate(institute_names):
        keyboard = keyboard.add(Text(name, payload={"command": "mailing_filter_institute_got"}))
        if i != (len(institute_names) - 1):
            keyboard = keyboard.row()

    await message.answer("Выберите институт", keyboard=keyboard.get_json())

@mailing_labeler.message(payload={"command": "mailing_filter_institute_got"})
async def mailing_filter_institute_got(message: Message) -> None:
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.GetInstituteByNameResponse = await stub.GetInstituteByName(
        apiv1.GetInstituteByNameRequest(
            institute_name=message.text,
        ),
    )

    mailing: dict = CtxStorage().get(message.peer_id)
    mailing["institute_id"] = res.institute.institute_id
    await message.answer("Институт сохранён", keyboard=KEYBOARD_FILTERS)

@mailing_labeler.message(payload={"command": "mailing_filter_academic_type"})
async def mailing_filter_academic_type(message: Message) -> None:
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.GetAllAcademicTypesResponse = await stub.GetAllAcademicTypes(Empty())
    type_names = [t.type_name for t in res.academic_types]
    keyboard = Keyboard()
    for i, name in enumerate(type_names):
        keyboard = keyboard.add(Text(name, payload={"command": "mailing_filter_academic_type_got"}))
        if i != (len(type_names) - 1):
            keyboard = keyboard.row()

    await message.answer("Выберите тип образовательной программы", keyboard=keyboard.get_json())

@mailing_labeler.message(payload={"command": "mailing_filter_academic_type_got"})
async def mailing_filter_academic_type_got(message: Message) -> None:
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.GetAcademicTypeByNameResponse = await stub.GetAcademicTypeByName(
        apiv1.GetAcademicTypeByNameRequest(
            type_name=message.text,
        ),
    )
    mailing: dict = CtxStorage().get(message.peer_id)
    mailing["academic_type_id"] = res.academic_type.type_id
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
        year = (datetime.datetime.now().year % 10) - int(message.text)
    except ValueError:
        await message.answer("Выберите курс", keyboard=KEYBOARD_COURSE)
        return
    else:
        mailing = CtxStorage().get(message.peer_id)
        mailing["year"] = year
        await message.answer("Сохранено", keyboard=KEYBOARD_FILTERS)

@mailing_labeler.message(payload={"command": "mailing_filter_group"})
async def mailing_filter_group(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_GROUP)
    await message.answer("Введите целевую академическую группу", keyboard=KEYBOARD_EMPTY)

@mailing_labeler.message(state=MailingState.PENDING_GROUP)
async def pending_group(message: Message) -> None:
    match = re.fullmatch(r'(\d{2})(\d{1})(\d{2})(\d{2})/(\d{1})(\d{2})(\d{2})', message.text)
    if match is None:
        await state_dispenser.set(message.peer_id, MailingState.PENDING_GROUP)
        await message.answer("Введите целевую академическую группу")
        return

    mailing: dict = CtxStorage().get(message.peer_id)
    if "institute_id" in mailing:
        mailing.pop("institute_id")
    if "academic_type_id" in mailing:
        mailing.pop("academic_type_id")
    if "year" in mailing:
        mailing.pop("year")
    mailing["group"] = message.text

    await state_dispenser.delete(message.peer_id)
    await message.answer("Целевая группа сохранена", keyboard=KEYBOARD_MAILING)

KEYBOARD_MAILING_CONFIRM = (
    Keyboard()
    .add(Text("Подтвердить", payload={"command": "mailing_confirm"}))
    .row()
    .add(Text("Вернуться к редактированию", payload={"command": "mailing_filter_back"}))
    .get_json()
)

@mailing_labeler.message(payload={"command": "mailing_done"})
async def mailing_done(message: Message) -> None:
    mailing: dict = CtxStorage().get(message.peer_id)

    if not("mailing_text" in mailing):
        await message.answer("Не задан текст рассылки!", keyboard=KEYBOARD_MAILING)
        return

    textat = "сейчас"

    if ("send_date" in mailing) and not("send_time" in mailing):
        await message.answer("Дата рассылки указана без времени рассылки!",
                             keyboard=KEYBOARD_MAILING)
        return

    if ("send_time" in mailing) and not("send_date" in mailing):
        mailing["send_date"] = datetime.datetime.now()

    if ("send_time" in mailing) and ("send_date" in mailing):
        send_time: time.struct_time = mailing["send_time"]

        send_date: datetime.datetime = mailing["send_date"]
        dt = send_date.replace(
            hour=send_time.tm_hour,
            minute=send_time.tm_min,
            second=send_time.tm_sec,
        )

        if dt < datetime.datetime.now():
            await message.answer("Дата и время рассылки меньше текущего времени!",
                                 keyboard=KEYBOARD_MAILING)
            return

        textat = "в" + " " + str(dt)
        timestamp = Timestamp()
        timestamp.FromDatetime(dt)
        mailing["at"] = timestamp

    await message.answer(
        f"Рассылка будет отправлена {textat}. Текст рассылки: \n\n {mailing["mailing_text"]}",
        keyboard=KEYBOARD_MAILING_CONFIRM,
    )

@mailing_labeler.message(payload={"command": "mailing_confirm"})
async def mailing_confirm(message: Message) -> None:
    mailing: dict = CtxStorage().get(message.peer_id)
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)

    if "send_time" in mailing:
        mailing.pop("send_time")
    if "send_date" in mailing:
        mailing.pop("send_date")

    logging.debug(f"Sending CreateMailingRequest: {mailing}")

    await stub.CreateMailing(apiv1.CreateMailingRequest(
        mailing=apiv1.Mailing(**mailing),
    ))

    await message.answer("Рассылка успешно создана!", keyboard=KEYBOARD_START)

async def mailing_task() -> None:
    logging.info("Executing mailing task...")
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)

    async for response in stub.MailingEvent(Empty()):
        try:
            response = cast(apiv1.MailingEventResponse, response)
            logging.debug("New MailingEvent was received")
            event = response.event
            message = ""
            if not event.mailing.theme:
                message = event.mailing.mailing_text
            else:
                message = (
                    event.mailing.theme +
                    "\n\n" +
                    event.mailing.mailing_text
                )
            user_ids = list([user.user_id for user in event.users])
            await api.messages.send(
                message=message,
                user_ids=user_ids,
                random_id=random_id()
            )
        except Exception as exc:
            logging.exception(exc)
    logging.critical("Leaving mailing_task") #tmp
