from typing import Optional
from vkbottle import Keyboard, Text, CtxStorage
from vkbottle.bot import Message, BotLabeler
import grpc
import dormyboba_api.v1api_pb2 as apiv1
import dormyboba_api.v1api_pb2_grpc as apiv1grpc
from ..config import api, STUB_KEY, state_dispenser

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
    stub: apiv1grpc.DormybobaCoreStub = CtxStorage().get(STUB_KEY)
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
