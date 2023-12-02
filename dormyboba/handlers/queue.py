from vkbottle import Keyboard, Text, VKApps, BaseStateGroup
from vkbottle.bot import Message, BotLabeler
from config import api, state_dispenser
from .common import KEYBOARD_START

queue_labeler = BotLabeler()

class QueueState(BaseStateGroup):
    PENDING_TITLE = "pending_title"
    PENDING_DESCRIPTION = "pending_description"
    PENDING_OPEN = "pending_open"
    PENDING_CLOSE = "pending_close"

KEYBOARD_QUEUE_INLINE = (
    Keyboard(inline=True)
    .add(Text("Записаться", payload={"command": "queue_join"}))
    .get_json()
)

KEYBOARD_QUEUE = (
    Keyboard()
    .add(Text("Задать название очереди", payload={"command": "queue_title"}))
    .row()
    .add(Text("Задать описание очереди", payload={"command": "queue_description"}))
    .row()
    .add(Text("Задать время открытия очереди", payload={"command": "queue_open"}))
    .row()
    .add(Text("Задать время закрытия очереди", payload={"command": "queue_close"}))
    .row()
    .add(Text("Готово", payload={"command": "queue_done"}))
    .row()
    .add(Text("Назад", payload={"command": "help"}))
    .get_json()
)

@queue_labeler.message(command="create_queue")
async def create_queue(message: Message) -> None:
    await message.answer("Очередь успешно создана", keyboard=KEYBOARD_QUEUE_INLINE)

@queue_labeler.message(payload={"command": "queue_join"})
async def queue_join(message: Message) -> None:
    users_info = await api.users.get(message.from_id)
    await message.answer("{} успешно добавлен в очередь".format(users_info[0].first_name),
                         keyboard=KEYBOARD_START)
    
@queue_labeler.message(payload={"command": "queue"})
async def queue(message: Message) -> None:
    await message.answer("Начат процесс создания очереди", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(payload={"command": "queue_title"})
async def queue_title(message: Message) -> None:
    await state_dispenser.set(message.peer_id, QueueState.PENDING_TITLE)
    await message.answer("Задайте название очереди")

@queue_labeler.message(state=QueueState.PENDING_TITLE)
async def pending_title(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Название очереди сохранено")

@queue_labeler.message(payload={"command": "queue_description"})
async def queue_description(message: Message) -> None:
    await state_dispenser.set(message.peer_id, QueueState.PENDING_DESCRIPTION)
    await message.answer("Задайте описание очереди", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(state=QueueState.PENDING_DESCRIPTION)
async def pending_description(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Описание очереди сохранено")

@queue_labeler.message(payload={"command": "queue_open"})
async def queue_open(message: Message) -> None:
    await state_dispenser.set(message.peer_id, QueueState.PENDING_OPEN)
    await message.answer("Задайте время открытия очереди", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(state=QueueState.PENDING_OPEN)
async def pending_open(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Время открытия очереди сохранено")

@queue_labeler.message(payload={"command": "queue_close"})
async def queue_close(message: Message) -> None:
    await state_dispenser.set(message.peer_id, QueueState.PENDING_CLOSE)
    await message.answer("Задайте время закрытия очереди", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(state=QueueState.PENDING_CLOSE)
async def pending_close(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Время закрытия очереди сохранено")

@queue_labeler.message(payload={"command": "queue_done"})
async def queue_done(message: Message) -> None:
    await message.answer("Очередь успешно создана!", keyboard=KEYBOARD_START)
