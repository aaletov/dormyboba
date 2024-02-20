import unittest
from unittest.mock import Mock, patch, AsyncMock
import pytest
import datetime
import time
from vkbottle import Keyboard, Text
from vkbottle.bot import BotLabeler
from google.protobuf.timestamp_pb2 import Timestamp
import dormyboba_api.v1api_pb2 as apiv1

from .supercommon import (
    message_default,
    ctx_storage_default,
    state_dispenser_default,
)

patch("dormyboba.handlers.injection.queue_labeler", BotLabeler()).start()
import dormyboba.handlers.queue as queue
patch("dormyboba.handlers.injection.common_labeler", BotLabeler()).start()
import dormyboba.handlers.common as common

@pytest.mark.asyncio
async def test_queue(
    message_default,
    ctx_storage_default,
):
    await queue.queue(
        message_default,
        ctx_storage_default,
    )
    ctx_storage_default.set.assert_called_once_with(message_default.peer_id, {})
    message_default.answer.assert_called_once_with(
        "Начат процесс создания очереди",
        keyboard=queue.KEYBOARD_QUEUE,
    )

@pytest.mark.asyncio
async def test_queue_title_default(
    message_default,
    state_dispenser_default,
):
    await queue.queue_title(
        message_default,
        state_dispenser_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, queue.QueueState.PENDING_TITLE,
    )
    message_default.answer.assert_called_once_with(
        "Задайте название очереди", keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_title_default(
    message_default,
    ctx_storage_default,
    state_dispenser_default,
):
    message_default.text = "TEXT"
    queue_dict = {}
    ctx_storage_default.get.return_value = queue_dict
    await queue.pending_title(
        message_default,
        ctx_storage_default,
        state_dispenser_default,
    )
    queue_dict["title"] = "TEXT"
    state_dispenser_default.delete.assert_called_once_with(
        message_default.peer_id,
    )
    message_default.answer.assert_called_once_with(
        "Название очереди сохранено", keyboard=queue.KEYBOARD_QUEUE,
    )

@pytest.mark.asyncio
async def test_queue_description_default(
    message_default,
    state_dispenser_default,
):
    await queue.queue_description(
        message_default,
        state_dispenser_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, queue.QueueState.PENDING_DESCRIPTION,
    )
    message_default.answer.assert_called_once_with(
        "Задайте описание очереди", keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_description_default(
    message_default,
    ctx_storage_default,
    state_dispenser_default,
):
    message_default.text = "TEXT"
    queue_dict = {}
    ctx_storage_default.get.return_value = queue_dict
    await queue.pending_description(
        message_default,
        ctx_storage_default,
        state_dispenser_default,
    )
    queue_dict["description"] = "TEXT"
    state_dispenser_default.delete.assert_called_once_with(
        message_default.peer_id,
    )
    message_default.answer.assert_called_once_with(
        "Описание очереди сохранено", keyboard=queue.KEYBOARD_QUEUE,
    )

@pytest.mark.asyncio
async def test_queue_open_default(
    message_default,
    state_dispenser_default,
):
    await queue.queue_open(
        message_default,
        state_dispenser_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, queue.QueueState.PENDING_OPEN,
    )
    message_default.answer.assert_called_once_with(
        "Задайте время открытия очереди в формате 23:59:59",
        keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_open_invalid(
    message_default,
    ctx_storage_default,
    state_dispenser_default,
):
    message_default.text = "111111"
    await queue.pending_open(
        message_default,
        ctx_storage_default,
        state_dispenser_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, queue.QueueState.PENDING_OPEN,
    )
    message_default.answer.assert_called_once_with(
        "Задайте время открытия очереди в формате 23:59:59", keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_open_default(
    message_default,
    ctx_storage_default,
    state_dispenser_default,
):
    message_default.text = "00:00:00"
    queue_dict = {}
    ctx_storage_default.get.return_value = queue_dict
    await queue.pending_open(
        message_default,
        ctx_storage_default,
        state_dispenser_default,
    )
    state_dispenser_default.delete.assert_called_once_with(message_default.peer_id)
    message_default.answer.assert_called_once_with(
       "Время открытия очереди сохранено", keyboard=queue.KEYBOARD_QUEUE
    )
    assert queue_dict["open"] == (
        datetime.datetime.combine(
            datetime.datetime.now().date(),
            datetime.datetime.strptime(message_default.text, '%H:%M:%S').time(),
        )
    )

@pytest.mark.asyncio
async def test_pending_close_invalid(
    message_default,
    ctx_storage_default,
    state_dispenser_default,
):
    message_default.text = "111111"
    await queue.pending_close(
        message_default,
        ctx_storage_default,
        state_dispenser_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, queue.QueueState.PENDING_CLOSE,
    )
    message_default.answer.assert_called_once_with(
        "Задайте время закрытия очереди в формате 23:59:59", keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_queue_close_default(
    message_default,
    state_dispenser_default,
):
    await queue.queue_close(
        message_default,
        state_dispenser_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, queue.QueueState.PENDING_CLOSE,
    )
    message_default.answer.assert_called_once_with(
        "Задайте время закрытия очереди",
        keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_close_default(
    message_default,
    ctx_storage_default,
    state_dispenser_default,
):
    message_default.text = "00:00:00"
    queue_dict = {}
    ctx_storage_default.get.return_value = queue_dict
    await queue.pending_close(
        message_default,
        ctx_storage_default,
        state_dispenser_default,
    )
    state_dispenser_default.delete.assert_called_once_with(message_default.peer_id)
    message_default.answer.assert_called_once_with(
       "Время закрытия очереди сохранено", keyboard=queue.KEYBOARD_QUEUE
    )
    assert queue_dict["close"] == datetime.datetime.strptime(message_default.text, '%H:%M:%S')

@pytest.fixture
def stub_CreateQueue_default():
    return Mock(
        spec=["CreateQueue"],
        CreateQueue=AsyncMock(),
    )

@pytest.mark.asyncio
async def test_queue_done_no_title(
    message_default,
    ctx_storage_default,
    stub_CreateQueue_default,
):
    queue_dict = {}
    ctx_storage_default.get.return_value = queue_dict
    await queue.queue_done(
        message_default,
        ctx_storage_default,
        stub_CreateQueue_default,
    )
    message_default.answer.assert_called_once_with(
        "Не задано название очереди!", keyboard=queue.KEYBOARD_QUEUE
    )

@pytest.mark.asyncio
async def test_queue_done_no_open(
    message_default,
    ctx_storage_default,
    stub_CreateQueue_default,
):
    queue_dict = {
        "title": "TEXT"
    }
    ctx_storage_default.get.return_value = queue_dict
    await queue.queue_done(
        message_default,
        ctx_storage_default,
        stub_CreateQueue_default,
    )
    message_default.answer.assert_called_once_with(
        "Не задано время открытия очереди!", keyboard=queue.KEYBOARD_QUEUE,
    )

@pytest.mark.asyncio
async def test_queue_done_default(
    message_default,
    ctx_storage_default,
    stub_CreateQueue_default,
):
    dt = datetime.datetime.now()
    timestamp = Timestamp()
    timestamp.FromDatetime(dt)

    queue_dict = {
        "title": "TEXT",
        "open": dt,
    }
    ctx_storage_default.get.return_value = queue_dict
    await queue.queue_done(
        message_default,
        ctx_storage_default,
        stub_CreateQueue_default,
    )
    stub_CreateQueue_default.CreateQueue.assert_called_once_with(
        apiv1.CreateQueueRequest(
            queue=apiv1.Queue(
                title="TEXT",
                open=timestamp,
            )
        )
    )
    message_default.answer.assert_called_once_with(
        "Очередь успешно создана!", keyboard=common.KEYBOARD_START,
    )
