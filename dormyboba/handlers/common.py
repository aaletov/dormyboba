from typing import cast, Optional
from vkbottle import Keyboard, Text, GroupEventType, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..config import api, ALCHEMY_SESSION_KEY
from ..model.generated import DormybobaUser, DormybobaRole

common_labeler = BotLabeler()

def build_keyboard_start(user_role: Optional[str]) -> str:
    keyboard = Keyboard()
    row_complete = False
    if user_role in (None, "admin", "council_member", "student"):
        keyboard = keyboard.add(Text("Информация о боте", payload={"command": "help"}))
        row_complete = True
    if user_role is None:
        if row_complete:
            keyboard = keyboard.row()
            row_complete = False
        keyboard = keyboard.add(Text("Зарегистрироваться", payload={"command": "register"}))
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

@common_labeler.message(command="help")
@common_labeler.message(command="start")
@common_labeler.message(payload={"command": "help"})
@common_labeler.message(payload={"command": "start"})
async def help(message: Message) -> None:
    users_info = await api.users.get(message.from_id)
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = select(DormybobaRole.role_name).join(
        DormybobaUser, DormybobaRole.role_id == DormybobaUser.role_id
    ).where(DormybobaUser.user_id == message.peer_id)
    res = session.execute(stmt).first()

    role_name = None
    if res is not None:
        role_name: str = res[0]

    await message.answer("Привет, {}".format(users_info[0].first_name),
                         keyboard=build_keyboard_start(role_name))
