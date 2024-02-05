from vkbottle import Bot, CtxStorage
import grpc
from dormyboba.config import labeler, api, state_dispenser, STUB_KEY
from dormyboba.handlers import common_labeler, invite_labeler, mailing_labeler, queue_labeler, defect_labeler
from dormyboba.daemon_tasks import mailing_task, queue_task
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

channel = grpc.insecure_channel('localhost:50051')
stub = apiv1grpc.DormybobaCoreStub(channel)
CtxStorage().set(STUB_KEY, stub)

@bot.error_handler.register_error_handler(RuntimeError)
async def runtime_error_handler(e: RuntimeError):
    print("Runtime error has occured", e)

# @bot.loop_wrapper.interval(seconds=15)
# async def cool_printer():
#     await mailing_task()

# @bot.loop_wrapper.interval(seconds=15)
# async def cool_queuer():
#     await queue_task()

if __name__ == "__main__":
    try:
        bot.run_forever()
    except Exception as exc:
        channel.close()
        print(exc)