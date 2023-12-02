import os
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

VK_TOKEN: str = os.environ["VK_TOKEN"]
GROUP_ID: str = os.environ["GROUP_ID"]

api = API(VK_TOKEN)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()
