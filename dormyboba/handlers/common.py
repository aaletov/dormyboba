from vkbottle import Keyboard, Text, VKApps
from vkbottle.bot import Message, BotLabeler
from config import api

common_labeler = BotLabeler()

KEYBOARD_START = (
    Keyboard()
    .add(Text("Информация о боте", payload={"command": "help"}))
    .row()
    .add(Text("Зарегистрироваться", payload={"command": "register"}))
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

KEYBOARD_EMPTY = Keyboard().get_json()

@common_labeler.message(command="help")
@common_labeler.message(command="start")
@common_labeler.message(payload={"command": "help"})
@common_labeler.message(payload={"command": "start"})
async def help(message: Message) -> None:
    users_info = await api.users.get(message.from_id)
    await message.answer("Привет, {}".format(users_info[0].first_name), keyboard=KEYBOARD_START)
