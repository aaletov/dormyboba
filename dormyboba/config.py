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
PRIVATE_KEY = config["private_key"]

pg_config = config["postgres"]
PG_USER = pg_config["user"]
PG_PASSWORD = pg_config["password"]
PG_HOST = pg_config["host"]
PG_DB = pg_config["db"]
DB_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DB}"

api = API(VK_TOKEN)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()

ALCHEMY_SESSION_KEY = "ALCHEMY_SESSION"