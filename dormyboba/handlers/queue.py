from typing import cast, Optional, Iterator
import logging
from datetime import datetime
import asyncio
from vkbottle import Keyboard, Text, VKApps, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.empty_pb2 import Empty
import dormyboba_api.v1api_pb2 as apiv1
import dormyboba_api.v1api_pb2_grpc as apiv1grpc
from ..config import api, state_dispenser, STUB_KEY
from .common import KEYBOARD_START, KEYBOARD_EMPTY
from .random import random_id

queue_labeler = BotLabeler()

class QueueState(BaseStateGroup):
    PENDING_TITLE = "pending_title"
    PENDING_DESCRIPTION = "pending_description"
    PENDING_OPEN = "pending_open"
    PENDING_CLOSE = "pending_close"

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
    
@queue_labeler.message(payload={"command": "queue"})
async def queue(message: Message) -> None:
    CtxStorage().set(message.peer_id, {})
    await message.answer("Начат процесс создания очереди", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(payload={"command": "queue_title"})
async def queue_title(message: Message) -> None:
    await state_dispenser.set(message.peer_id, QueueState.PENDING_TITLE)
    await message.answer("Задайте название очереди", keyboard=KEYBOARD_EMPTY)

@queue_labeler.message(state=QueueState.PENDING_TITLE)
async def pending_title(message: Message) -> None:
    queue: dict = CtxStorage().get(message.peer_id)
    queue["title"] = message.text
    await state_dispenser.delete(message.peer_id)
    await message.answer("Название очереди сохранено", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(payload={"command": "queue_description"})
async def queue_description(message: Message) -> None:
    await state_dispenser.set(message.peer_id, QueueState.PENDING_DESCRIPTION)
    await message.answer("Задайте описание очереди", keyboard=KEYBOARD_EMPTY)

@queue_labeler.message(state=QueueState.PENDING_DESCRIPTION)
async def pending_description(message: Message) -> None:
    queue: dict = CtxStorage().get(message.peer_id)
    queue["description"] = message.text
    await state_dispenser.delete(message.peer_id)
    await message.answer("Описание очереди сохранено", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(payload={"command": "queue_open"})
async def queue_open(message: Message) -> None:
    await state_dispenser.set(message.peer_id, QueueState.PENDING_OPEN)
    await message.answer("Задайте время открытия очереди в формате 23:59:59",
                         keyboard=KEYBOARD_EMPTY)

@queue_labeler.message(state=QueueState.PENDING_OPEN)
async def pending_open(message: Message) -> None:
    open = None
    try:
        open = datetime.strptime(message.text, '%H:%M:%S')
    except ValueError as ve1:
        print('ValueError 1:', ve1)
        await state_dispenser.set(message.peer_id, QueueState.PENDING_OPEN)
        await message.answer("Задайте время открытия очереди в формате 23:59:59",
                             keyboard=KEYBOARD_EMPTY)
        return
    
    open = cast(datetime, open)
    open = datetime.combine(datetime.now().date(), open.time())
    queue: dict = CtxStorage().get(message.peer_id)
    queue["open"] = open

    await state_dispenser.delete(message.peer_id)
    await message.answer("Время открытия очереди сохранено", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(payload={"command": "queue_close"})
async def queue_close(message: Message) -> None:
    await state_dispenser.set(message.peer_id, QueueState.PENDING_CLOSE)
    await message.answer("Задайте время закрытия очереди", keyboard=KEYBOARD_EMPTY)

@queue_labeler.message(state=QueueState.PENDING_CLOSE)
async def pending_close(message: Message) -> None:
    close = None
    try:
        close = datetime.strptime(message.text, '%H:%M:%S')
    except ValueError as ve1:
        print('ValueError 1:', ve1)
        await state_dispenser.set(message.peer_id, QueueState.PENDING_OPEN)
        await message.answer("Задайте время открытия очереди в формате 23:59:59",
                             keyboard=KEYBOARD_EMPTY)
        return
    
    close = close(datetime, close)
    queue: dict = CtxStorage().get(message.peer_id)
    queue["close"] = close

    await state_dispenser.delete(message.peer_id)
    await message.answer("Время закрытия очереди сохранено", keyboard=KEYBOARD_QUEUE)

@queue_labeler.message(payload={"command": "queue_done"})
async def queue_done(message: Message) -> None:
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    queue: dict = CtxStorage().get(message.peer_id)

    if not("title" in queue):
        await message.answer("Не задано название очереди!", keyboard=KEYBOARD_QUEUE)
        return

    if not("open" in queue):
        await message.answer("Не задано время открытия очереди!", keyboard=KEYBOARD_QUEUE)
        return

    queue["open"] = Timestamp().FromDatetime(queue["open"])

    if "close" in queue:
        queue["close"] = Timestamp().FromDatetime(queue["close"])


    await stub.CreateQueue(
        apiv1.CreateQueueRequest(**queue)
    )

    await message.answer("Очередь успешно создана!", keyboard=KEYBOARD_START)

def build_complete_keyboard(queue_id: int) -> str:
    return (
        Keyboard(inline=True)
        .add(Text(
            label="Я закончил",
            payload={"command": "queue_complete", "queue_id": queue_id},
        ))
        .get_json()
    )

def build_leave_keyboard(queue_id: int) -> Keyboard:
    return (
        Keyboard(inline=True)
        .add(Text(
            label="Выйти из очереди",
            payload={"command": "queue_leave", "queue_id": queue_id},
        ))
    )

@queue_labeler.message(payload_contains={"command": "queue_join"})
async def queue_join(message: Message) -> None:
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    queue_id: str = message.get_payload_json()["queue_id"]
    res: apiv1.AddPersonToQueueResponse = await stub.AddPersonToQueue(
        apiv1.AddPersonToQueueRequest(
            queue_id=queue_id,
            user_id=message.peer_id,
        ),
    )

    if res.is_active:
        await message.answer("Сейчас ваша очередь",
                             keyboard=build_complete_keyboard(queue_id))
    else:
        await message.answer("Вы успешно добавлены в очередь!",
                            keyboard=build_leave_keyboard(queue_id))
    
@queue_labeler.message(payload_contains={"command": "queue_leave"})
async def queue_leave(message: Message) -> None:
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    queue_id: str = message.get_payload_json()["queue_id"]
    await stub.RemovePersonFromQueue(
        apiv1.RemovePersonFromQueueRequest(
            queue_id=queue_id,
            user_id=message.peer_id,
        ),
    )

    await message.answer("Вы успешно вышли из очереди!")

@queue_labeler.message(payload_contains={"command": "queue_complete"})
async def queue_complete(message: Message) -> None:
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    queue_id: str = message.get_payload_json()["queue_id"]

    res: apiv1.PersonCompleteQueueResponse = await stub.PersonCompleteQueue(
        apiv1.PersonCompleteQueueRequest(
            queue_id=queue_id,
            user_id=message.peer_id,
        ),
    )

    if not res.is_queue_empty:
        await api.messages.send(
            user_id=res.active_user_id,
            message="Теперь ваша очередь!",
            random_id=random_id(),
            keyboard=build_complete_keyboard(queue_id),
        )

    await message.answer("Очередь передана следующему человеку")

def build_join_keyboard(queue_id: int) -> str:
    return (
        Keyboard(inline=True)
        .add(Text(
            label="Занять очередь",
            payload={"command": "queue_join", "queue_id": queue_id},
        ))
        .get_json()
    )

async def queue_task() -> None:
    logging.debug("Executing queue task...")
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)

    async for response in stub.QueueEvent(Empty()):
        response = cast(apiv1.QueueEventResponse, response)
        logging.debug("New QueueEvent was received")
        event = response.event

        message = (
            "Открыта очередь" +
            " " +
            f"\"{event.queue.title}\""
        )
        if event.queue.description is not None:
            message += (
                "\n\n" +
                event.queue.description
            )
        user_ids = list([user.user_id for user in event.users])
        await api.messages.send(
            message=message,
            user_ids=user_ids,
            random_id=random_id(),
            keyboard=build_join_keyboard(event.queue.queue_id),
        )
