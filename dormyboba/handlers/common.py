from vkbottle import Keyboard, Text, VKApps
from vkbottle.bot import Message, BotLabeler
from config import api, GROUP_ID, FORM_APP_ID, MAILING_HASH, DEFECT_HASH

common_labeler = BotLabeler()

KEYBOARD_START = (
    Keyboard()
    .add(Text("Помощь", payload={"command": "help"}))
    .row()
    .add(Text("Пригласить", payload={"command": "invite"}))
    .row()
    .add(Text("Сообщить о проблеме", payload={"command": "defect"}))
    .row()
    .add(Text("Рассылка", payload={"command": "mailing"}))
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
