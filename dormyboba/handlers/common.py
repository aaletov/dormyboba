from typing import cast
from vkbottle import Keyboard, Text, GroupEventType, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from vkbottle_types.events import MessageAllow
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from ..config import api, state_dispenser, ALCHEMY_SESSION_KEY
from ..model.generated import SentToken, DormybobaUser, DormybobaRole
from .random import random_id
from .token import Token

common_labeler = BotLabeler()

class CommonState(BaseStateGroup):
    PENDING_REGISTER = "pending_register"

def build_keyboard_start(user_role: str) -> str:
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

@common_labeler.raw_event(GroupEventType.MESSAGE_ALLOW, dataclass=MessageAllow)
async def message_allow(event: MessageAllow) -> None:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = select(DormybobaUser).where(DormybobaUser.user_id == event.object.user_id)
    is_registered = session.execute(stmt).first() is not None
    if is_registered:
        return
    # ensure unique user_ids at db level
    stmt = select(SentToken).where(SentToken.user_id == event.object.user_id)
    sent_token = session.execute(stmt).first()[0]
    sent_token = cast(str, sent_token)
    token_obj = None
    try:
        token_obj = Token.from_str(sent_token)
    except Exception as exc:
        print(exc)

    token_obj = cast(Token, token_obj)
    
    # multi-table insert, must use role table as well
    stmt = insert(DormybobaUser).from_select(
        ['user_id', 'role_id'],
        select(event.object.user_id, DormybobaRole.role_id).where(DormybobaRole.role_name == "student")
    )
    session.execute(stmt)
    session.commit()

    await api.messages.send(message="Добро пожаловать!",
                                user_ids=[event.object.user_id],
                                random_id=random_id(),
                                keyboard=KEYBOARD_REGISTER)

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
    role_name: str = session.execute(stmt).first()[0]
    await message.answer("Привет, {}".format(users_info[0].first_name),
                         keyboard=build_keyboard_start(role_name))
