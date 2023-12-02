import os
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

VK_TOKEN: str = os.environ["VK_TOKEN"]
FORM_APP_ID: str = os.environ["FORM_APP_ID"]
GROUP_ID: str = os.environ["GROUP_ID"]
MAILING_HASH: str = os.environ["MAILING_HASH"]
DEFECT_HASH: str = os.environ["DEFECT_HASH"]

api = API(VK_TOKEN)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()
