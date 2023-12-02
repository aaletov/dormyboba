from vkbottle import Keyboard, Text, VKApps
from vkbottle.bot import Message, BotLabeler
from config import api

mailing_labeler = BotLabeler()

@mailing_labeler.message(command="forward")
async def forward(message: Message) -> None:
    await message.answer("Сообщение успешно отправлено")

@mailing_labeler.message(command="forward_imp")
async def forward_imp(message: Message) -> None:
    await message.answer("Сообщение успешно отправлено")
