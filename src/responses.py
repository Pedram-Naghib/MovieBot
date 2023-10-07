from src import bot, sqldb, constants, bottuns
# from src.constants import is_channel_member,IsAdmin, MyStates, echo, help, keyboards, movie_data
import requests
from bs4 import BeautifulSoup
import html.parser
from telebot import types, formatting
import sqlite3


#* -------------------------------------------------------------------------------------------------    
#* callback queries


@bot.callback_query_handler(func=lambda call: call.data == 'joined')
def join_check(call: types.CallbackQuery):
    user_id = call.from_user.id
    if constants.is_channel_member(user_id):
        return bot.send_message(user_id, f"{formatting.hbold('Thank you for joining us ❤️.')}\nYou can now use the bot.",
                         reply_markup=constants.keyboards.home)
    bot.answer_callback_query(call.id, 
        "You are not joined yet. Please first join and then press Done.",True)


#* -------------------------------------------------------------------------------------------------    
#* general commands


@bot.message_handler(commands=["start"], chat_types=["private"]) # Todo: fix this function
def start(msg):
    constants.echo(msg)
    user_id = msg.from_user.id
    sqldb.save_user(msg.from_user)
    if not constants.is_channel_member(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("✅", callback_data=f"joined"))
        
        return bot.send_message(user_id, f"لطفا برای استفاده از بات به چنل های زیر عضو شوید 👇\n\
چنل اطلاع رسانی: https://t.me/+Ao4dp9k25QgzZjg0\n\
چنل آرشیو: https://t.me/+VxnB-YYcAjEUz-hD",
            reply_markup=markup)
    # uploads message if send command contains file id

        
@bot.message_handler(commands=["help"]) # Todo: fix this function
def help(msg: types.Message):
    bot.send_message(msg.chat.id, help, 'MarkdownV2')


            
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
# (id, Title, imdbID, Year, Genre, Runtime, Director, Writers, Actors, Plot, Ratings, Poster, Type)
@bot.inline_handler(lambda query: True)
def query_movies(inline_query: types.InlineQuery):
    queries = []
    id = 1

    title = inline_query.query
    if inline_query.query == '':
        title = None
    markup = None
    results = sqldb.get_data(title)
    if results == None:
        markup = {"✅ تایید": f"send_sug {title}"}
        queries = [types.InlineQueryResultArticle(100, f"📲 درخواست اضافه شدن {title} به آرشیو.",
                                           types.InputTextMessageContent(f"ارسال درخواست اضافه شدن {title} به آرشیو؟"),
                                           reply_markup=constants.inline_markup(markup))]
    else:
        for i in results:
            caption = constants.movie_data(i[1], i[2], i[10], i[5], i[3], i[4], i[9], i[6], i[7], i[8])
            cd_extra = sqldb.cd_extra_exists(i[2])
            markup = constants.media_markup(i[2], i[12], inline_query.from_user.id, cd_extra)
            markup = constants.inline_markup(markup, 2)
            r = types.InlineQueryResultArticle(id, i[1], types.InputTextMessageContent(caption, parse_mode='HTML'),
                                            description=i[12], thumbnail_url=i[11], reply_markup=markup)
            queries.append(r)
            id += 1

    bot.answer_inline_query(inline_query.id, queries, 1)


@ bot.message_handler(regexp=r"dl_.*", chat_types=["private"])
def award_choose(msg):
    id = msg.text[4:]
    result = sqldb.get_data_by_id(id)
    for i in result:
        caption = constants.movie_data(i[1], i[2], i[10], i[5], i[3], i[4], i[9], i[6], i[7], i[8])
        cd_extra = sqldb.cd_extra_exists(i[2])
        markup = constants.media_markup(i[2], i[12], msg.from_user.id, cd_extra)
        markup = constants.inline_markup(markup, 2)
        bot.send_message(msg.chat.id, caption, parse_mode='HTML', reply_markup=markup)


@ bot.message_handler(commands=['rss'], chat_types=["private"], bot_admin=True)
def show_rss(msg):
    updates_list = bottuns.print_updates(display=False).split('\n')
    updates_dic = {}
    c = 0
    for i in updates_list:
        updates_dic[i] = f'rss {c}'
        c += 1
    markup = constants.inline_markup(updates_dic, 1)
    bot.send_message(msg.chat.id, 'Choose an update to delete 👇', reply_markup=markup)


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'rss')
def delete_rss(call: types.CallbackQuery):
    _, index = call.data.split(' ')
    # get the list again, delete the item, write the list on file
    updates_list = bottuns.print_updates(display=False).split('\n')
    print(updates_list, index)
    print(updates_list[int(index)])
    _, name_id = updates_list[int(index)].split('➡️')
    name, _id = name_id.split(' /dl_')
    print(name, _id)
    
    del updates_list[int(index)]
    print(updates_list)
    with open('log.txt', 'w') as log:
        for i in updates_list[::-1]:
            if i != '':
                log.write(f'{i}\n')
    bot.send_message(call.from_user.id, "✅ Deleted succesfully.")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'se')
def show_seasons(call: types.CallbackQuery):
    _, _id, type = call.data.split(' ')
    seasons = list(sqldb.season_ep_no(_id))
    markup = constants.season_markup(_id, seasons)
    if call.message:
        chat_id, message_id = call.message.chat.id, call.message.message_id
        return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=constants.inline_markup(markup, 1))
    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=constants.inline_markup(markup, 1))


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'season')
def show_eps(call: types.CallbackQuery):
    _, season, _id = call.data.split(' ')
    eps = sqldb.season_ep_no(_id, season)
    markup = constants.ep_markup(_id, season, eps)

    if call.message:
        chat_id, message_id = call.message.chat.id, call.message.message_id
        return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=constants.inline_markup(markup, 1))
    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=constants.inline_markup(markup, 1))


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'dl')
def show_quals(call: types.CallbackQuery):
    # uncomment next 4 lines when free trial ends!
    # if not constants.IsVIP.check(call):
    #     bot.answer_callback_query(call.id, ' this feature is only available for VIP members. Upgrade to VIP to unlock this feature and enjoy exclusive benefits!',
    #                               show_alert=True)
    #     return

    _, _id, type = call.data.split(' ')
    if type == 'movie':
        movie = sqldb.get_movie_quals(_id)
    elif type == 'cd':
        movie = sqldb.get_cdextra_quals(_id, 'cd')
    elif type == 'extra':
        movie = sqldb.get_cdextra_quals(_id, 'extra')
    else:
        s_ep, _id = _id, type
        movie = sqldb.get_series_quals(_id, s_ep)
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

    if type == 'series':
        markup[f'⬅️ Back'] = f'b-e {s_ep} {_id}'
    else:
        markup[f'⬅️ Back'] = f'back-media {type} {_id}'

    if call.message:
        chat_id, message_id = call.message.chat.id, call.message.message_id
        return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=constants.inline_markup(markup, 1))
    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=constants.inline_markup(markup, 1))


@ bot.callback_query_handler(func=lambda call: 'send' == call.data.split(' ')[0])
def send_files(call: types.CallbackQuery):
    quality = call.data[5:]
    try:
        captions = constants.USER_DATA[call.from_user.id][quality]['captions'].split('///')
        file_ids = constants.USER_DATA[call.from_user.id][quality]['file_ids'].split('///')
    except KeyError:
        bold = formatting.hbold
        return bot.send_message(call.from_user.id, f"Press '{bold('⬅️ Back')}' and then '{bold('📥 Encodes')}' again.")

    for file_id, caption in zip(file_ids, captions):
        try:
            bot.send_document(call.from_user.id, file_id, caption=caption)
        except:
            bot.send_video(call.from_user.id, file_id, caption=caption)
    del constants.USER_DATA[call.from_user.id][quality]


@ bot.callback_query_handler(func=lambda call: 'ed' == call.data.split(' ')[0])
def edit_data(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, 'Not implemented yet!')



@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'back-media')
def back_media(call: types.CallbackQuery):
    _, type, _id = call.data.split(' ')
    cd_extra = sqldb.cd_extra_exists(_id)
    markup = constants.media_markup(_id, type, call.from_user.id, cd_extra)

    if call.message:
        chat_id, message_id = call.message.chat.id, call.message.message_id
        return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=constants.inline_markup(markup, 2))
    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=constants.inline_markup(markup, 2))


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'b-s')
def back_season(call: types.CallbackQuery):
    _, _id = call.data.split(' ')
    seasons = list(sqldb.season_ep_no(_id))
    markup = constants.season_markup(_id, seasons)
    if call.message:
        chat_id, message_id = call.message.chat.id, call.message.message_id
        return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=constants.inline_markup(markup, 1))
    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=constants.inline_markup(markup, 1))


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'b-e')
def back_ep(call: types.CallbackQuery):
    _, s_ep, _id = call.data.split(' ')
    season = s_ep.split('.')[0]
    eps = sqldb.season_ep_no(_id, season)
    markup = constants.ep_markup(_id, season, eps)
    if call.message:
        chat_id, message_id = call.message.chat.id, call.message.message_id
        return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=constants.inline_markup(markup, 1))
    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=constants.inline_markup(markup, 1))


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'send_sug')
def media_suggest(call: types.CallbackQuery):
    _, title = call.data.split('send_sug ')
    user = call.from_user
    text = f"کاربری با مشخصات:\nFirst name: {user.first_name}\nLast name: {user.last_name}\nUsername: @{user.username}\n\nدرخواست برای اضافه شدن فیلم {title} به آرشیو کرده است."
    bot.send_message(-1001475842256, text)
    bot.answer_callback_query(call.id, "✅ درخواست شما با موفقیت ارسال شد.")

    if call.message:
        chat_id, message_id = call.message.chat.id, call.message.message_id
        return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
    bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=None)


@ bot.message_handler(commands=['del'], bot_admin=True)
def data_todelete(msg: types.Message):
    try:
        _, table = msg.text.split(' ')
        if table not in ['cd', 'extra', 'file', 'episode']:
            return bot.send_message(msg.chat.id, "Value should be cd, extra or encode")
    except ValueError:
        return bot.send_message(msg.chat.id, constants.del_help, reply_markup=constants.keyboards.cancel)

    bot.set_state(msg.from_user.id, constants.MyStates.delete, msg.chat.id)
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        data['table'] = table
    
    bot.send_message(msg.chat.id, constants.del_step1)


@bot.message_handler(state=constants.MyStates.delete)
def delete_db(msg: types.Message):
    _id, name = msg.text.split('\n')
    column = {'cd': 'cd_type', 'extra': 'type', 'movies': 'quality'}
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        table = 'movies' if data['table'] == 'file' else data['table']

    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        if table != 'episode':
            query = f"DELETE FROM {table} WHERE id = ? AND LOWER({column[table]}) LIKE '%' || LOWER(?) || '%'"
            cursor.execute(query, (_id, name))
        else:
            s, e = name.split('.')
            query = f"DELETE FROM episodes WHERE id = ? AND season = ? AND episode = ?"
            cursor.execute(query, (_id, s[1:], e[1:]))
        conn.commit()
    bot.send_message(msg.chat.id, "✅ Deleted succesfully.")
    
    
@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == '🗑')
def media_edit(call: types.CallbackQuery):
    _, _id, type = call.data.split(' ')
    bot.send_message(call.from_user.id, f"⚠️ Are you sure you want to delete everything about {_id} from database? (y/n)")
    bot.set_state(call.from_user.id, constants.MyStates.del_conf, call.from_user.id)
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data['id'], data['type'] = _id, type


@bot.message_handler(state=constants.MyStates.del_conf)
def delete_db(msg: types.Message):
    if msg.text.lower() == 'y':
        pass
    elif msg.text.lower() == 'n':
        return bot.send_message(msg.chat.id, "✅ Canceled.")
    else:
        return bot.send_message(msg.chat.id, "❌ Please answer with 'y' or 'n'.")
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
        _id, type = data['id'], data['type']
    table = {'movie': 'movies', 'series': 'episodes'}
    with sqlite3.connect('./database.db') as conn:
        cursor = conn.cursor()
        for table_ in ['awards', 'extra', 'cd']:
            cursor.execute(f"DELETE FROM {table_} WHERE id = ?", (_id,))
        cursor.execute("DELETE FROM data WHERE imdbID = ?", (_id,))
        cursor.execute(f"DELETE FROM {table[type]} WHERE id = ?", (_id,))
        conn.commit()
    bot.send_message(msg.chat.id, "✅ Deleted succesfully.")