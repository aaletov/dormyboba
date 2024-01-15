from vkbottle import Bot, CtxStorage
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dormyboba import config, handlers

config.labeler.load(handlers.common_labeler)
config.labeler.load(handlers.invite_labeler)
config.labeler.load(handlers.mailing_labeler)
config.labeler.load(handlers.queue_labeler)
config.labeler.load(handlers.defect_labeler)

bot = Bot(
    api=config.api,
    labeler=config.labeler,
    state_dispenser=config.state_dispenser,
)

engine = create_engine(config.DB_URL)
session = Session(engine)
ctx_storage = CtxStorage()
ctx_storage.set(config.ALCHEMY_SESSION_KEY, session)

@bot.error_handler.register_error_handler(RuntimeError)
async def runtime_error_handler(e: RuntimeError):
    print("Runtime error has occured", e)

def run_forever() -> None:
    bot.run_forever()

if __name__ == "__main__":
    try:
        run_forever()
    except Exception:
        session.close()
