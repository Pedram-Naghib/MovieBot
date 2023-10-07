from telebot import types, TeleBot
from telebot.storage import StateMemoryStorage
from flask import Flask, request
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


TOKEN = os.environ['BotToken']
state_storage = StateMemoryStorage()
bot = TeleBot(TOKEN, parse_mode='HTML', state_storage=state_storage) #, use_class_middlewares=True
bot.delete_webhook()

server = Flask(__name__)

API_KEY = os.environ['OMDB_API']

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://moviebotdream-8d82606f47a7.herokuapp.com/' + TOKEN)
    return "!", 200


@server.after_request
def add_vary_header(response):
    response.headers['Vary'] = 'Cookie'
    return response


from src import constants, responses, sqldb, register, bottuns
