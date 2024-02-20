import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import pytest
import datetime
import time
from vkbottle import Keyboard, Text
from vkbottle.bot import BotLabeler
import dormyboba_api.v1api_pb2 as apiv1
from dormyboba.handlers.common import KEYBOARD_EMPTY

from .supercommon import (
    message_default,
    ctx_storage_default,
    state_dispenser_default,
)

patch("dormyboba.handlers.injection.mailing_labeler", BotLabeler()).start()
import dormyboba.handlers.mailing as mailing
patch("dormyboba.handlers.injection.common_labeler", BotLabeler()).start()
import dormyboba.handlers.common as common

@pytest.mark.asyncio
async def test_mailing(
    message_default,
    ctx_storage_default,
):
    await mailing.mailing(
        message_default,
        ctx_storage_default,
    )
    ctx_storage_default.set.assert_called_once_with(message_default.peer_id, {})
    message_default.answer.assert_called_once_with(
        "Начат процесс создания рассылки",
        keyboard=mailing.KEYBOARD_MAILING,
    )

@pytest.mark.asyncio
async def test_mailing_theme(
    message_default,
    state_dispenser_default,
):
    await mailing.mailing_theme(message_default, state_dispenser_default)
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id,
        mailing.MailingState.PENDING_THEME,
    )
    message_default.answer.assert_called_once_with(
        "Задайте тему сообщения",
        keyboard=KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_theme(
    message_default,
    state_dispenser_default,
    ctx_storage_default,
):
    message_default.text = "TEXT"
    mailing_dict = {}
    ctx_storage_default.get.return_value = mailing_dict
    await mailing.pending_theme(
        message_default,
        state_dispenser_default,
        ctx_storage_default,
    )
    state_dispenser_default.delete.assert_called_once_with(message_default.peer_id)
    message_default.answer.assert_called_once_with(
        "Тема сообщения сохранена", keyboard=mailing.KEYBOARD_MAILING,
    )
    assert mailing_dict["theme"] == "TEXT"

@pytest.mark.asyncio
async def test_mailing_text(
    message_default,
    state_dispenser_default,
):
    await mailing.mailing_text(message_default, state_dispenser_default)
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id,
        mailing.MailingState.PENDING_TEXT,
    )
    message_default.answer.assert_called_once_with(
        "Задайте текст сообщения",
        keyboard=KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_text(
    message_default,
    state_dispenser_default,
    ctx_storage_default,
):
    message_default.text = "TEXT"
    mailing_dict = {}
    ctx_storage_default.get.return_value = mailing_dict
    await mailing.pending_text(
        message_default,
        state_dispenser_default,
        ctx_storage_default,
    )
    state_dispenser_default.delete.assert_called_once_with(message_default.peer_id)
    message_default.answer.assert_called_once_with(
        "Текст сообщения сохранен", keyboard=mailing.KEYBOARD_MAILING,
    )
    assert mailing_dict["mailing_text"] == "TEXT"

@pytest.mark.asyncio
async def test_mailing_date(
    message_default,
    state_dispenser_default,
):
    await mailing.mailing_date(message_default, state_dispenser_default)
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id,
        mailing.MailingState.PENDING_DATE,
    )
    message_default.answer.assert_called_once_with(
        "Задайте дату отправки в формате 2022-12-31",
        keyboard=KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_date_invalid(
    message_default,
    state_dispenser_default,
    ctx_storage_default,
):
    message_default.text = "111111"
    await mailing.pending_date(
        message_default,
        state_dispenser_default,
        ctx_storage_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, mailing.MailingState.PENDING_DATE,
    )
    message_default.answer.assert_called_once_with(
        "Задайте дату отправки в формате 2022-12-31", keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_date(
    message_default,
    state_dispenser_default,
    ctx_storage_default,
):
    message_default.text = "2022-12-31"
    mailing_dict = {}
    ctx_storage_default.get.return_value = mailing_dict
    await mailing.pending_date(
        message_default,
        state_dispenser_default,
        ctx_storage_default,
    )
    state_dispenser_default.delete.assert_called_once_with(message_default.peer_id)
    message_default.answer.assert_called_once_with(
        "Дата отправки сохранена", keyboard=mailing.KEYBOARD_MAILING,
    )
    assert mailing_dict["send_date"] == datetime.datetime.strptime(
        message_default.text, '%Y-%m-%d',
    )

@pytest.mark.asyncio
async def test_pending_time_invalid(
    message_default,
    state_dispenser_default,
    ctx_storage_default,
):
    message_default.text = "111111"
    await mailing.pending_time(
        message_default,
        state_dispenser_default,
        ctx_storage_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, mailing.MailingState.PENDING_TIME,
    )
    message_default.answer.assert_called_once_with(
        "Задайте время отправки в формате 23:59:59", keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_mailing_time(
    message_default,
    state_dispenser_default,
):
    await mailing.mailing_time(message_default, state_dispenser_default)
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id,
        mailing.MailingState.PENDING_TIME,
    )
    message_default.answer.assert_called_once_with(
        "Задайте время отправки в формате 23:59:59",
        keyboard=KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_pending_time(
    message_default,
    state_dispenser_default,
    ctx_storage_default,
):
    message_default.text = "00:00:00"
    mailing_dict = {}
    ctx_storage_default.get.return_value = mailing_dict
    await mailing.pending_time(
        message_default,
        state_dispenser_default,
        ctx_storage_default,
    )
    state_dispenser_default.delete.assert_called_once_with(message_default.peer_id)
    message_default.answer.assert_called_once_with(
        "Время отправки сохранено", keyboard=mailing.KEYBOARD_MAILING,
    )
    assert mailing_dict["send_time"] == time.strptime(message_default.text, '%H:%M:%S')

@pytest.mark.asyncio
async def test_mailing_filters_default(
    message_default,
):
    await mailing.mailing_filters(message_default)
    message_default.answer.assert_called_once_with(
        "Выберите необходимые фильтры", keyboard=mailing.KEYBOARD_FILTERS,
    )

@pytest.mark.asyncio
async def test_mailing_filter_back_default(
    message_default,
):
    await mailing.mailing_filter_back(message_default)
    message_default.answer.assert_called_once_with(
        "Выберите параметры рассылки", keyboard=mailing.KEYBOARD_MAILING,
    )

@pytest.mark.asyncio
async def test_mailing_filter_institute_default(
    message_default,
):
    stub = Mock(
        spec=["GetAllInstitutes"],
        GetAllInstitutes=AsyncMock(),
    )
    stub.GetAllInstitutes.return_value = apiv1.GetAllInstitutesResponse(
        institutes=[apiv1.Institute(institute_name=name) for name in ["a", "b"]],
    )
    expected_keyboard = (
        Keyboard()
        .add(Text("a", payload={"command": "mailing_filter_institute_got"}))
        .row()
        .add(Text("b", payload={"command": "mailing_filter_institute_got"}))
        .get_json()
    )
    await mailing.mailing_filter_institute(message_default, stub)
    message_default.answer.assert_called_once_with(
        "Выберите институт", keyboard=expected_keyboard,
    )

@pytest.mark.asyncio
async def test_mailing_filter_institute_got_default(
    message_default,
    ctx_storage_default,
):
    message_default.text = "ИКНТ"
    mailing_dict = {}
    ctx_storage_default.get.return_value = mailing_dict
    stub = Mock(
        spec=["GetInstituteByName"],
        GetInstituteByName=AsyncMock(),
    )
    stub.GetInstituteByName.return_value = apiv1.GetInstituteByNameResponse(
        institute=apiv1.Institute(
            institute_id=1,
        ),
    )
    await mailing.mailing_filter_institute_got(
        message_default,
        ctx_storage_default,
        stub,
    )
    message_default.answer.assert_called_once_with(
        "Институт сохранён", keyboard=mailing.KEYBOARD_FILTERS,
    )
    assert mailing_dict["institute_id"] == 1

@pytest.mark.asyncio
async def test_mailing_filter_academic_type_default(
    message_default,
    ctx_storage_default,
):
    stub = Mock(
        spec=["GetAllAcademicTypes"],
        GetAllAcademicTypes=AsyncMock(),
    )
    stub.GetAllAcademicTypes.return_value = apiv1.GetAllAcademicTypesResponse(
        academic_types=[apiv1.AcademicType(type_name=name) for name in ["a", "b"]],
    )
    expected_keyboard = (
        Keyboard()
        .add(Text("a", payload={"command": "mailing_filter_academic_type_got"}))
        .row()
        .add(Text("b", payload={"command": "mailing_filter_academic_type_got"}))
        .get_json()
    )
    await mailing.mailing_filter_academic_type(
        message_default,
        ctx_storage_default,
        stub,
    )
    message_default.answer.assert_called_once_with(
        "Выберите тип образовательной программы", keyboard=expected_keyboard,
    )

@pytest.mark.asyncio
async def test_mailing_filter_academic_type_got(
    message_default,
    ctx_storage_default,
):
    mailing_dict = {}
    ctx_storage_default.get.return_value = mailing_dict
    stub = Mock(
        spec=["GetAcademicTypeByName"],
        GetAcademicTypeByName=AsyncMock(),
    )
    stub.GetAcademicTypeByName.return_value = apiv1.GetAcademicTypeByNameResponse(
        academic_type=apiv1.AcademicType(
            type_id=1,
        ),
    )
    message_default.text = "Бакалавариат"
    await mailing.mailing_filter_academic_type_got(
        message_default,
        ctx_storage_default,
        stub,
    )
    message_default.answer.assert_called_once_with(
        "Сохранено", keyboard=mailing.KEYBOARD_FILTERS,
    )
    assert mailing_dict["academic_type_id"] == 1

@pytest.mark.asyncio
async def test_mailing_filter_course_default(
    message_default,
):
    await mailing.mailing_filter_course(message_default)
    message_default.answer.assert_called_once_with(
        "Выберите курс", keyboard=mailing.KEYBOARD_COURSE,
    )

@pytest.mark.asyncio
async def test_mailing_filter_course_got_invalid(
    message_default,
    ctx_storage_default,
):
    message_default.text = "ttt"
    await mailing.mailing_filter_course_got(
        message_default,
        ctx_storage_default,
    )
    message_default.answer.assert_called_once_with(
        "Выберите курс", keyboard=mailing.KEYBOARD_COURSE,
    )

@pytest.mark.asyncio
async def test_mailing_filter_course_got_default(
    message_default,
    ctx_storage_default,
):
    message_default.text = "4"
    mailing_dict = {}
    ctx_storage_default.get.return_value = mailing_dict
    await mailing.mailing_filter_course_got(
        message_default,
        ctx_storage_default,
    )
    message_default.answer.assert_called_once_with(
        "Сохранено", keyboard=mailing.KEYBOARD_FILTERS,
    )
    assert mailing_dict["year"] == 0

@pytest.mark.asyncio
async def test_mailing_filter_group(
    message_default,
    state_dispenser_default,
):
    await mailing.mailing_filter_group(
        message_default,
        state_dispenser_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, mailing.MailingState.PENDING_GROUP,
    )
    message_default.answer.assert_called_once_with(
        "Введите целевую академическую группу", keyboard=common.KEYBOARD_EMPTY,
    )

@pytest.mark.asyncio
async def test_mailing_filter_pending_group_invalid(
    message_default,
    ctx_storage_default,
    state_dispenser_default,
):
    message_default.text = "11331122"
    await mailing.pending_group(
        message_default, ctx_storage_default, state_dispenser_default,
    )
    state_dispenser_default.set.assert_called_once_with(
        message_default.peer_id, mailing.MailingState.PENDING_GROUP,
    )
    message_default.answer.assert_called_once_with("Введите целевую академическую группу")

@pytest.mark.asyncio
async def test_mailing_filter_pending_group_default(
    message_default,
    ctx_storage_default,
    state_dispenser_default,
):
    message_default.text = "5130904/00104"
    mailing_dict = {
        "institute_id": 1,
        "academic_type_id": 1,
        "year": 1,
    }
    ctx_storage_default.get.return_value = mailing_dict

    await mailing.pending_group(
        message_default, ctx_storage_default, state_dispenser_default,
    )

    state_dispenser_default.delete.assert_called_once_with(message_default.peer_id)
    message_default.answer.assert_called_once_with(
        "Целевая группа сохранена", keyboard=mailing.KEYBOARD_MAILING,
    )

@pytest.mark.asyncio
async def test_mailing_done_no_text(
    message_default,
    ctx_storage_default,
):
    ctx_storage_default.get.return_value = {}
    await mailing.mailing_done(message_default, ctx_storage_default)
    message_default.answer.assert_called_once_with(
        "Не задан текст рассылки!", keyboard=mailing.KEYBOARD_MAILING
    )

@pytest.mark.asyncio
async def test_mailing_done_default(
    message_default,
    ctx_storage_default,
):
    ctx_storage_default.get.return_value = {
        "mailing_text": "Mailing Text",
    }
    await mailing.mailing_done(message_default, ctx_storage_default)
    message_default.answer.assert_called_once_with(
        "Рассылка будет отправлена сейчас. Текст рассылки: \n\n Mailing Text",
        keyboard=mailing.KEYBOARD_MAILING_CONFIRM,
    )

@pytest.mark.asyncio
async def test_mailing_done_date_without_time(
    message_default,
    ctx_storage_default,
):
    ctx_storage_default.get.return_value = {
        "mailing_text": "Mailing Text",
        "send_date": datetime.datetime.now(),
    }
    await mailing.mailing_done(message_default, ctx_storage_default)
    message_default.answer.assert_called_once_with(
        "Дата рассылки указана без времени рассылки!", keyboard=mailing.KEYBOARD_MAILING,
    )

@pytest.mark.asyncio
async def test_mailing_done_time_without_date(
    message_default,
    ctx_storage_default,
):
    mailing_dict = {
        "mailing_text": "Mailing Text",
        "send_time": time.strptime("23:59:59", '%H:%M:%S'),
    }
    ctx_storage_default.get.return_value = mailing_dict
    await mailing.mailing_done(message_default, ctx_storage_default)
    assert "send_date" in mailing_dict

@pytest.mark.asyncio
async def test_mailing_done_dt_less(
    message_default,
    ctx_storage_default,
):
    mailing_dict = {
        "mailing_text": "Mailing Text",
        "send_time": time.strptime("00:00:00", '%H:%M:%S'),
        "send_date": datetime.datetime.now(),
    }
    ctx_storage_default.get.return_value = mailing_dict
    await asyncio.sleep(1)
    await mailing.mailing_done(message_default, ctx_storage_default)
    message_default.answer.assert_called_once_with(
        "Дата и время рассылки меньше текущего времени!", keyboard=mailing.KEYBOARD_MAILING,
    )

@pytest.mark.asyncio
async def test_mailing_confirm_default(
    message_default,
    ctx_storage_default,
):
    mailing_dict = {
        "mailing_text": "Mailing Text",
    }
    ctx_storage_default.get.return_value = mailing_dict
    stub = Mock(
        spec=["CreateMailing"],
        CreateMailing=AsyncMock(),
    )
    await mailing.mailing_confirm(message_default, ctx_storage_default, stub)
    stub.CreateMailing.assert_called_once_with(
        apiv1.CreateMailingRequest(
            mailing=apiv1.Mailing(
                mailing_text=mailing_dict["mailing_text"],
            ),
        ),
    )
    message_default.answer.assert_called_once_with(
        "Рассылка успешно создана!", keyboard=common.KEYBOARD_START,
    )
