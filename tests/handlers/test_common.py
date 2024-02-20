import unittest
from unittest.mock import Mock, patch, AsyncMock
import pytest
from vkbottle import Keyboard, Text
from vkbottle.bot import BotLabeler
import dormyboba_api.v1api_pb2 as apiv1
from .supercommon import (
    message_default,
    stub_getUserById_role_default,
    state_dispenser_default,
)

patch("dormyboba.handlers.injection.common_labeler", BotLabeler()).start()
import dormyboba.handlers.common as common

@pytest.fixture
def student_start_keyboard():
    return (
        Keyboard()
        .add(Text("Информация о боте", payload={"command": "help"}))
        .row()
        .add(Text("Сообщить о проблеме", payload={"command": "defect"}))
        .get_json()
    )

def test_build_keyboard_start_student(
    student_start_keyboard
):
    role = "student"
    keyboard = common.build_keyboard_start(role)
    assert keyboard == student_start_keyboard

@pytest.fixture
def admin_start_keyboard():
    return (
        Keyboard()
        .add(Text("Информация о боте", payload={"command": "help"}))
        .row()
        .add(Text("Пригласить нового пользователя", payload={"command": "invite"}))
        .row()
        .add(Text("Сообщить о проблеме", payload={"command": "defect"}))
        .row()
        .add(Text("Создать рассылку", payload={"command": "mailing"}))
        .row()
        .add(Text("Создать очередь", payload={"command": "queue"}))
        .get_json()
    )

def test_build_keyboard_start_council_member(
    admin_start_keyboard,
):
    role = "council_member"
    keyboard = common.build_keyboard_start(role)
    assert keyboard == admin_start_keyboard


def test_build_keyboard_start_admin(
    admin_start_keyboard,
):
    role = "admin"
    keyboard = common.build_keyboard_start(role)
    assert keyboard == admin_start_keyboard

@pytest.fixture
def api_user_info_default():
    api = Mock()
    api.users.get = AsyncMock()
    api.users.get.return_value = [Mock(
        spec=["first_name"],
        first_name="John",
    )]
    return api

@pytest.mark.asyncio
async def test_start_nullifies_state(
    message_default,
    state_dispenser_default,
    api_user_info_default,
    stub_getUserById_role_default,
):
    state_dispenser_default.get.return_value = "SOME_STATE"
    await common.start(
        message_default,
        stub_getUserById_role_default,
        state_dispenser_default,
        api_user_info_default,
    )
    state_dispenser_default.delete.assert_called_once_with(message_default.peer_id)

@pytest.fixture
def state_dispenser_none():
    state_dispenser = Mock(
        spec=["get"],
        get=AsyncMock(),
    )
    state_dispenser.get.return_value = None
    return state_dispenser

@pytest.mark.asyncio
async def test_start(
    message_default,
    admin_start_keyboard,
    stub_getUserById_role_default,
    api_user_info_default,
    state_dispenser_none,
):

    await common.start(
        message_default,
        stub_getUserById_role_default,
        state_dispenser_none,
        api_user_info_default,
    )
    message_default.answer.assert_called_once_with(
        "Привет, John",
        keyboard=admin_start_keyboard,
    )
    api_user_info_default.users.get.assert_called_once_with(message_default.peer_id)

@pytest.fixture
def stub_getUserById_unregistered():
    stub = Mock()
    stub.GetUserById = AsyncMock()
    stub.GetUserById.return_value = apiv1.GetUserByIdResponse(
        user=None,
    )
    return stub

@pytest.fixture
def api_messages_send():
    return Mock(
        spec=["messages"],
        messages=Mock(
            spec=["send"],
            send=AsyncMock(),
        ),
    )

@pytest.mark.asyncio
async def test_help_unregistered(
    message_default,
    stub_getUserById_unregistered,
    api_messages_send,
):
    message_default.answer = AsyncMock()
    await common.help(
        message_default,
        stub_getUserById_unregistered,
        api_messages_send,
    )
    message_default.answer.assert_called_once_with(
        message="Вы не зарегистрированы! Для регистрации обратитесь к администратору",
    )


@pytest.fixture
def message_allow_default():
    return Mock(
        spec=["object"],
        object=Mock(
            spec=["user_id"],
            user_id=123456,
        )
    )

@pytest.mark.asyncio
async def test_message_allow_unregistered(
    message_allow_default,
    stub_getUserById_unregistered,
    api_messages_send,
):
    tc = unittest.TestCase()
    with tc.assertRaises(RuntimeError, msg="User not found in database"):
        await common.message_allow(
            message_allow_default,
            stub_getUserById_unregistered,
            api_messages_send,
        )



