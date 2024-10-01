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

from aiogram import Dispatcher, Bot, types
from config import TELEGRAM_BOT_TOKEN, E621_API_KEY, E621_API_USERNAME
from random import shuffle
import requests
from global_vars.vars import TAG_SPECIES
import hashlib
from requests_toolbelt.multipart import MultipartEncoder
from io import BytesIO

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands="hi")
async def start(message: types.Message):
    await message.answer(f"{message.from_user.mention}, и тебе привет!")

async def reverse_search(image_file_id):
    # Download the image file from Telegram
    image_file = await bot.download_file_by_id(image_file_id)
    image_bytes = BytesIO(image_file.read())
      
    # Set the API endpoint and parameters
    url = "https://e621.net/iqdb_queries.json"
    auth = requests.auth.HTTPBasicAuth(E621_API_USERNAME,E621_API_KEY)
    parameters = {
        "limit": 1
    }
    headers = {
        "User-Agent": "TFA Posting Bot"
    }

    # Send the request
    response = requests.post(url, auth=auth, headers=headers, files={'file': image_bytes}, params=parameters)

    # Check if the response was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Return the results
        image_md5 = hashlib.md5(image_file.read()).hexdigest()
        try:
            return {"md5": image_md5, "posts": data[0]["post"]["posts"]}
        except (KeyError, IndexError):
            return ["Error: Unable to parse response"]
    else:
        # Return an error message
        return ["Error: {}".format(response.status_code)]

# Define a handler for the /reverse_search command
@dp.message_handler(content_types=["photo"])
async def handle_reverse_search(message: types.Message):
    print('Recieved image to search')
    # Check if the user sent an image file
    if message.photo:
        # Get the image file ID
        image_file_id = message.photo[-1].file_id
        # Perform the reverse search
        results = await reverse_search(image_file_id)
        if isinstance(results, dict):
            pass
        else:
            await message.reply("Error: Unable to parse response")
            return
        # Send the results to the user
        tags = results['posts']['tag_string'].split()
        post_tags = []

        for tag in tags:
            if tag in TAG_SPECIES:
                post_tags.append(tag)
        post_url = 'https://e621.net/posts/' + str(results['posts']['id'])
        md5 = results['md5']
        post_tags_str = ' '.join('#' + tag_to_print for tag_to_print in post_tags)
        message_reply = f'{post_url}\nMD5: {md5}\n{post_tags_str}'
        await message.reply(message_reply)
    else:
        # Send an error message
        await message.reply("Please send an image file to perform a reverse search.")

#if __name__ == '__main__':
#    executor.start_polling(dp, skip_updates=True)