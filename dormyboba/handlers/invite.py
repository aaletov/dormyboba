from urllib.parse import urlencode
import re
from vkbottle import Keyboard, Text, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from ..config import api, state_dispenser, DOMAIN, ALCHEMY_SESSION_KEY
from .common import KEYBOARD_START, KEYBOARD_EMPTY, CommonState
from .token import Token
from ..model.generated import DormybobaUser, DormybobaRole

invite_labeler = BotLabeler()

class RegisterState(BaseStateGroup):
    PENDING_NAME = "pending_name"
    PENDING_GROUP = "pending_group"

def build_keyboard_invite(user_role: str) -> str:
    keyboard = Keyboard()
    row_complete = False
    if user_role in ("admin",):
        keyboard = keyboard.add(Text("Администратор", payload={"command": "inviteAdmin"}))
        row_complete = True
    if user_role in ("admin", "council_member"):
        if row_complete:
            keyboard = keyboard.row()
            row_complete = False
        keyboard = keyboard.add(Text("Член студсовета", payload={"command": "inviteCouncilMem"}))
        row_complete = True
    if user_role in ("admin", "council_member"):
        if row_complete:
            keyboard = keyboard.row()
            row_complete = False
        keyboard = keyboard.add(Text("Студент", payload={"command": "inviteStudent"}))
        row_complete= True
    if user_role in ("admin", "council_member"):
        if row_complete:
            keyboard = keyboard.row()
            row_complete = False
        keyboard = keyboard.add(Text("Назад", payload={"command": "start"}))      

    return keyboard.get_json()

@invite_labeler.message(payload={"command": "invite"})
async def invite(message: Message) -> None:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = select(DormybobaRole.role_name).join(
        DormybobaUser, DormybobaRole.role_id == DormybobaUser.role_id
    ).where(DormybobaUser.user_id == message.peer_id)
    role_name: str = session.execute(stmt).first()[0]

    await message.answer("Выберите роль нового пользователя",
                         keyboard=build_keyboard_invite(role_name))

def create_invite_link(token: Token) -> str:
    params = {"token": token.encode()}
    return f"https://{DOMAIN}/invite/widget?" + urlencode(params)

@invite_labeler.message(payload={"command": "inviteAdmin"})
async def invite_admin(message: Message) -> None:
    invite_link = create_invite_link(Token("admin").encode())
    await message.answer(invite_link, keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteCouncilMem"})
async def invite_client(message: Message) -> None:
    invite_link = create_invite_link(Token("council_member").encode())
    await message.answer(invite_link, keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteStudent"})
async def invite_client(message: Message) -> None:
    invite_link = create_invite_link(Token("student").encode())
    await message.answer(invite_link, keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "register"})
async def register(message: Message) -> None:
    await state_dispenser.set(message.peer_id, RegisterState.PENDING_NAME)
    await message.answer("Введите своё имя", keyboard=KEYBOARD_EMPTY)

@invite_labeler.message(state=RegisterState.PENDING_NAME)
async def pending_name(message: Message) -> None:
    match = re.fullmatch(r'(?u)\w+', message.text)
    if match is None:
        await state_dispenser.set(message.peer_id, RegisterState.PENDING_NAME)
        await message.answer("Введите своё имя", keyboard=KEYBOARD_EMPTY)
        return
    name = match.group()

    # There is no name field in table so we don't save it lol

    await state_dispenser.set(message.peer_id, RegisterState.PENDING_GROUP)
    await message.answer("Введите свою группу")

@invite_labeler.message(state=RegisterState.PENDING_GROUP)
async def pending_name(message: Message) -> None:
    # 51 3 09 04 / 00 1 04
    match = re.fullmatch(r'(\d{2})(\d{1})(\d{2})(\d{2})/(\d{1})(\d{2})(\d{2})', message.text)
    if match is None:
        await state_dispenser.set(message.peer_id, RegisterState.PENDING_GROUP)
        await message.answer("Введите свою группу")
        return
    
    groups = match.groups()
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = update(DormybobaUser).where(
            DormybobaUser.user_id == message.peer_id,
        ).values(
            institute_id=groups[0],
            academic_type_id=groups[1],
            year=groups[4],
            group="".join(groups[4:7]),
        )
    session.execute(stmt)
    session.commit()

    await state_dispenser.delete(message.peer_id)
    await message.answer("Регистрация завершена", keyboard=KEYBOARD_START)
