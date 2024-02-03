from typing import List
from vkbottle import Keyboard, Text, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from ..config import api, state_dispenser, defect_sheet
from .common import KEYBOARD_START, KEYBOARD_EMPTY, random_id
from gspread import Cell

defect_labeler = BotLabeler()

class DefectState(BaseStateGroup):
    PENDING_DESCRIPTION = "pending_description"

KEYBOARD_DEFECT = (
    Keyboard()
    .add(Text("Тип проблемы", payload={"command": "defect_type"}))
    .row()
    .add(Text("Задать описание проблемы", payload={"command": "defect_description"}))
    .row()
    .add(Text("Готово", payload={"command": "defect_done"}))
    .row()
    .add(Text("Назад", payload={"command": "help"}))
    .get_json()
)

@defect_labeler.message(payload={"command": "defect"})
async def defect(message: Message) -> None:
    CtxStorage().set(message.peer_id, {})
    await message.answer("Начат процесс создания проблемы", keyboard=KEYBOARD_DEFECT)

KEYBOARD_DEFECT_TYPE = (
    Keyboard()
    .add(Text("Электрика", payload={
        "command": "defect_set_type",
        "type": "electricity",
    }))
    .row()
    .add(Text("Сантехника", payload={
        "command": "defect_set_type",
        "type": "plumb",
    }))
    .row()
    .add(Text("Общее", payload={
        "command": "defect_set_type",
        "type": "common",
    }))
    .row()
    .add(Text("Назад", payload={"command": "defect"}))
    .get_json()
)

@defect_labeler.message(payload={"command": "defect_type"})
async def defect_type(message: Message) -> None:
    await message.answer("Опишите тип проблемы", keyboard=KEYBOARD_DEFECT_TYPE)

@defect_labeler.message(payload_contains={"command": "defect_set_type"})
async def defect_set_type(message: Message) -> None:
    defect: dict = CtxStorage().get(message.peer_id)
    defect["type"] = message.get_payload_json()["type"]
    await message.answer("Тип проблемы сохранён", keyboard=KEYBOARD_DEFECT)

@defect_labeler.message(payload={"command": "defect_description"})
async def defect_description(message: Message) -> None:
    await state_dispenser.set(message.peer_id, DefectState.PENDING_DESCRIPTION)
    await message.answer("Задайте описание проблемы", keyboard=KEYBOARD_EMPTY)

@defect_labeler.message(state=DefectState.PENDING_DESCRIPTION)
async def defect_description(message: Message) -> None:
    defect: dict = CtxStorage().get(message.peer_id)
    defect["description"] = message.text
    await state_dispenser.delete(message.peer_id)
    await message.answer("Описание успешно сохранено", keyboard=KEYBOARD_DEFECT)

@defect_labeler.message(payload={"command": "defect_done"})
async def defect_done(message: Message) -> None:
    defect: dict = CtxStorage().get(message.peer_id)

    if not ("type" in defect):
        await message.answer("Не задано название очереди!", keyboard=KEYBOARD_DEFECT)
        return

    if not ("description" in defect):
        await message.answer("Не задано время открытия очереди!", keyboard=KEYBOARD_DEFECT)
        return

    users_info = await api.users.get(message.from_id)
    user_name = users_info[0].first_name + " " + users_info[0].last_name

    worksheet = defect_sheet.get_worksheet(0)
    column = worksheet.col_values(1)
    i = len(column) + 1
    if None in column:
        i = column.index(None) + 1
    irange: List[Cell] = worksheet.range(i, 1, i+4, 5)
    defect_id = "DD" + str(random_id())
    values = (
        defect_id,
        user_name,
        defect["type"],
        defect["description"],
        "Добавлено",
    )
    for cell, value in zip(irange, values):
        cell.value = value

    worksheet.update_cells(irange)
    await message.answer(f"Проблема успешно создана. Номер проблемы - {defect_id}", keyboard=KEYBOARD_START)


