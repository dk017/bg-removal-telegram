import telebot
import os
from rembg import remove
import random
import string
import redis
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

TOKEN = "5554608527:AAGYjK2aViWGOYWDbJza8wvzqmLLrz0H_eQ"
bot = telebot.TeleBot(TOKEN)

PORT = int(os.environ.get('PORT', 5000))
re = redis.Redis(
    host="redis-16901.c92.us-east-1-3.ec2.cloud.redislabs.com",
    port="16901",
    password="PwXaZGzSnG2xejDqWrI2GLcrwhCzNxyt"
)


def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(text='BuyMeACoffee', url='https://www.buymeacoffee.com/dk17'))
    return markup


# Handles all text messages that contains the commands '/start' or '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    print(message.from_user)
    bot.reply_to(message, "Hey!!!! Upload the picture for which you want to remove the background for.")


@bot.message_handler(content_types=['photo'])
def handle_docs_audio(message):
    res = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits, k=5))
    cid = message.chat.id
    send_suggestion = False
    fileID = message.photo[-1].file_id
    file = bot.get_file(fileID)
    downloaded_file = bot.download_file(file.file_path)
    output_path = 'output' + res + '.png'
    input_path = 'input' + res + '.png'
    with open(input_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    try:
        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                read_input = i.read()
                read_output = remove(read_input)
                o.write(read_output)
    except:
        bot.send_message("Issue with processing your image. We are on it already. Try after sometime!!!")
    bot.send_photo(cid, open(output_path, 'rb'))
    count = re.get(cid)
    if count is not None:
        count = int(count) + 1
        if count % 10 == 0:
            send_suggestion = True
        re.set(cid, count)
        print(count)
    else:
        re.set(cid, 1)

    if send_suggestion:
        bot.send_message(
            cid,
            text='Hope you are enjoying the tool!!!\nConsider buying me a coffee if you wish!!!',
            reply_markup=gen_markup()
        )

    if os.path.exists(output_path):
        os.remove(output_path)
    else:
        print("The file does not exist")

    if os.path.exists(input_path):
        os.remove(input_path)
    else:
        print("The file does not exist")


bot.infinity_polling()
