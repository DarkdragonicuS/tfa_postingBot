from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot
from bot import dp, bot
from config import TELEGRAM_BOT_TOKEN, ENDPOINT_URL
import uvicorn

app = FastAPI()
WEBHOOK_PATH = f"/bot/{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = f"{ENDPOINT_URL}{WEBHOOK_PATH}"
# bot = Bot(token=TELEGRAM_BOT_TOKEN)
# dp = Dispatcher(bot)
# dp.skip_updates()

@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()

uvicorn.run(app=app,host='0.0.0.0',port=8080)