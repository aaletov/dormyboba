from urllib.parse import urlencode
import re
import random
from vkbottle import Keyboard, Text, BaseStateGroup, CtxStorage
from vkbottle.bot import Message, BotLabeler
import dormyboba_api.v1api_pb2 as apiv1
import dormyboba_api.v1api_pb2_grpc as apiv1grpc
from ..config import api, state_dispenser, STUB_KEY
from .common import KEYBOARD_START, KEYBOARD_EMPTY, build_keyboard_start

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
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.GetUserByIdResponse = await stub.GetUserById(
        apiv1.GetUserByIdRequest(
            user_id=message.peer_id,
        ),
    )
    await message.answer("Выберите роль нового пользователя",
                         keyboard=build_keyboard_invite(res.user.role.role_name))

async def generate_code(role_name: str) -> int:
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.GenerateVerificationCodeResponse = await stub.GenerateVerificationCode(
        apiv1.GenerateVerificationCodeRequest(
            role_name=role_name,
        ),
    )
    return res.verification_code

@invite_labeler.message(payload={"command": "inviteAdmin"})
async def invite_admin(message: Message) -> None:
    code = await generate_code("admin")
    await message.answer(f"Код регистрации: {code}", keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteCouncilMem"})
async def invite_client(message: Message) -> None:
    code = await generate_code("council_member")
    await message.answer(f"Код регистрации: {code}", keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteStudent"})
async def invite_client(message: Message) -> None:
    code = await generate_code("student")
    await message.answer(f"Код регистрации: {code}", keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "register"})
async def register(message: Message) -> None:
    await state_dispenser.set(message.peer_id, RegisterState.PENDING_CODE)
    CtxStorage().set(message.peer_id, {})
    await message.answer("Введите проверочный код", keyboard=KEYBOARD_EMPTY)

@invite_labeler.message(state=RegisterState.PENDING_CODE)
async def pending_code(message: Message) -> None:
    try:
        stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)

        match = re.fullmatch(r'\d{4}', message.text)
        if match is None:
            raise ValueError("Некорректный проверочный код")
        code = match.group()

        res: apiv1.GetRoleByVerificationCodeResponse = await stub.GetRoleByVerificationCode(
            apiv1.GetRoleByVerificationCodeRequest(
                verification_code=int(code),
            ),
        )
        
        if not(res.HasField("role")):
            raise ValueError("Некорректный проверочный код")

        user: dict = CtxStorage().get(message.peer_id)
        user["role_id"] = res.role.role_id
        user["verification_code"] = int(code)
    except ValueError as exc:
        await state_dispenser.set(message.peer_id, RegisterState.PENDING_GROUP)
        await message.answer("Введите проверочный код повторно")
        return    

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
    user_dict: dict = CtxStorage().get(message.peer_id)

    user = apiv1.DormybobaUser(
        user_id=message.peer_id,
        institute=apiv1.Institute(
            institute_id=int(groups[0]),
            institute_name=None,
        ),
        role=apiv1.DormybobaRole(
            role_id=int(user_dict["role_id"]),
            role_name=None,
        ),
        academic_type=apiv1.AcademicType(
            type_id=int(groups[1]),
            type_name=None,
        ),
        year=int(groups[4]),
        group="".join(groups[4:7]),
    )
    verification_code = user_dict["verification_code"]

    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
    res: apiv1.CreateUserResponse = await stub.CreateUser(
        apiv1.CreateUserRequest(
            user=user,
            verification_code=verification_code,
        ),
    )

    await state_dispenser.delete(message.peer_id)
    await message.answer("Регистрация завершена",
                         keyboard=build_keyboard_start(res.user.role.role_name))
