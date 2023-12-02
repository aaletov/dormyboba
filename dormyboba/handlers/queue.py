from vkbottle import Keyboard, Text, VKApps
from vkbottle.bot import Message, BotLabeler
from config import api
from .common import KEYBOARD_START

queue_labeler = BotLabeler()

KEYBOARD_QUEUE_INLINE = (
    Keyboard(inline=True)
    .add(Text("Записаться", payload={"command": "queue_join"}))
    .get_json()
)

@queue_labeler.message(command="create_queue")
async def create_queue(message: Message) -> None:
    await message.answer("Очередь успешно создана", keyboard=KEYBOARD_QUEUE_INLINE)

@queue_labeler.message(payload={"command": "queue_join"})
async def queue_join(message: Message) -> None:
    users_info = await api.users.get(message.from_id)
    await message.answer("{} успешно добавлен в очередь".format(users_info[0].first_name),
                         keyboard=KEYBOARD_START)