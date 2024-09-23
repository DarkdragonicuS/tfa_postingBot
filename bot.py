from aiogram import Dispatcher, Bot, types
from config import TELEGRAM_BOT_TOKEN, E621_API_KEY, E621_API_USERNAME
from random import shuffle
import requests

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands="hi")
async def start(message: types.Message):
    await message.answer(f"{message.from_user.mention}, и тебе привет!")

async def reverse_search(image_file_id):
    # Download the image file from Telegram
    image_file = await bot.download_file_by_id(image_file_id)

    # Set the API endpoint and parameters
    url = "https://e621.net/iqdb_queries.json"
    auth = requests.auth.HTTPBasicAuth(E621_API_USERNAME,E621_API_KEY)
    headers = {
        "User-Agent": "TFA Posting Bot"
    }
    # Send the request
    response = requests.post(url, auth=auth, headers=headers, files={"file": image_file})

    # Check if the response was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Return the results
        return data[0]["post"]["posts"]
    else:
        # Return an error message
        return ["Error: {}".format(response.status_code)]

# Define a handler for the /reverse_search command
@dp.message_handler(content_types=["photo"])
async def handle_reverse_search(message: types.Message):
    # Check if the user sent an image file
    if message.photo:
        # Get the image file ID
        image_file_id = message.photo[-1].file_id
        # Perform the reverse search
        results = await reverse_search(image_file_id)
        # Send the results to the user
        #await message.reply(json.dumps(results))
        await message.reply('https://e621.net/posts/' + str(results['id']) + '\n' +
            ' '.join('#' + word for word in results['tag_string'].split()))
    else:
        # Send an error message
        await message.reply("Please send an image file to perform a reverse search.")

#if __name__ == '__main__':
#    executor.start_polling(dp, skip_updates=True)