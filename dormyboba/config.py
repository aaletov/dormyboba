# from typing import Any
# from dataclasses import dataclass
# import os
# import yaml
# from pathlib import Path
# from vkbottle import API, BuiltinStateDispenser
# from vkbottle.bot import BotLabeler

# # @dataclass
# # class DormybobaConfig:
# #     addr: str
# #     core_addr: str
# #     vk_token: str

# #     @staticmethod
# #     def parse(yaml_config: Any) -> 'DormybobaConfig':
# #         return DormybobaConfig(
# #             addr=yaml_config["addr"],
# #             core_addr=yaml_config["core_addr"],
# #             vk_token=yaml_config["vk_token"],
# #         )

# # def parse_config(path: str | Path) -> DormybobaConfig:
# #     with open(path, "r") as yamlfile:
# #         yaml_config = yaml.load(yamlfile, Loader=yaml.FullLoader)["dormyboba"]
# #         return DormybobaConfig.parse(yaml_config)

# # CONFIG_DIR = Path(os.getenv("CONFIG_DIR", "./config")).resolve()
# # CONFIG = parse_config(CONFIG_DIR / "config.yaml")

# # STUB_KEY = "STUB_KEY"
