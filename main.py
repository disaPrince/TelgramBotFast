import json
import urllib3
import telebot
from os import getenv
import md5util
import logging

logger = telebot.logger

token = getenv('TELEGRAM_TOKEN', '6060711671:AAHUMAUupbtsEyqIhWMsgODzETU6Bjn5JxM')
domain = getenv('DOMAIN', 'http://localhost/FastKomek/FastKomek/public/api')
bot = telebot.TeleBot(token, parse_mode='html')
hash_telegram = md5util.Md5Util.get_data_md5({'token': token}, ['token'])

@bot.message_handler(commands=['start'])
def welcome(message_data):
    try:
        http = urllib3.PoolManager()
        encoded_body = json.dumps({
            'hash': hash_telegram,
            'telegram_id': message_data.chat.id,
            'user_name': message_data.chat.username,
            'message_id': message_data.message_id
        })
        result = http.request('POST', domain + '/start',
                              headers={'Content-Type': 'application/json'},
                              body=encoded_body)
        if result.status == 401:
            bot.send_message(chat_id=message_data.chat.id, text='Oops... Bot is unavailable:(')
    except:
        return True

@bot.message_handler(content_types=['text'])
def message(message_data):
    try:
        http = urllib3.PoolManager()
        encoded_body = json.dumps({
            'hash': hash_telegram,
            'telegram_id': message_data.chat.id,
            'user_name': message_data.chat.username,
            'message': message_data.text,
            'message_id': message_data.message_id
        })
        result = http.request('POST', domain + '/message',
                              headers={'Content-Type': 'application/json'},
                              body=encoded_body)
        if result.status != 200:
            logger.setLevel(logging.WARN)
            logger.log(msg=result.data, level=logging.WARN)
    except:
        return True

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        http = urllib3.PoolManager()
        encoded_body = json.dumps({
            'hash': hash_telegram,
            'telegram_id': call.message.chat.id,
            'callback': call.data,
            'message_id': call.message.id,
        })
        result = http.request('POST', domain + '/callback',
                              headers={'Content-Type': 'application/json'},
                              body=encoded_body)
        if result.status == 401:
            logger.setLevel(logging.WARN)
            logger.log(msg=result.data, level=logging.WARN)
    except:
        return True

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)