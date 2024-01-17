import threading
from vkbottle import Bot, CtxStorage
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dormyboba.config import labeler, DB_URL, ALCHEMY_SESSION_KEY, api, state_dispenser
from dormyboba.handlers import common_labeler, invite_labeler, mailing_labeler, queue_labeler, defect_labeler
from dormyboba.daemon_tasks import mailing_task

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

engine = create_engine(DB_URL)
session = Session(engine)
ctx_storage = CtxStorage()
ctx_storage.set(ALCHEMY_SESSION_KEY, session)

@bot.error_handler.register_error_handler(RuntimeError)
async def runtime_error_handler(e: RuntimeError):
    print("Runtime error has occured", e)

@bot.loop_wrapper.interval(seconds=15)
async def cool_printer():
    await mailing_task()

if __name__ == "__main__":
    try:
        bot.run_forever()
    except Exception:
        session.close()
