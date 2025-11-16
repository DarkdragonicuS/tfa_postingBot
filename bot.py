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

from aiogram import Dispatcher, Bot, types, F
from aiogram.filters import Command, CommandObject
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import TELEGRAM_BOT_TOKEN, E621_API_KEY, E621_API_USERNAME
from random import shuffle
import requests
from global_vars.vars import TAG_SPECIES, TAG_GENERAL, TAG_CHARACTERS, TAG_GENERAL_MAPPING, TAGS_ORDER, TAG_IMPLICATIONS, TAG_SYNONYMS, TAG_SPOILERED
import hashlib
from io import BytesIO
from datetime import datetime

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(F.text, Command("hi"))
async def command_hi(message: types.Message):
    await message.reply(f"{message.from_user.mention_html('@' + message.from_user.first_name)}, и тебе привет!")

async def reverse_search(image_file_id):
    # Download the image file from Telegram
    image_file = await bot.get_file(image_file_id)
    image_bytes = BytesIO()
    await bot.download(image_file,image_bytes)
      
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
        image_md5 = hashlib.md5(image_bytes.read()).hexdigest()
        try:
            return {"md5": image_md5, "posts": data[0]["post"]["posts"]}
        except (KeyError, IndexError):
            return ["Error: Unable to parse response"]
    else:
        # Return an error message
        return ["Error: {}".format(response.status_code)]

async def get_post(post_id):
    """
    Downloads a post from e621.net

    Args:
        post_id: The id of the post to download

    Returns:
        A dictionary containing the post's information, or a list of error messages
    """

    # Set the API endpoint and parameters
    url = f"https://e621.net/posts/{post_id}.json"
    auth = requests.auth.HTTPBasicAuth(E621_API_USERNAME,E621_API_KEY)
    headers = {
        "User-Agent": "TFA Posting Bot"
    }

    # Send the request
    response = requests.get(url, auth=auth, headers=headers)

    # Check if the response was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        post = data["post"]
        #post["tag_string"] = post["tags"].join(", ")
        tag_string = ""
        for type in post["tags"]:
            for tag in post["tags"][type]:
                tag_string += tag + " "
        post["tag_string"] = tag_string
        post["large_file_url"] = post["file"]["url"]
        md5 = post["file"]["md5"]
        # Return the results
        try:
            return {"posts": post, "md5": md5}
        except (KeyError, IndexError):
            return ["Error: Unable to parse response"]
    else:
        # Return an error message
        return ["Error: {}".format(response.status_code)]

# Define a handler for the /reverse_search command
@dp.message(F.photo)
async def handle_reverse_search(message: types.Message):
    print('Recieved image to search')
    # Check if the user sent an image file
    if message.photo:
        # Send the results to the user
        result = await send_image_source(message)
        if result is not None:
            try:
                await message.delete()
            except Exception as e:
                pass
    else:
        # Send an error message
        await message.reply("Please send an image file to perform a reverse search.")

@dp.channel_post(F.photo)
async def handle_reverse_search_channel(message: types.Message):
    print('URL: ' + message.get_url())
    if message.caption is None and message.media_group_id is None:
        print('Recieved image to search')
        # Check if the user sent an image file
        if message.photo:
            # Get the image file ID
            #await send_image_source(message=message, edit_message=True)
            await send_image_source(message=message, edit_message=False)
        else:
            # Send an error message
            await message.reply("Please send an image file to perform a reverse search.")
    else:
        print('Ignored image to search because it has a caption')

@dp.channel_post(F.animation)
async def handle_reverse_search_channel(message: types.Message):
    print('URL: ' + message.get_url())
    print('It''s an animation. Skipping...')

@dp.channel_post(F.video)
async def handle_reverse_search_channel(message: types.Message):
    print('URL: ' + message.get_url())
    print('It''s a video. Skipping...')

@dp.message(F.text, Command(commands=['source','delsource'], prefix='/'))
async def handle_source_command(message: types.Message, command: CommandObject):
    print('Recieved image to search')
    reply_message = message.reply_to_message
    if reply_message and reply_message.photo:
        await send_image_source(message, reply_message)
        try:
            await message.delete()
        except Exception as e:
            pass
        
        if command.command == 'delsource':
            try:
                await reply_message.delete()
            except Exception as e:
                pass
    else:
        await message.reply("Please reply to a photo message with this command.") 

async def sort_tags(tags):
    sorted_tags = []
    for tag_group in TAGS_ORDER:
        for tag in tags:
            if tag in tag_group and tag not in sorted_tags:
                sorted_tags.append(tag)
    return sorted_tags

async def convert_tags(tags):
    return [tag.replace('(', '').replace(')', '').replace('-', '_') for tag in tags]

def remap_tags(tags):
    # Rename tags according to TAG_GENERAL_MAPPING
    for i, tag in enumerate(tags):
        if tag in TAG_GENERAL_MAPPING:
            tags[i] = TAG_GENERAL_MAPPING[tag]

    # Remove implied tags
    for i, tag in enumerate(tags):
        if tag in TAG_IMPLICATIONS and TAG_IMPLICATIONS[tag] in tags:
            tags.remove(tag)
    return tags

async def send_image_source(message, reply_message=None, edit_message=False, tags_as_buttons=False, src=None):
    
    if reply_message is None:
        reply_message = message

    # Get post info by post id
    if src is not None:
        results = await get_post(src)
    # Get post info by image reverse search
    else:        
        image_file_id = reply_message.photo[-1].file_id
        results = await reverse_search(image_file_id)
    
    if isinstance(results, dict):
        pass
    else:
        try:
            await reply_message.reply("Image source not found")
        except Exception as e:
            pass
        return
    tags = results['posts']['tag_string'].split()

    img_file_url = results['posts'].get('large_file_url', None)
    if not img_file_url:
        img_file_url = reply_message.photo[-1].file_id

    #source_file_url = results['posts']['large_file_url']
    #tags = remap_tags(tags)
    post_tags = []
    for tag in tags:
        if tag in TAG_SPECIES:
            post_tags.append(tag)
        if tag in TAG_CHARACTERS:
            post_tags.append(tag)
        if tag in TAG_GENERAL:
            if tag in TAG_GENERAL_MAPPING:
                post_tags.append(TAG_GENERAL_MAPPING[tag])
    post_tags = remap_tags(post_tags)
    post_tags = await sort_tags(post_tags)
    post_tags = await convert_tags(post_tags)
    post_url = 'https://e621.net/posts/' + str(results['posts']['id'])
    md5 = results['md5']
    message_reply = f'MD5: {md5}\nTags: {" ".join(post_tags)}\n{post_url}'

    caption = ""
    caption_entities = []
    for tag in post_tags:
        hashtag_entity = types.MessageEntity(
            type="hashtag",
            offset=len(caption),
            length=len(tag) + 1 # plus one for the hash symbol
        )
        caption_entities.append(hashtag_entity)
        caption += f"#{tag} "
    blockquote_entity = types.MessageEntity(
        type="expandable_blockquote",
        offset=0,
        length=len(caption),
    )
    caption_entities.append(blockquote_entity)

    inline_kb_list = []
    if tags_as_buttons:
        row = []
        for tag in post_tags:
            button = types.InlineKeyboardButton(text=tag, callback_data=tag)
            row.append(button)
            if len(row) == 3:
                inline_kb_list.append(row)
                row = []
        if row:
            inline_kb_list.append(row)
    else:
        message_reply = f'MD5: {md5}\nTags: {caption}\n{post_url}'

    button = types.InlineKeyboardButton(text='e621', url=post_url)
    inline_kb_list.append([button])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    
    #if edit_message and (message.forward_from_chat and message.chat.id == message.forward_from_chat.id):
    if edit_message:
        if tags_as_buttons:
            try:
                await reply_message.edit_caption(caption=caption, caption_entities=caption_entities, reply_markup=keyboard, parse_mode=None)
            except Exception as e:
                print(f"Error editing caption: {e}")
        else:
            try:
                await reply_message.edit_caption(caption=caption, caption_entities=caption_entities, reply_markup=keyboard, parse_mode=None)
            except Exception as e:
                print(f"Error editing caption: {e}")
    else:
        if any(tag in post_tags for tag in TAG_SPOILERED):
            try:
                await bot.send_photo(message.chat.id, img_file_url, caption=caption, caption_entities=caption_entities, reply_markup=keyboard, has_spoiler=True, parse_mode=None)
            except Exception as e:
                print(f"Error sending photo with spoiler: {e}")
                await bot.send_photo(message.chat.id, img_file_url, caption=caption, caption_entities=caption_entities, reply_markup=keyboard, parse_mode=None)
        else:
            #await bot.send_photo(message.chat.id, reply_message.photo[-1].file_id, caption=" ".join([f"#{tag}" for tag in post_tags]), reply_markup=keyboard)
            try:
                await bot.send_photo(message.chat.id, img_file_url, caption=caption, caption_entities=caption_entities, reply_markup=keyboard, parse_mode=None)
            except Exception as e:
                print(f"Error sending photo: {e}")
                await bot.send_message(message.chat.id, text=caption, reply_markup=keyboard)
        try:
            await message.delete()
        except Exception as e:
            pass

    return message_reply

@dp.channel_post(Command(commands=['source', 'delsource'], prefix='/'))
async def handle_reverse_search_channel_commands(message: types.Message, command: CommandObject):
    print(f"{datetime.now().isoformat()} - {message.text}")
    if command.command in ['source', 'delsource']:
        args = command.args
        print('Recieved image to search')
        reply_message = message.reply_to_message
        if reply_message and reply_message.photo:
            if reply_message.media_group_id is None:
                if args:
                    result = await send_image_source(message=message, reply_message=reply_message, src=args)
                else:
                    result = await send_image_source(message=message, reply_message=reply_message)
            else:
                if args:
                    result = await send_image_source(message=message, reply_message=reply_message, edit_message=True, src=args)    
                else:
                    result = await send_image_source(message=message, reply_message=reply_message, edit_message=True)
            # try:
            #     await message.delete()                
            # except Exception as e:
            #     pass
            
            if command.command == 'delsource' and result is not None:
                try:
                    await reply_message.delete()
                except Exception as e:
                    pass
            try:
                await message.delete()
            except Exception as e:
                pass
        else:
            await message.reply("Please reply to a photo message with this command.")