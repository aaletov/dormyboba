import os
from pathlib import Path
import json
from dependency_injector import containers, providers
from vkbottle import API, BuiltinStateDispenser, CtxStorage
from vkbottle.bot import BotLabeler
import grpc
import dormyboba_api.v1api_pb2_grpc as apiv1grpc

CONFIG_DIR = Path(os.getenv("CONFIG_DIR", default="")).resolve()

GRPC_CONFIG = json.dumps(
    {
        "methodConfig": [
            {
                "name": [{}],
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": "1.0s",
                    "maxBackoff": "30s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": ["UNAVAILABLE"],
                },
            },
        ],
    }
)

class Container(containers.DeclarativeContainer):

    config = providers.Configuration(yaml_files=[CONFIG_DIR / "config.yaml"])

    api = providers.Singleton(
        API,
        config.dormyboba.vk_token,
    )

    common_labeler = providers.Singleton(
        BotLabeler,
    )

    invite_labeler = providers.Singleton(
        BotLabeler,
    )

    mailing_labeler = providers.Singleton(
        BotLabeler,
    )

    queue_labeler = providers.Singleton(
        BotLabeler,
    )

    defect_labeler = providers.Singleton(
        BotLabeler,
    )

    state_dispenser = providers.Singleton(
        BuiltinStateDispenser,
    )

    channel = providers.Singleton(
        grpc.aio.insecure_channel,
        config.dormyboba.core_addr,
        options=[("grpc.service_config", GRPC_CONFIG)]
    )

    dormyboba_core_stub = providers.Singleton(
        apiv1grpc.DormybobaCoreStub,
        channel,
    )

    ctx_storage = providers.Singleton(
        CtxStorage,
    )
