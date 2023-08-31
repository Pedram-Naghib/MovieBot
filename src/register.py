from src import bot, API_KEY, sqldb, constants
from src.responses import award_data
from telebot import types, formatting
import requests
import json


@bot.message_handler(commands=["register"], chat_types=["private"], bot_admin=True)
def video_handler(msg: types.Message):
    bot.send_message(msg.from_user.id, "Send me the IMDB ID.")
    bot.set_state(msg.from_user.id, constants.MyStates.file_imdb_id, msg.chat.id)


@bot.message_handler(state=constants.MyStates.file_imdb_id)
def get_id(message):
    """
    State 1. Will process when user's state is MyStates.file_imdb_id.
    """
    url = f"http://www.omdbapi.com/?i={message.text}&apikey={API_KEY}"
    resp = requests.get(url)
    file_data = json.loads(resp.text)
    if file_data["Response"] == 'False':
        return bot.send_message(message.chat.id, "❌ IMDB ID that you have entered is incorrect.")
    title = formatting.hbold(file_data["Title"])

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['data'] = file_data

    # if sqldb.exists(message.text):
    #     command = formatting.hcode(f'/edit {message.text}')
    #     return bot.send_message(message.chat.id, f"❌ This movie already exists. Try editing it with {command}")

    bot.send_message(message.chat.id, f"⚠️ You entered the id for title: {title}\nIf you want to proceed type in your file's quality:",
                     reply_markup=constants.keyboards.cancel)
    bot.set_state(message.from_user.id, constants.MyStates.confirmation, message.chat.id)
    

@bot.message_handler(state="*", commands=['cancel'])
def cancel_state(message):
    """
    Cancel state
    """
    try:
        bot.send_message(message.chat.id, "✅ The process was canceled.", reply_markup=types.ReplyKeyboardRemove())
        bot.delete_state(message.from_user.id, message.chat.id)
    except KeyError:
        bot.send_message(message.chat.id, "❌ No ongoing process found.")


@bot.message_handler(state="*", commands=['done'])
def done_state(message):
    """
    Done state
    """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data = data['data']
            all_ids, all_captions = '///'.join(data['all_ids']), '///'.join(data['captions'])
            if not sqldb.exists(data['imdbID']):
                sqldb.add_data(data) # add media data to db
                award_data(data['imdbID'], data['Title']) # add awards to db
            sqldb.insert_file((all_ids, data['imdbID'], data['quality'], all_captions)) # add media file to db

        bot.send_message(message.chat.id, "👍 Type in another quality or /cancel .", reply_markup=constants.keyboards.cancel)
        bot.set_state(message.from_user.id, constants.MyStates.confirmation, message.chat.id)
    except KeyError as e:
        bot.send_message(message.chat.id, "❌ No ongoing process found.")
        print(e)


@bot.message_handler(state=constants.MyStates.confirmation)
def confirm(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['data']['quality'] = message.text

        if data['data']["Type"] == 'series':
            # ask user send file for each ep and season
            bot.set_state(message.from_user.id, constants.MyStates.series, message.chat.id)
        else:
            bot.send_message(message.chat.id, "✅ Send the video/file or /done .", reply_markup=constants.keyboards.done)
            bot.set_state(message.from_user.id, constants.MyStates.movie, message.chat.id)


@bot.message_handler(state=constants.MyStates.series)
def series(message):
    pass


@bot.message_handler(state=constants.MyStates.movie, content_types = ['video', 'document'])
def movie(message: types.Message):
    if message.content_type == "video":
        file_id = message.video.file_id
        name = message.video.file_name
    else:
        file_id = message.document.file_id
        name = message.document.file_name
    
    caption = message.caption if message.caption else name
    if len(caption) > 128:
        return bot.send_message(message.chat.id, f"❌ Caption or file name(in cases which caption is empty) is too long. please add a shorter caption.")
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data['data'].get('all_ids', None) == None:
            data['data']['all_ids'] = [file_id]
            data['data']['captions'] = [caption]
        else:
            data['data']['all_ids'].append(file_id)
            data['data']['captions'].append(caption)
    
    bot.send_message(message.chat.id, f"✅ Added {name}.\nsend more or /done .")