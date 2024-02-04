from urllib.parse import urlencode
import re
import random
from vkbottle import Keyboard, Text, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
from sqlalchemy.orm import Session
from sqlalchemy import select, update, insert
from ..config import api, state_dispenser, DOMAIN, ALCHEMY_SESSION_KEY
from .common import KEYBOARD_START, KEYBOARD_EMPTY
from .token import Token
from ..model.generated import DormybobaUser, DormybobaRole, VerificationCode

invite_labeler = BotLabeler()

class RegisterState(BaseStateGroup):
    PENDING_CODE = "pending_code"
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

def generate_code(role_name: str) -> int:
    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    code = random.randint(1000, 9999)
    stmt = select(DormybobaRole.role_id).where(DormybobaRole.role_name == role_name)
    role_id: int = session.execute(stmt).first()[0]
    stmt = insert(VerificationCode).values(
        code=code,
        role_id=role_id,
    )
    session.execute(stmt)
    session.commit()
    return code

@invite_labeler.message(payload={"command": "inviteAdmin"})
async def invite_admin(message: Message) -> None:
    code = generate_code("admin")
    await message.answer(f"Код регистрации: {code}", keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteCouncilMem"})
async def invite_client(message: Message) -> None:
    code = generate_code("council_member")
    await message.answer(f"Код регистрации: {code}", keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteStudent"})
async def invite_client(message: Message) -> None:
    code = generate_code("student")
    await message.answer(f"Код регистрации: {code}", keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "register"})
async def register(message: Message) -> None:
    await state_dispenser.set(message.peer_id, RegisterState.PENDING_CODE)
    CtxStorage().set(message.peer_id, {})
    await message.answer("Введите проверочный код", keyboard=KEYBOARD_EMPTY)

@invite_labeler.message(state=RegisterState.PENDING_CODE)
async def pending_code(message: Message) -> None:
    try:
        session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
        match = re.fullmatch(r'\d{4}', message.text)
        if match is None:
            raise ValueError("Некорректный проверочный код")
        code = match.group()
        stmt = select(VerificationCode).where(VerificationCode.code == code)
        res = session.execute(stmt).first()
        if res is None:
            raise ValueError("Некорректный проверочный код")
        code: VerificationCode = res[0]
        user: dict = CtxStorage().get(message.peer_id)
        user["role_id"] = code.role_id
    except:
        await state_dispenser.set(message.peer_id, RegisterState.PENDING_GROUP)
        await message.answer("Введите проверочный код повторно")        

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
async def pending_group(message: Message) -> None:
    # 51 3 09 04 / 00 1 04
    match = re.fullmatch(r'(\d{2})(\d{1})(\d{2})(\d{2})/(\d{1})(\d{2})(\d{2})', message.text)
    if match is None:
        await state_dispenser.set(message.peer_id, RegisterState.PENDING_GROUP)
        await message.answer("Введите свою группу")
        return
    
    groups = match.groups()
    user: dict = CtxStorage().get(message.peer_id)

    session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
    stmt = insert(DormybobaUser).values(
        user_id=message.peer_id,
        institute_id=groups[0],
        role_id=user["role_id"],
        academic_type_id=groups[1],
        year=groups[4],
        group="".join(groups[4:7]),
    )
    session.execute(stmt)
    session.commit()

    await state_dispenser.delete(message.peer_id)
    await message.answer("Регистрация завершена", keyboard=KEYBOARD_START)
