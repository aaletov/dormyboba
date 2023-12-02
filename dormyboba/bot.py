from vkbottle import Bot
from config import api, state_dispenser, labeler
from handlers import common_labeler, invite_labeler, mailing_labeler, queue_labeler

labeler.load(common_labeler)
labeler.load(invite_labeler)
labeler.load(mailing_labeler)
labeler.load(queue_labeler)

bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser,
)

@bot.error_handler.register_error_handler(RuntimeError)
async def runtime_error_handler(e: RuntimeError):
    print("Runtime error has occured", e)

def run_forever() -> None:
    bot.run_forever()

if __name__ == "__main__":
    run_forever()
