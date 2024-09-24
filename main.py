# Copyright (C) 2024 Nixiris Dartero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot
from bot import dp, bot
from config import TELEGRAM_BOT_TOKEN, ENDPOINT_URL, WEBAPP_HOST, WEBAPP_PORT
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

uvicorn.run(app=app,host=WEBAPP_HOST,port=WEBAPP_PORT)
