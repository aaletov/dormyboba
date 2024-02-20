import unittest
from unittest.mock import Mock, patch, AsyncMock
import pytest
from vkbottle import Keyboard, Text
from vkbottle.bot import BotLabeler
import dormyboba_api.v1api_pb2 as apiv1
from .supercommon import message_default, ctx_storage_default

patch("dormyboba.handlers.injection.defect_labeler", BotLabeler()).start()
import dormyboba.handlers.defect as defect

@pytest.mark.asyncio
async def test_defect(
    message_default,
    ctx_storage_default,
):
    await defect.defect(
        message_default,
        ctx_storage_default,
    )
    ctx_storage_default.set.assert_called_once_with(message_default.peer_id, {})
    message_default.answer.assert_called_once_with(
        "Начат процесс создания проблемы",
        keyboard=defect.KEYBOARD_DEFECT,
    )