from vkbottle import Bot
from vkbottle.bot import BotLabeler
from .container import Container

container = Container()
container.wire(
    modules=[
        "dormyboba.handlers.injection",
    ],
)

from .handlers import (
    common,
    invite,
    mailing,
    queue,
    defect,
)

labelers = (
    container.common_labeler(),
    container.invite_labeler(),
    container.mailing_labeler(),
    container.queue_labeler(),
    container.defect_labeler(),
)

labeler = BotLabeler()

for module_labeler in labelers:
    labeler.load(module_labeler)

bot = Bot(
    api=container.api(),
    state_dispenser=container.state_dispenser(),
    labeler=labeler,
)

@bot.error_handler.register_error_handler(RuntimeError)
async def runtime_error_handler(e: RuntimeError):
    print("Runtime error has occured", e)

if __name__ == "__main__":
    config = container.config()
    print(config)
    channel = container.channel()
    try:
        bot.loop_wrapper.add_task(mailing.mailing_task())
        bot.loop_wrapper.add_task(queue.queue_task())
        bot.run_forever()
    except Exception as exc:
        channel.close()
        print(exc)