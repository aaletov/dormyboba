from dependency_injector.wiring import Provide
from vkbottle.bot import BotLabeler
from vkbottle import API, BuiltinStateDispenser, CtxStorage
import dormyboba_api.v1api_pb2_grpc as apiv1grpc
from ..container import Container

common_labeler: BotLabeler = Provide[Container.common_labeler]
invite_labeler: BotLabeler = Provide[Container.invite_labeler]
mailing_labeler: BotLabeler = Provide[Container.mailing_labeler]
queue_labeler: BotLabeler = Provide[Container.queue_labeler]
defect_labeler: BotLabeler = Provide[Container.defect_labeler]
