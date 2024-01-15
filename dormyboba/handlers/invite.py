from vkbottle import Keyboard, Text, BaseStateGroup
from vkbottle.bot import Message, BotLabeler
from ..config import api, state_dispenser
from .common import KEYBOARD_START, KEYBOARD_EMPTY, CommonState

invite_labeler = BotLabeler()

class RegisterState(BaseStateGroup):
    PENDING_NAME = "pending_name"
    PENDING_GROUP = "pending_group"

KEYBOARD_INVITE = (
    Keyboard()
    .add(Text("Администратор", payload={"command": "inviteAdmin"}))
    .row()
    .add(Text("Пользователь", payload={"command": "inviteClient"}))
    .row()
    .add(Text("Назад", payload={"command": "start"}))
    .get_json()
)

@invite_labeler.message(payload={"command": "invite"})
async def invite(message: Message) -> None:
    await message.answer("Выберите роль нового пользователя", keyboard=KEYBOARD_INVITE)

@invite_labeler.message(payload={"command": "inviteAdmin"})
async def invite_admin(message: Message) -> None:
    await message.answer("https://www.youtube.com/watch?v=dQw4w9WgXcQ", keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "inviteClient"})
async def invite_client(message: Message) -> None:
    await message.answer("https://www.youtube.com/watch?v=dQw4w9WgXcQ", keyboard=KEYBOARD_START)

@invite_labeler.message(payload={"command": "register"})
async def register(message: Message) -> None:
    await state_dispenser.set(message.peer_id, RegisterState.PENDING_NAME)
    await message.answer("Введите своё имя", keyboard=KEYBOARD_EMPTY)

@invite_labeler.message(state=RegisterState.PENDING_NAME)
async def pending_name(message: Message) -> None:
    await state_dispenser.set(message.peer_id, RegisterState.PENDING_GROUP)
    await message.answer("Введите свою группу")

@invite_labeler.message(state=RegisterState.PENDING_GROUP)
async def pending_name(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Регистрация завершена", keyboard=KEYBOARD_START)
