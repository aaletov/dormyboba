import unittest
from unittest.mock import Mock, patch, AsyncMock
import pytest
from vkbottle import Keyboard, Text
from vkbottle.bot import BotLabeler
import dormyboba_api.v1api_pb2 as apiv1
from .supercommon import (
    message_default,
    ctx_storage_default,
    stub_getUserById_role_default,
    stub_getUserById_role_council_member,
)

patch("dormyboba.handlers.injection.invite_labeler", BotLabeler()).start()
import dormyboba.handlers.invite as invite

KEYBOARD_INVITE_ADMIN = (
    Keyboard()
    .add(Text("Администратор", payload={"command": "inviteAdmin"}))
    .row()
    .add(Text("Член студсовета", payload={"command": "inviteCouncilMem"}))
    .row()
    .add(Text("Студент", payload={"command": "inviteStudent"}))
    .row()
    .add(Text("Назад", payload={"command": "start"}))
    .get_json()
)

def test_keyboard_admin():
    keyboard = invite.build_keyboard_invite("admin")
    assert keyboard == KEYBOARD_INVITE_ADMIN

@pytest.mark.asyncio
async def test_invite_admin(
    message_default,
    stub_getUserById_role_default,
):
    await invite.invite(
        message_default,
        stub_getUserById_role_default,
    )
    message_default.answer.assert_called_once_with(
        "Выберите роль нового пользователя",
        keyboard=KEYBOARD_INVITE_ADMIN,
    )

KEYBOARD_INVITE_COUNCIL_MEMBER = (
    Keyboard()
    .add(Text("Член студсовета", payload={"command": "inviteCouncilMem"}))
    .row()
    .add(Text("Студент", payload={"command": "inviteStudent"}))
    .row()
    .add(Text("Назад", payload={"command": "start"}))
    .get_json()
)

def test_keyboard_council_member():
    keyboard = invite.build_keyboard_invite("council_member")
    assert keyboard == KEYBOARD_INVITE_COUNCIL_MEMBER

@pytest.mark.asyncio
async def test_invite_council_member(
    message_default,
    stub_getUserById_role_council_member,
):
    await invite.invite(
        message_default,
        stub_getUserById_role_council_member,
    )
    message_default.answer.assert_called_once_with(
        "Выберите роль нового пользователя",
        keyboard=KEYBOARD_INVITE_COUNCIL_MEMBER,
    )