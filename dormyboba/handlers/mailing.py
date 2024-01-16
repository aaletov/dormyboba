from vkbottle import Keyboard, Text, VKApps, BaseStateGroup
from vkbottle.bot import Message, BotLabeler
from ..config import api, state_dispenser
from .common import KEYBOARD_START, KEYBOARD_EMPTY

mailing_labeler = BotLabeler()

class MailingState(BaseStateGroup):
    PENDING_THEME = "pending_theme"
    PENDING_TEXT = "pending_text"
    PENDING_DATE = "pending_date"
    PENDING_TIME = "pending_time"

KEYBOARD_MAILING = (
    Keyboard()
    .add(Text("Задать тему рассылки", payload={"command": "mailing_theme"}))
    .row()
    .add(Text("Задать сообщение", payload={"command": "mailing_text"}))
    .row()
    .add(Text("Задать дату рассылки", payload={"command": "mailing_date"}))
    .row()
    .add(Text("Задать время рассылки", payload={"command": "mailing_time"}))
    .row()
    .add(Text("Готово", payload={"command": "mailing_done"}))
    .row()
    .add(Text("Назад", payload={"command": "help"}))
    .get_json()
)

@mailing_labeler.message(command="forward")
async def forward(message: Message) -> None:
    await message.answer("Сообщение успешно отправлено")

@mailing_labeler.message(command="forward_imp")
async def forward_imp(message: Message) -> None:
    await message.answer("Сообщение успешно отправлено")

@mailing_labeler.message(payload={"command": "mailing"})
async def mailing(message: Message) -> None:
    await message.answer("Начат процесс создания рассылки", keyboard=KEYBOARD_MAILING)

@mailing_labeler.message(payload={"command": "mailing_theme"})
async def mailing_theme(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_THEME)
    await message.answer("Задайте тему сообщения")

@mailing_labeler.message(state=MailingState.PENDING_THEME)
async def pending_theme(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Тема сообщения сохранена")

@mailing_labeler.message(payload={"command": "mailing_text"})
async def mailing_text(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_TEXT)
    await message.answer("Задайте текст сообщения")

@mailing_labeler.message(state=MailingState.PENDING_TEXT)
async def pending_text(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Текст сообщения сохранен")

@mailing_labeler.message(payload={"command": "mailing_date"})
async def mailing_date(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_DATE)
    await message.answer("Задайте дату отправки")

@mailing_labeler.message(state=MailingState.PENDING_DATE)
async def pending_date(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Дата отправки сохранена")

@mailing_labeler.message(payload={"command": "mailing_time"})
async def mailing_time(message: Message) -> None:
    await state_dispenser.set(message.peer_id, MailingState.PENDING_TIME)
    await message.answer("Задайте время отправки")

@mailing_labeler.message(state=MailingState.PENDING_TIME)
async def pending_time(message: Message) -> None:
    await state_dispenser.delete(message.peer_id)
    await message.answer("Время отправки сохранено")

@mailing_labeler.message(payload={"command": "mailing_done"})
async def mailing_time(message: Message) -> None:
    await message.answer("Рассылка успешно создана!", keyboard=KEYBOARD_START)