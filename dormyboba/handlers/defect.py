from typing import List
import asyncio
from vkbottle import Keyboard, Text, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from sqlalchemy import select
from sqlalchemy.orm import Session
from gspread import Cell
from ..config import api, state_dispenser, defect_sheet, ALCHEMY_SESSION_KEY
from .common import KEYBOARD_START, KEYBOARD_EMPTY, random_id
from ..model.generated import DormybobaUser, DormybobaRole

defect_labeler = BotLabeler()

class DefectState(BaseStateGroup):
    PENDING_DESCRIPTION = "pending_description"
    DEFECT_NOT_ASSIGNED = "defect_not_assigned"

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

    worksheet = defect_sheet.get_worksheet(0)
    column = worksheet.col_values(1)
    i = len(column) + 1
    if None in column:
        i = column.index(None) + 1
    irange: List[Cell] = worksheet.range(i, 1, i+4, 5)
    defect_id = "DD" + str(random_id())
    values = (
        defect_id,
        message.peer_id,
        defect["type"],
        defect["description"],
        "Добавлено",
    )
    for cell, value in zip(irange, values):
        cell.value = value

    worksheet.update_cells(irange)

    await asyncio.gather(
        message.answer(f"Проблема успешно создана. Номер проблемы - {defect_id}",
                       keyboard=KEYBOARD_START),
        defect_assign(defect_id),
    )

def build_accept_keyboard(defect_id: int) -> str:
    return (
        Keyboard(inline=True)
        .add(Text("Принято", payload={
            "command": "defect_accept",
            "defect_id": defect_id,
        }))
        .get_json()
    )
    
async def defect_assign(defect_id: str) -> None:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = (
        select(DormybobaUser)
        .join(DormybobaRole, DormybobaUser.role_id == DormybobaRole.role_id)
        .where(DormybobaRole.role_name == "admin")
    )
    admin_user: DormybobaUser = session.execute(stmt).first()[0]

    await api.messages.send(
        user_id=admin_user.user_id,
        message=f"Новая проблема {defect_id}",
        random_id=random_id(),
        keyboard=build_accept_keyboard(defect_id)
    )

def build_resolved_keyboard(defect_id: int) -> str:
    return (
        Keyboard(inline=True)
        .add(Text("Решено", payload={
            "command": "defect_resolved",
            "defect_id": defect_id,
        }))
        .get_json()
    )

async def notify_effective_user(effective_user_id: int, defect_id: str, status: str) -> None:
    await api.messages.send(
        user_id=effective_user_id,
        message=f"Статус проблемы {defect_id} изменен на {status}",
        random_id=random_id(),
    )

@defect_labeler.message(payload_contains={"command": "defect_accept"})
async def defect_accept(message: Message) -> None:
    payload = message.get_payload_json()

    worksheet = defect_sheet.get_worksheet(0)
    column = worksheet.col_values(1)
    i = column.index(payload["defect_id"]) + 1
    effective_user_id: int = worksheet.cell(row=i, col=2).value
    worksheet.update_cell(row=i, col=5, value="Принято")

    await asyncio.gather(
        message.answer(message="Статус проблемы изменен на \"Принято\"",
                       keyboard=build_resolved_keyboard(payload["defect_id"])),
        notify_effective_user(effective_user_id, payload["defect_id"], "Принято")
    )


@defect_labeler.message(payload_contains={"command": "defect_resolved"})
async def defect_resolved(message: Message) -> None:
    payload = message.get_payload_json()

    worksheet = defect_sheet.get_worksheet(0)
    column = worksheet.col_values(1)
    i = column.index(payload["defect_id"]) + 1
    effective_user_id: int = worksheet.cell(row=i, col=2).value
    worksheet.update_cell(row=i, col=5, value="Решено")

    await asyncio.gather(
        message.answer(message="Статус проблемы изменен на \"Решено\""),
        notify_effective_user(effective_user_id, payload["defect_id"], "Решено")
    )

