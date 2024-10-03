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
from global_vars.vars import TAG_SPECIES, TAG_CHARACTERS, TAG_GENERAL, TAG_GENERAL_MAPPING
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
        # Send the results to the user
        await send_image_source(message)
        await message.delete()
    else:
        # Send an error message
        await message.reply("Please send an image file to perform a reverse search.")

@dp.channel_post_handler(content_types=["photo"])
async def handle_reverse_search_channel(message: types.Message):
    print('Recieved image to search')
    # Check if the user sent an image file
    if message.photo:
        # Get the image file ID
        #await send_image_source(message=message, edit_message=True)
        await send_image_source(message=message, edit_message=False)
    else:
        # Send an error message
        await message.reply("Please send an image file to perform a reverse search.")

@dp.message_handler(commands=['source','delsource'], content_types=["text"])
async def handle_source_command(message: types.Message):
    print('Recieved image to search')
    reply_message = message.reply_to_message
    if reply_message and reply_message.photo:
        await send_image_source(message, reply_message)
        try:
            await message.delete()
        except Exception as e:
            pass
        
        if message.text.startswith('/delsource'):
            try:
                await reply_message.delete()
            except Exception as e:
                pass
    else:
        await message.reply("Please reply to a photo message with this command.") 

async def send_image_source(message, reply_message=None, edit_message=False, tags_as_buttons=False):
    
    if reply_message is None:
        reply_message = message
    image_file_id = reply_message.photo[-1].file_id
    results = await reverse_search(image_file_id)
    if isinstance(results, dict):
        pass
    else:
        await message.reply("Error: Unable to parse response")
        return
    tags = results['posts']['tag_string'].split()
    post_tags = []
    for tag in tags:
        if tag in TAG_SPECIES:
            post_tags.append(tag)
        # if tag in TAG_CHARACTERS:
        #     post_tags.append(tag)
        if tag in TAG_GENERAL:
            if tag in TAG_GENERAL_MAPPING:
                post_tags.append(TAG_GENERAL_MAPPING[tag])
    post_url = 'https://e621.net/posts/' + str(results['posts']['id'])
    md5 = results['md5']
    message_reply = f'MD5: {md5}\nTags: {" ".join(post_tags)}\n{post_url}'
    keyboard = types.InlineKeyboardMarkup()
    if tags_as_buttons:
        row = []
        for tag in post_tags:
            button = types.InlineKeyboardButton(text=tag, callback_data=tag)
            row.append(button)
            if len(row) == 3:
                keyboard.row(*row)
                row = []
        if row:
            keyboard.row(*row)
    else:
        message_reply = f'MD5: {md5}\nTags: {" ".join([f"#{tag}" for tag in post_tags])}\n{post_url}'

    button = types.InlineKeyboardButton(text='e621', url=post_url)
    keyboard.add(button)
    
    #if edit_message and (message.forward_from_chat and message.chat.id == message.forward_from_chat.id):
    if edit_message:
        if tags_as_buttons:
            await reply_message.edit_caption(" ".join([f"#{tag}" for tag in post_tags]), reply_markup=keyboard)
        else:
            await reply_message.edit_caption(" ".join([f"#{tag}" for tag in post_tags]), reply_markup=keyboard)
    else:
        if 'cub' in post_tags:
            await bot.send_photo(message.chat.id, reply_message.photo[-1].file_id, caption=" ".join([f"#{tag}" for tag in post_tags]), reply_markup=keyboard, has_spoiler=True)
        else:
            await bot.send_photo(message.chat.id, reply_message.photo[-1].file_id, caption=" ".join([f"#{tag}" for tag in post_tags]), reply_markup=keyboard)

    return message_reply

