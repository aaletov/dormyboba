from typing import Optional
import asyncio
from vkbottle import Keyboard, Text, GroupEventType
from vkbottle.bot import Message
from vkbottle_types.events import MessageAllow
import dormyboba_api.v1api_pb2 as apiv1
from .random import random_id

from .injection import (
    common_labeler,
    stub,
    api,
    state_dispenser
)

def build_keyboard_start(user_role: Optional[str]) -> str:
    keyboard = Keyboard()
    row_complete = False
    if user_role in ("admin", "council_member", "student"):
        keyboard = keyboard.add(Text("Информация о боте", payload={"command": "help"}))
        row_complete = True
    if user_role in ("admin", "council_member"):
        if row_complete:
            keyboard = keyboard.row()
            row_complete = False
        keyboard = keyboard.add(Text("Пригласить нового пользователя", payload={"command": "invite"}))
        row_complete = True
    if user_role in ("admin", "council_member", "student"):
        if row_complete:
            keyboard = keyboard.row()
            row_complete = False
        keyboard = keyboard.add(Text("Сообщить о проблеме", payload={"command": "defect"}))
        row_complete = True
    if user_role in ("admin", "council_member"):
        if row_complete:
            keyboard = keyboard.row()
            row_complete = False
        keyboard = keyboard.add(Text("Создать рассылку", payload={"command": "mailing"}))
        row_complete = True
    if user_role in ("admin", "council_member"):
        if row_complete:
            keyboard = keyboard.row()
            row_complete = False
        keyboard = keyboard.add(Text("Создать очередь", payload={"command": "queue"}))

    return keyboard.get_json()

KEYBOARD_START = (
    Keyboard()
    .add(Text("Информация о боте", payload={"command": "help"}))
    .row()
    .add(Text("Пригласить нового пользователя", payload={"command": "invite"}))
    .row()
    .add(Text("Сообщить о проблеме", payload={"command": "defect"}))
    .row()
    .add(Text("Создать рассылку", payload={"command": "mailing"}))
    .row()
    .add(Text("Создать очередь", payload={"command": "queue"}))
    .get_json()
)

KEYBOARD_REGISTER = (
    Keyboard()
    .add(Text("Зарегистрироваться", payload={"command": "register"}))
    .get_json()
)

KEYBOARD_EMPTY = Keyboard().get_json()

@common_labeler.message(command="start")
@common_labeler.message(payload={"command": "start"})
async def start(message: Message) -> None:
    res: apiv1.GetUserByIdResponse = await stub.GetUserById(
        apiv1.GetUserByIdRequest(
            user_id=message.peer_id,
        ),
    )
    role_name = None if not(res.HasField("user")) else res.user.role.role_name
    users_info = await api.users.get(message.from_id)

    state = await state_dispenser.get(message.peer_id)
    if state is not None:
        await state_dispenser.delete(message.peer_id)
    await message.answer("Привет, {}".format(users_info[0].first_name),
                        keyboard=build_keyboard_start(role_name))

INFO = """
    Привет, <username>!
    Данный бот позволит вам:
        - Получать рассылки от администрации
        - Занимать место в очередях
        - Напрямую сообщать администрации о проблемах в общежитии
    Для перехода в главное меню отправь мне команду /start
"""

@common_labeler.message(command="help")
@common_labeler.message(payload={"command": "help"})
async def help(message: Message) -> None:
    res: apiv1.GetUserByIdResponse = await stub.GetUserById(
        apiv1.GetUserByIdRequest(
            user_id=message.peer_id,
        ),
    )

    if not(res.HasField("user")):
        await message.answer(
            message="Вы не зарегистрированы! Для регистрации обратитесь к администратору"
        )
        return

    role_name = None if not(res.HasField("user")) else res.user.role.role_name
    users_info = await api.users.get(message.from_id)
    await message.answer(INFO.replace("<username>", users_info[0].first_name),
                        keyboard=build_keyboard_start(role_name))

@common_labeler.raw_event(GroupEventType.MESSAGE_ALLOW, dataclass=MessageAllow)
async def message_allow(event: MessageAllow) -> None:
    await asyncio.sleep(5)
    res: apiv1.GetUserByIdResponse = await stub.GetUserById(apiv1.GetUserByIdRequest(
        user_id=event.object.user_id,
    ))

    if res.user.is_registered:
        return

    if not(res.HasField("user")):
        raise RuntimeError("User not found in database")

    await api.messages.send(message="Добро пожаловать!",
                                user_ids=[event.object.user_id],
                                random_id=random_id(),
                                keyboard=KEYBOARD_REGISTER)
