from vkbottle import Keyboard, Text, VKApps
from vkbottle.bot import Message, BotLabeler
from config import api, labeler, GROUP_ID, FORM_APP_ID, MAILING_HASH, DEFECT_HASH

handlers_labeler = BotLabeler()

KEYBOARD_START = (
    Keyboard()
    .add(Text("Помощь", payload={"command": "help"}))
    .row()
    .add(Text("Пригласить", payload={"command": "invite"}))
    .row()
    .add(VKApps(label="Сообщить о проблеме", app_id=FORM_APP_ID, owner_id=GROUP_ID, hash=DEFECT_HASH))
    .row()
    .add(VKApps(label="Рассылка", app_id=FORM_APP_ID, owner_id=GROUP_ID, hash=MAILING_HASH))
    .get_json()
)

@labeler.message(command="help")
@labeler.message(command="start")
@labeler.message(payload={"command": "help"})
@labeler.message(payload={"command": "start"})
async def help(message: Message) -> None:
    users_info = await api.users.get(message.from_id)
    await message.answer("Привет, {}".format(users_info[0].first_name), keyboard=KEYBOARD_START)

KEYBOARD_INVITE = (
    Keyboard()
    .add(Text("Администратор", payload={"command": "inviteAdmin"}))
    .row()
    .add(Text("Пользователь", payload={"command": "inviteClient"}))
    .row()
    .add(Text("Назад", payload={"command": "start"}))
    .get_json()
)

@labeler.message(payload={"command": "invite"})
async def invite(message: Message) -> None:
    await message.answer("Выберите роль нового пользователя", keyboard=KEYBOARD_INVITE)

@labeler.message(payload={"command": "inviteAdmin"})
async def invite_admin(message: Message) -> None:
    await message.answer("https://www.youtube.com/watch?v=dQw4w9WgXcQ", keyboard=KEYBOARD_START)

@labeler.message(payload={"command": "inviteClient"})
async def invite_client(message: Message) -> None:
    await message.answer("https://www.youtube.com/watch?v=dQw4w9WgXcQ", keyboard=KEYBOARD_START)

@labeler.message(command="forward")
async def forward(message: Message) -> None:
    await message.answer("Сообщение успешно отправлено")

@labeler.message(command="forward_imp")
async def forward_imp(message: Message) -> None:
    await message.answer("Сообщение успешно отправлено")

KEYBOARD_QUEUE_INLINE = (
    Keyboard(inline=True)
    .add(Text("Записаться", payload={"command": "queue_join"}))
    .get_json()
)

@labeler.message(command="create_queue")
async def create_queue(message: Message) -> None:
    await message.answer("Очередь успешно создана", keyboard=KEYBOARD_QUEUE_INLINE)

@labeler.message(payload={"command": "queue_join"})
async def queue_join(message: Message) -> None:
    users_info = await api.users.get(message.from_id)
    await message.answer("{} успешно добавлен в очередь".format(users_info[0].first_name),
                         keyboard=KEYBOARD_START)