import yaml
from pathlib import Path
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

config = None
with open(BASE_DIR / "config.yaml", "r") as yamlfile:
    config = yaml.load(yamlfile, Loader=yaml.FullLoader)["dormyboba"]

DOMAIN = config["domain"]
VK_TOKEN = config["vk_token"]
GROUP_ID = config["group_id"]

api = API(VK_TOKEN)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()

STUB_KEY = "STUB_KEY"
