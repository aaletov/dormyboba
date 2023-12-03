from vkbottle import Keyboard, Text, BaseStateGroup
from vkbottle.bot import Message, BotLabeler
from config import api, state_dispenser
from .common import KEYBOARD_START, KEYBOARD_EMPTY

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
    await message.answer("Начат процесс создания проблемы", keyboard=KEYBOARD_DEFECT)

KEYBOARD_DEFECT_TYPE = (
    Keyboard()
    .add(Text("Электрика", payload={"command": "defect_type_electricity"}))
    .row()
    .add(Text("Сантехника", payload={"command": "defect_type_plumb"}))
    .row()
    .add(Text("Общее", payload={"command": "defect_type_common"}))
    .row()
    .add(Text("Назад", payload={"command": "defect"}))
    .get_json()
)

@defect_labeler.message(payload={"command": "defect_type"})
async def defect_type(message: Message) -> None:
    await message.answer("Опишите тип проблемы", keyboard=KEYBOARD_DEFECT_TYPE)

@defect_labeler.message(payload={"command": "defect_type_electricity"})
async def defect_type_electricity(message: Message) -> None:
    await message.answer("Проблема связана с электрикой", keyboard=KEYBOARD_DEFECT)

@defect_labeler.message(payload={"command": "defect_type_plumb"})
async def defect_type_plumb(message: Message) -> None:
    await message.answer("Проблема связана с сантехникой", keyboard=KEYBOARD_DEFECT)

@defect_labeler.message(payload={"command": "defect_type_common"})
async def defect_type_common(message: Message) -> None:
    await message.answer("Проблема общего характера", keyboard=KEYBOARD_DEFECT)

@defect_labeler.message(payload={"command": "defect_description"})
async def defect_description(message: Message) -> None:
    await state_dispenser.set(message.peer_id, DefectState.PENDING_DESCRIPTION)
    await message.answer("Задайте описание проблемы", keyboard=KEYBOARD_EMPTY)

@defect_labeler.message(state=DefectState.PENDING_DESCRIPTION)
async def defect_description(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Описание успешно сохранено", keyboard=KEYBOARD_DEFECT)

@defect_labeler.message(payload={"command": "defect_done"})
async def defect_done(message: Message) -> None:
    await message.answer("Проблема успешно создана!", keyboard=KEYBOARD_START)


