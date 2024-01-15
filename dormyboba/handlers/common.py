from typing import cast
from vkbottle import Keyboard, Text, GroupEventType, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from vkbottle_types.events import MessageAllow
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from ..config import api, state_dispenser, ALCHEMY_SESSION_KEY
from ..model.generated import SentToken, User
from .limits import random_id
from .token import Token

common_labeler = BotLabeler()

class CommonState(BaseStateGroup):
    PENDING_REGISTER = "pending_register"

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
    # ensure unique user_ids at db level
    sent_token = session.execute(select(SentToken).where(SentToken.user_id == str(event.object.user_id))).first()[0]
    sent_token = cast(str, sent_token)
    token_obj = None
    try:
        token_obj = Token.from_str(sent_token)
    except Exception as exc:
        print(exc)
    else:
        token_obj = cast(Token, token_obj)
        
        # multi-table insert, must use role table as well
        user = User(user_id=event.object.user_id, role=0)
        session.add(user)
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
    await message.answer("Привет, {}".format(users_info[0].first_name), keyboard=KEYBOARD_START)
