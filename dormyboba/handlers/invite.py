from vkbottle import Keyboard, Text, VKApps
from vkbottle.bot import Message, BotLabeler
from config import api
from .common import KEYBOARD_START

invite_labeler = BotLabeler()

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
