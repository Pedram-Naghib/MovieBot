from src import bot, API_KEY, sqldb, constants
from src.responses import award_data
from telebot import types, formatting
import requests
import json
import re


def register_data(_id, chatid):
    url = f"http://www.omdbapi.com/?i={_id}&apikey={API_KEY}"
    resp = requests.get(url)
    file_data = json.loads(resp.text)
    if file_data["Response"] == 'False':
        return bot.send_message(chatid, "❌ IMDB ID that you have entered is incorrect.")
    return file_data


def register_log(data):
    with open('log.txt', 'a+') as f:
        f.write(f'\n{data}')
        f.seek(0)
        lines = f.readlines()
        rss = lines[-20:][::-1]
        # Truncate the file to keep only the last 20 lines
        f.truncate(0)
        f.writelines(rss[::-1])


@bot.message_handler(commands=["register"], chat_types=["private"], bot_admin=True)
def register_media(msg: types.Message):
    bot.send_message(msg.from_user.id, "Send me the IMDB ID.")
    bot.set_state(msg.from_user.id, constants.MyStates.file_imdb_id, msg.chat.id)


@bot.message_handler(state=constants.MyStates.file_imdb_id)
def get_id(message):
    """
    State 1. Will process when user's state is MyStates.file_imdb_id.
    """
    file_data = register_data(message.text, message.chat.id)
    title = formatting.hbold(file_data["Title"])

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['data'] = file_data

    bot.send_message(message.chat.id, f"⚠️ You entered the id for title: {title}\nIf you want to proceed type in your file's quality:",
                     reply_markup=constants.keyboards.cancel)
    bot.set_state(message.from_user.id, constants.MyStates.confirmation, message.chat.id)
    

@bot.message_handler(state="*", commands=['cancel'])
def cancel_state(message):
    """
    Cancel state
    """
    try:
        bot.send_message(message.chat.id, "✅ The process was canceled.", reply_markup=constants.keyboards.home)
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
        register_log(f'{data["Title"]} ➡️ {data["quality"]} /dl_{data["imdbID"]}')
        del data['all_ids']
        del data['captions']
        bot.set_state(message.from_user.id, constants.MyStates.confirmation, message.chat.id)
    except KeyError as e:
        bot.send_message(message.chat.id, "❌ No ongoing process found.")
        print(e)


@bot.message_handler(state="*", commands=['ok'])
def ok_state(message):
    """
    Ok state
    """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data = data['data']
            all_ids, all_captions = '///'.join(data['all_ids']), '///'.join(data['captions'])
            season_ep = data['season_ep']
            if not sqldb.exists(data['imdbID']):
                sqldb.add_data(data) # add media data to db
            sqldb.insert_file([all_ids, data['imdbID'], data['quality'], all_captions], season_ep) # add media file to db

        bot.send_message(message.chat.id, "👍 Type in another quality or /cancel .", reply_markup=constants.keyboards.cancel)
        register_log(f'{data["Title"]} ➡️ {data["quality"]} /dl_{data["imdbID"]}')
        del data['all_ids']
        del data['captions']
        bot.set_state(message.from_user.id, constants.MyStates.confirmation, message.chat.id)
    except KeyError as e:
        bot.send_message(message.chat.id, "❌ No ongoing process found.")
        print(e)


@bot.message_handler(state=constants.MyStates.confirmation)
def confirm(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if len(message.text) > 58:
            return bot.send_message(message.chat.id, f"❌ Maximum allowed quality name lentgh -> 128 character\nCurrent quality name -> {len(message.text)}.")
        data['data']['quality'] = message.text

        if data['data']["Type"] == 'series':
            # ask user send file for each ep and season
            bot.send_message(message.chat.id, "✅ Send the video/file.", reply_markup=constants.keyboards.ok)
            bot.set_state(message.from_user.id, constants.MyStates.series, message.chat.id)
        else:
            bot.send_message(message.chat.id, "✅ Send the video/file.", reply_markup=constants.keyboards.done)
            bot.set_state(message.from_user.id, constants.MyStates.movie, message.chat.id)


@bot.message_handler(state=constants.MyStates.series, content_types = ['video', 'document'])
def series(message):
    if message.content_type == "video":
        file_id = message.video.file_id
        name = message.video.file_name
    else:
        file_id = message.document.file_id
        name = message.document.file_name
    
    caption = message.caption if message.caption else name
    matches = re.findall(r'S\d{2}\.?E\d{2}', caption)

    if not matches:
        return bot.send_message(message.chat.id, f'❌ Please add caption indicating season and ep number to your file. (ex: S01E08)')
    else:
        season_ep = matches[0]
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data['data'].get('all_ids', None) == None:
            data['data']['all_ids'] = [file_id]
            data['data']['captions'] = [caption]
            data['data']['season_ep'] = season_ep
        else:
            data['data']['all_ids'].append(file_id)
            data['data']['captions'].append(caption)
            # data['data']['season_ep'].append(season_ep)
    
    bot.send_message(message.chat.id, f"✅ Added {name}.\nsend more or /ok .")


@bot.message_handler(state=constants.MyStates.movie, content_types = ['video', 'document'])
def movie(message: types.Message):
    if message.content_type == "video":
        file_id = message.video.file_id
        name = message.video.file_name
    else:
        file_id = message.document.file_id
        name = message.document.file_name
    
    caption = message.caption if message.caption else name
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data['data'].get('all_ids', None) == None:
            data['data']['all_ids'] = [file_id]
            data['data']['captions'] = [caption]
        else:
            data['data']['all_ids'].append(file_id)
            data['data']['captions'].append(caption)
    
    bot.send_message(message.chat.id, f"✅ Added {name}.\nsend more or /done .")


@bot.message_handler(commands=["cd"], chat_types=["private"], bot_admin=True)
def add_cd(msg: types.Message):
    bot.set_state(msg.from_user.id, constants.MyStates.cd_extra, msg.chat.id)
    try:
        _, _id, *quality = msg.text.split(' ')
        quality = ' '.join(quality)
        if len(quality) > 58:
            return bot.send_message(msg.chat.id, f"❌ Maximum allowed quality name lentgh -> 128 character\nCurrent quality name -> {len(quality)}.")
    except ValueError:
        bot.send_message(msg.chat.id, f'❌ Wrong command arguement.\nExample: {formatting.hbold("/cd tt4158110 quality")}')
    
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['id'], data['type'], data['quality'] = _id, 'cd', quality
        data['data'] = register_data(_id, msg.chat.id)
    bot.send_message(msg.chat.id, "✅ Send the video/file.", reply_markup=constants.keyboards.finish)


@bot.message_handler(commands=["extra"], chat_types=["private"], bot_admin=True)
def add_extra(msg: types.Message):
    bot.set_state(msg.from_user.id, constants.MyStates.cd_extra, msg.chat.id)
    try:
        _, _id, *name = msg.text.split(' ')
        name = ' '.join(name)
    except ValueError:
        return bot.send_message(msg.chat.id, f'❌ Wrong command arguement.\nExample: {formatting.hbold("/extra tt4158110 name")}')
    
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['id'], data['type'], data['quality'] = _id, 'extra', name
        data['data'] = register_data(_id, msg.chat.id)
    bot.send_message(msg.chat.id, "✅ Send the video/file.", reply_markup=constants.keyboards.finish)


@bot.message_handler(state=constants.MyStates.cd_extra, content_types = ['video', 'document'])
def cd_extra(message):
    if message.content_type == "video":
        file_id = message.video.file_id
        name = message.video.file_name
    else:
        file_id = message.document.file_id
        name = message.document.file_name
    
    caption = message.caption if message.caption else name
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data.get('all_ids', None) == None:
            data['all_ids'] = [file_id]
            data['captions'] = [caption]
        else:
            data['all_ids'].append(file_id)
            data['captions'].append(caption)
    
    bot.send_message(message.chat.id, f"✅ Added {name}.\nsend more or /finish .")


@bot.message_handler(state="*", commands=['finish'])
def finish_state(message):
    """
    Finish state
    """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            all_ids, all_captions = '///'.join(data['all_ids']), '///'.join(data['captions'])
            if not sqldb.exists(data['data']['imdbID']):
                sqldb.add_data(data['data']) # add media data to db
            quality = None
            quality = data['quality']
            sqldb.cd_extra(data['type'], (data['id'], all_ids, quality, all_captions)) # add cd_extra file to db

        bot.send_message(message.chat.id, "👍 Type in another quality or /cancel .", reply_markup=constants.keyboards.cancel)
        register_log(f'{data["data"]["Title"]} ➡️ {data["quality"]} /dl_{data["data"]["imdbID"]}')
        del data['all_ids']
        del data['captions']
        bot.set_state(message.from_user.id, constants.MyStates.cd_extra_confirm, message.chat.id)
    except KeyError as e:
        bot.send_message(message.chat.id, "❌ No ongoing process found.")
        print(e)


@bot.message_handler(state=constants.MyStates.cd_extra_confirm)
def cd_extra_confirm(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if len(message.text) > 58:
            return bot.send_message(message.chat.id, f"❌ Maximum allowed quality name lentgh -> 128 character\nCurrent quality name -> {len(message.text)}.")
        data['data']['quality'] = message.text

        bot.send_message(message.chat.id, "✅ Send the video/file.", reply_markup=constants.keyboards.finish)
        bot.set_state(message.from_user.id, constants.MyStates.cd_extra, message.chat.id)