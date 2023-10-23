import os
from vkbottle.bot import Bot, Message

def run_bot(token: str) -> None:
    bot = Bot(token=token)
    @bot.on.message(test="/hello")
    async def hello(message: Message) -> None:
        users_info = await bot.api.users.get(message.from_id)
        await message.answer("Привет, {}".format(users_info[0].first_name))

    bot.run_forever()

def main():
    VK_TOKEN: str = os.environ["VK_TOKEN"]

    run_bot(VK_TOKEN)
