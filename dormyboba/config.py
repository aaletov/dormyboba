import yaml
from pathlib import Path
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

# Build paths inside the project like this: BASE_DIR / 'subdir'.
CONFIG_PATH = Path("/").resolve() / "config"

config = None
with open(CONFIG_PATH / "config.yaml", "r") as yamlfile:
    config = yaml.load(yamlfile, Loader=yaml.FullLoader)["dormyboba"]

DOMAIN = config["domain"]
VK_TOKEN = config["vk_token"]
GROUP_ID = config["group_id"]

api = API(VK_TOKEN)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()

STUB_KEY = "STUB_KEY"
