from src import bot, sqldb, constants
# from src.constants import is_channel_member,IsAdmin, MyStates, echo, help, keyboards, movie_data
import requests
from bs4 import BeautifulSoup
import html.parser
from telebot import types, formatting
import sqlite3


#* -------------------------------------------------------------------------------------------------    
#* callback queries


@bot.callback_query_handler(func=None, validator='joined')
def join_check(call: types.CallbackQuery):
    user_id = call.from_user.id
    if constants.is_channel_member(user_id):
        bot.send_message(user_id, f"{formatting.hbold('Thank you for joining us ❤️.')}\nYou can now use the bot.")
        return
    bot.answer_callback_query(call.id, 
        "You are not joined yet. Please first join and then press Done.",True)

    
#* -------------------------------------------------------------------------------------------------    
#* content types handlers


#* -------------------------------------------------------------------------------------------------    
#* general commands


@bot.message_handler(commands=["start"], chat_types=["private"]) # Todo: fix this function
def start(msg):
    user_id = msg.from_user.id
    #ToDo saves user's info into database
    
    # uploads message if send command contains file id
    constants.echo(msg)

        
@bot.message_handler(commands=["help"]) # Todo: fix this function
def help(msg: types.Message):
    bot.send_message(msg.chat.id, help, 'MarkdownV2')



@bot.message_handler(commands=["ersal"], bot_admin=True) # Todo: fix this function
def send_all(msg: types.Message):
    users = 0
    try:
        reply_msg = msg.reply_to_message.message_id
    except AttributeError:
        bot.send_message(msg.from_user.id, "Reply this command to a message you want to send to bot users.")

    for i in sqldb.user_ids()[1]:
        try:
            bot.copy_message(i, msg.from_user.id, reply_msg)
            users += 1
        except Exception as e:
            print(e)
    bot.send_message(msg.from_user.id, f"Message sent succesfully to {users} users.")

# just to chnage
@bot.message_handler(commands=["fileid"])
def msgid(msg: types.Message):
    try:
        if msg.reply_to_message.content_type == "video":
            file_id = msg.reply_to_message.video.file_id
        elif msg.reply_to_message.content_type == "document":
            file_id = msg.reply_to_message.document.file_id
        else:
            return bot.send_message(msg.chat.id, "❌ Reply This message to a video or document(file).")
    except AttributeError:
        return bot.send_message(msg.chat.id, "❌ Reply This message to a video or document (file).")
    bot.send_message(msg.chat.id, file_id)


@bot.message_handler(commands=["file"])
def file_command(msg: types.Message):
    file_id = msg.text.split(' ')[1]
    try:
        bot.send_document(msg.chat.id, file_id)
    except:
        try:
            bot.send_video(msg.chat.id, file_id)
        except:
            bot.send_message(msg.chat.id, "❌ No such file id found in database!")

#* -------------------------------------------------------------------------------------------------    
#* functions related to admins or super user



@bot.message_handler(commands=["users"]) # Todo: fix this function
def users(msg):
    if msg.from_user.id == 247768888:
        arg = msg.text.split(" ")
        action = {"user": sqldb.user_ids()[0], "id": sqldb.user_ids()[1]}
        result = action.get(
            arg[1], "Wrong command argument! use 'user' or 'id'"
        )
        with open('users.txt', 'w') as f:
            f.write(str(result))
        with open('users.txt', 'r') as f:
            bot.send_document(msg.chat.id, f)

            
#* ------------------------------------------------------------------------------------------------- 
#* other functions


def award_data(_id, title):
    title = title.replace(' ', '-')
    read = requests.get(f"https://mubi.com/en/tr/films/{title}/awards")
    soup = BeautifulSoup(read.content, "html.parser")
    # returns an iterable containing all the HTML for all the listings displayed on that page
    awards = soup.find_all("div", class_="css-wffprx e1at15620")
    aws = {}

    for award in awards:
        name = award.find("a", class_='css-15hqn5v e1at15624').text
        if name in constants.AWARDS.keys():
            year = award.find("div", class_='css-16kkjs e1at15626').text.split(' ')[0]
            if aws.get(name, None):
                aws[name].add(year)
            else:
                aws[name] = {year}

    sqldb.add_awards(_id, aws)

#    0      1      2      3       4        5        6        7      8      9        10    11
# (Title, imdbID, Year, Genre, Runtime, Director, Writers, Actors, Plot, Ratings, Poster, Type)
@bot.inline_handler(lambda query: True, bot_admin=True)
def query_movies(inline_query: types.InlineQuery):
    queries = []
    id = 1

    title = inline_query.query
    if inline_query.query == '':
        title = None
    for i in sqldb.get_data(title):
        caption = constants.movie_data(i[0], i[1], i[9], i[4], i[2], i[3], i[8], i[5], i[6], i[7])
        markup = constants.media_markup(i[1], i[11], inline_query.from_user.id)
        r = types.InlineQueryResultArticle(id, i[0], types.InputTextMessageContent(caption, parse_mode='HTML'),
                                           description=i[11], thumbnail_url=i[10], reply_markup=constants.inline_markup(markup, 2)) #Todo: inline keyboard for dl
        queries.append(r)
        id += 1
    bot.answer_inline_query(inline_query.id, queries, 1)


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'dl')
def show_quals(call: types.CallbackQuery):
    _, _id, type = call.data.split(' ')
    if type == 'movie':
        movie = sqldb.get_movie_quals(_id)
        markup = {}
        for qual in movie:
            user_id = call.from_user.id
            if user_id not in constants.USER_DATA:
                constants.USER_DATA[user_id] = {}

            constants.USER_DATA[user_id][qual[1]] = {
                'captions': qual[2],
                'file_ids': qual[0]
            }
            markup[f'🎥 {qual[1]}'] = f'send {qual[1]}'
    else:
        pass
    markup[f'⬅️ Back'] = f'back-media {type} {_id}'

    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=constants.inline_markup(markup, 1))


@ bot.callback_query_handler(func=lambda call: 'send' == call.data.split(' ')[0])
def send_files(call: types.CallbackQuery):
    quality = call.data[5:]
    captions = constants.USER_DATA[call.from_user.id][quality]['captions'].split('///')
    file_ids = constants.USER_DATA[call.from_user.id][quality]['file_ids'].split('///')

    for file_id, caption in zip(file_ids, captions):
        try:
            bot.send_document(call.from_user.id, file_id, caption=caption)
        except:
            bot.send_video(call.from_user.id, file_id, caption=caption)
    del constants.USER_DATA[call.from_user.id][quality]


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] in ['delf', 'dela'])
def data_del(call: types.CallbackQuery):
    data, movie, type = call.data.split(' ')
    table = {'movie': 'movies', 'series': 'episodes'}
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table[type]} WHERE id = ?", (movie,))
        if data == 'dela':
            cursor.execute("DELETE FROM media WHERE imdbID = ?", (movie,))
        conn.commit()
    bot.send_message(call.from_user.id, "✅ Deleted succesfully.")


@ bot.callback_query_handler(func=lambda call: 'ed' == call.data.split(' ')[0])
def edit_data(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, 'Not implemented yet!')



@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'back-media')
def send_files(call: types.CallbackQuery):
    _, type, _id = call.data.split(' ')
    markup = constants.media_markup(_id, type, call.from_user.id)
    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=constants.inline_markup(markup))