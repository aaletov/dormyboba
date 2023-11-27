import os
from vkbottle import Keyboard, Text, BotPolling, API
from vkbottle.dispatch.rules.base import CommandRule, VBMLRule
from vkbottle.bot import Bot, Message

KEYBOARD_START = (
    Keyboard()
    .add(Text("Помощь", payload={"command": "help"}))
    .row()
    .add(Text("Пригласить", payload={"command": "invite"}))
    .row()
    .add(Text("Рассылка", payload={"command": "mailing"}))
    .get_json()
)

KEYBOARD_INVITE = (
    Keyboard()
    .add(Text("Администратор", payload={"command": "inviteAdmin"}))
    .row()
    .add(Text("Пользователь", payload={"command": "inviteClient"}))
    .row()
    .add(Text("Назад", payload={"command": "start"}))
    .get_json()
)

KEYBOARD_MAILING = (
    Keyboard()
    .add(Text("Администратор", payload={"command": "inviteAdmin"}))
    .row()
    .add(Text("Пользователь", payload={"command": "inviteClient"}))
    .row()
    .add(Text("Назад", payload={"command": "start"}))
    .get_json()
)

def run_bot(token: str) -> None:
    bot = Bot(token=token)

    @bot.error_handler.register_error_handler(RuntimeError)
    async def runtime_error_handler(e: RuntimeError):
        print("возникла ошибка runtime", e)

    @bot.on.message(command="help")
    @bot.on.message(command="start")
    @bot.on.message(payload={"command": "help"})
    @bot.on.message(payload={"command": "start"})
    async def hello(message: Message) -> None:
        users_info = await bot.api.users.get(message.from_id)
        await message.answer("Привет, {}".format(users_info[0].first_name), keyboard=KEYBOARD_START)

    @bot.on.message(payload={"command": "invite"})
    async def invite(message: Message) -> None:
        await message.answer("Выберите роль нового пользователя", keyboard=KEYBOARD_INVITE)

    @bot.on.message(payload={"command": "inviteAdmin"})
    async def invite(message: Message) -> None:
        await message.answer("https://www.youtube.com/watch?v=dQw4w9WgXcQ", keyboard=KEYBOARD_START)

    @bot.on.message(payload={"command": "inviteClient"})
    async def invite(message: Message) -> None:
        await message.answer("https://www.youtube.com/watch?v=dQw4w9WgXcQ", keyboard=KEYBOARD_START)

    @bot.on.message(payload={"command": "mailing"})
    async def invite(message: Message) -> None:
        await message.answer("", keyboard=KEYBOARD_MAILING)

    bot.run_forever()


if __name__ == "__main__":
    VK_TOKEN: str = os.environ["VK_TOKEN"]

    run_bot(VK_TOKEN)
