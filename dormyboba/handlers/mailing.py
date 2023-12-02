from vkbottle import Keyboard, Text, VKApps, BaseStateGroup
from vkbottle.bot import Message, BotLabeler
from config import api, state_dispenser
from .common import KEYBOARD_START, KEYBOARD_EMPTY

mailing_labeler = BotLabeler()

class MailingStates(BaseStateGroup):
    PENDING_THEME = "pending_theme"
    PENDING_TEXT = "pending_text"
    PENDING_DATE = "pending_date"
    PENDING_TIME = "pending_time"

@mailing_labeler.message(command="forward")
async def forward(message: Message) -> None:
    await message.answer("Сообщение успешно отправлено")

@mailing_labeler.message(command="forward_imp")
async def forward_imp(message: Message) -> None:
    await message.answer("Сообщение успешно отправлено")

@mailing_labeler.message(payload={"command": "mailing"})
async def mailing(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingStates.PENDING_THEME)
    await message.answer("Задайте тему сообщения", keyboard=KEYBOARD_EMPTY)

@mailing_labeler.message(state=MailingStates.PENDING_THEME)
async def pending_theme(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingStates.PENDING_TEXT)
    await message.answer("Задайте текст сообщения")

@mailing_labeler.message(state=MailingStates.PENDING_TEXT)
async def pending_text(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingStates.PENDING_DATE)
    await message.answer("Задайте дату отправки сообщения")

@mailing_labeler.message(state=MailingStates.PENDING_DATE)
async def pending_date(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingStates.PENDING_TIME)
    await message.answer("Задайте время отправки сообщения")

@mailing_labeler.message(state=MailingStates.PENDING_TIME)
async def pending_time(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Рассылка успешно создана!", keyboard=KEYBOARD_START)