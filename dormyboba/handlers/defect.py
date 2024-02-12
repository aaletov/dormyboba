from typing import List
import asyncio
from vkbottle import Keyboard, Text, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
import dormyboba_api.v1api_pb2 as apiv1
import dormyboba_api.v1api_pb2_grpc as apiv1grpc
from ..config import api, state_dispenser, STUB_KEY
from .common import KEYBOARD_START, KEYBOARD_EMPTY
from .random import random_id

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
        "type": apiv1.ELECTRICITY,
    }))
    .row()
    .add(Text("Сантехника", payload={
        "command": "defect_set_type",
        "type": apiv1.PLUMB,
    }))
    .row()
    .add(Text("Общее", payload={
        "command": "defect_set_type",
        "type": apiv1.COMMON,
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
    payload: dict = message.get_payload_json()
    defect: dict = CtxStorage().get(message.peer_id)
    defect["defect_type"] = payload["type"]
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

def build_accept_keyboard(defect_id: int) -> str:
    return (
        Keyboard(inline=True)
        .add(Text("Принято", payload={
            "command": "defect_accept",
            "defect_id": defect_id,
            "status": apiv1.ACCEPTED,
        }))
        .get_json()
    )

@defect_labeler.message(payload={"command": "defect_done"})
async def defect_done(message: Message) -> None:
    defect: dict = CtxStorage().get(message.peer_id)

    if not("defect_type" in defect):
        await message.answer("Не задан тип проблемы!", keyboard=KEYBOARD_DEFECT)
        return

    if not("description" in defect):
        await message.answer("Не задано описание проблемы!", keyboard=KEYBOARD_DEFECT)
        return

    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)

    res: apiv1.CreateDefectResponse = await stub.CreateDefect(
        apiv1.CreateDefectRequest(
            defect=apiv1.Defect(user_id=message.peer_id, **defect),
        ),
    )
    defect_id = res.defect.defect_id
    res: apiv1.AssignDefectResponse = await stub.AssignDefect(
        apiv1.AssignDefectRequest(
            defect_id=defect_id,
        ),
    )
    
    await message.answer(f"Проблема успешно создана. Номер проблемы - {defect_id}",
                         keyboard=KEYBOARD_START)
    await api.messages.send(
        user_id=res.assigned_user_id,
        message=f"Создана проблема с номером {defect_id}",
        random_id=random_id(),
        keyboard=build_accept_keyboard(defect_id)
    )
    
def build_resolved_keyboard(defect_id: int) -> str:
    return (
        Keyboard(inline=True)
        .add(Text("Решено", payload={
            "command": "defect_resolved",
            "defect_id": defect_id,
            "status": apiv1.RESOLVED,
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

    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.GetDefectByIdResponse = await stub.GetDefectById(
        apiv1.GetDefectByIdRequest(
            defect_id=payload["defect_id"],
        ),
    )
    defect = res.defect
    defect.defect_status = payload["status"]
    await stub.UpdateDefect(
        apiv1.UpdateDefectRequest(
            defect=defect,
        ),
    )

    await asyncio.gather(
        message.answer(message="Статус проблемы изменен на \"Принято\"",
                       keyboard=build_resolved_keyboard(payload["defect_id"])),
        notify_effective_user(defect.user_id, payload["defect_id"], "Принято")
    )


@defect_labeler.message(payload_contains={"command": "defect_resolved"})
async def defect_resolved(message: Message) -> None:
    payload = message.get_payload_json()

    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.GetDefectByIdResponse = await stub.GetDefectById(
        apiv1.GetDefectByIdRequest(
            defect_id=payload["defect_id"],
        ),
    )
    defect = res.defect
    defect.defect_status = payload["status"]
    await stub.UpdateDefect(
        apiv1.UpdateDefectRequest(
            defect=defect,
        ),
    )

    await asyncio.gather(
        message.answer(message="Статус проблемы изменен на \"Решено\""),
        notify_effective_user(defect.user_id, payload["defect_id"], "Решено")
    )

