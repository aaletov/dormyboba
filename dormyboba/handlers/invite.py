from dependency_injector.wiring import inject, Provide
from urllib.parse import urlencode
import re
from vkbottle import Keyboard, Text, BaseStateGroup, BuiltinStateDispenser, CtxStorage
from vkbottle.bot import Message
import dormyboba_api.v1api_pb2 as apiv1
import dormyboba_api.v1api_pb2_grpc as apiv1grpc
from ..container import Container
from .common import KEYBOARD_START, KEYBOARD_EMPTY, build_keyboard_start

from .injection import invite_labeler

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
@inject
async def invite(
    message: Message,
    stub: apiv1grpc.DormybobaCoreStub = Provide[Container.dormyboba_core_stub]
) -> None:
    res: apiv1.GetUserByIdResponse = await stub.GetUserById(
        apiv1.GetUserByIdRequest(
            user_id=message.peer_id,
        ),
    )
    await message.answer("Выберите роль нового пользователя",
                         keyboard=build_keyboard_invite(res.user.role.role_name))

@inject
async def generate_invite_link(
    role_name: str,
    stub: apiv1grpc.DormybobaCoreStub = Provide[Container.dormyboba_core_stub],
    config = Provide[Container.config]
) -> str:
    res: apiv1.GenerateTokenResponse = await stub.GenerateToken(
        apiv1.GenerateTokenRequest(
            role_name=role_name,
        ),
    )
    params = {"token": res.token}
    addr = config["dormyboba"]["addr"]
    return f"http://{addr}/invite/widget?" + urlencode(params)

@invite_labeler.message(payload={"command": "inviteAdmin"})
async def invite_admin(message: Message) -> None:
    invite_link = await generate_invite_link("admin")
    await message.answer(invite_link, keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteCouncilMem"})
async def invite_client(message: Message) -> None:
    invite_link = await generate_invite_link("council_member")
    await message.answer(invite_link, keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteStudent"})
async def invite_client(message: Message) -> None:
    invite_link = await generate_invite_link("student")
    await message.answer(invite_link, keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "register"})
@inject
async def register(
    message: Message,
    state_dispenser: BuiltinStateDispenser = Provide[Container.state_dispenser],
    ctx_storage: CtxStorage = Provide[Container.ctx_storage],
) -> None:
    await state_dispenser.set(message.peer_id, RegisterState.PENDING_NAME)
    ctx_storage.set(message.peer_id, {})
    await message.answer("Введите своё имя", keyboard=KEYBOARD_EMPTY)

@invite_labeler.message(state=RegisterState.PENDING_NAME)
@inject
async def pending_name(
    message: Message,
    state_dispenser: BuiltinStateDispenser = Provide[Container.state_dispenser],
) -> None:
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
@inject
async def pending_group(
    message: Message,
    state_dispenser: BuiltinStateDispenser = Provide[Container.state_dispenser],
    ctx_storage: CtxStorage = Provide[Container.ctx_storage],
    stub: apiv1grpc.DormybobaCoreStub = Provide[Container.dormyboba_core_stub],
) -> None:
    # 51 3 09 04 / 00 1 04
    match = re.fullmatch(r'(\d{2})(\d{1})(\d{2})(\d{2})/(\d{1})(\d{2})(\d{2})', message.text)
    if match is None:
        await state_dispenser.set(message.peer_id, RegisterState.PENDING_GROUP)
        await message.answer("Введите свою группу")
        return

    groups = match.groups()
    user_dict: dict = ctx_storage.get(message.peer_id)

    res: apiv1.GetUserByIdResponse = await stub.GetUserById(apiv1.GetUserByIdRequest(
        user_id=message.peer_id,
    ))
    user = res.user
    user.institute.institute_id = int(groups[0])
    user.academic_type.type_id = int(groups[1])
    user.year = int(groups[4])
    user.group = message.text
    user.is_registered = True

    res: apiv1.UpdateUserResponse = await stub.UpdateUser(
        apiv1.UpdateUserRequest(
            user=user,
        ),
    )

    await state_dispenser.delete(message.peer_id)
    await message.answer("Регистрация завершена",
                         keyboard=build_keyboard_start(res.user.role.role_name))
