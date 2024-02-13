from vkbottle import Bot, CtxStorage
import grpc
from .config import labeler, api, state_dispenser, STUB_KEY
from .handlers import common_labeler, invite_labeler, mailing_labeler, queue_labeler, defect_labeler
from .handlers.mailing import mailing_task
from .handlers.queue import queue_task
import dormyboba_api.v1api_pb2 as apiv1
import dormyboba_api.v1api_pb2_grpc as apiv1grpc

labeler.load(common_labeler)
labeler.load(invite_labeler)
labeler.load(mailing_labeler)
labeler.load(queue_labeler)
labeler.load(defect_labeler)

bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser,
)

channel = grpc.aio.insecure_channel('dormyboba_core:50051')
stub = apiv1grpc.DormybobaCoreStub(channel)
CtxStorage().set(STUB_KEY, stub)

@bot.error_handler.register_error_handler(RuntimeError)
async def runtime_error_handler(e: RuntimeError):
    print("Runtime error has occured", e)

# @bot.loop_wrapper.interval(seconds=15)
# async def daemons() -> None:

if __name__ == "__main__":
    try:
        bot.loop_wrapper.add_task(mailing_task())
        bot.loop_wrapper.add_task(queue_task())
        bot.run_forever()
    except Exception as exc:
        channel.close()
        print(exc)