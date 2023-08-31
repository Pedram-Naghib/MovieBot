from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    InlineQuery
)
import glob
import os
from types import SimpleNamespace
from telebot import custom_filters
from telebot.formatting import hbold, hcode, hlink
from src import bot
from telebot.handler_backends import BaseMiddleware, CancelUpdate


# class Middleware(BaseMiddleware):
#     def __init__(self):
#         self.update_types = ['message']
#     def pre_process(self, message, data):
#         pass
#     def post_process(self, message: Message, data, exception=None):
#         pass


def keyboard(keys, row_width=3, resize_keyboard=True):
    markup = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=resize_keyboard)
    buttons = map(KeyboardButton, keys)
    markup.add(*buttons)

    return markup


keys = SimpleNamespace(
    cancel="/cancel",
    done="/done",
)
keyboards = SimpleNamespace(
    cancel=keyboard([keys.cancel]),
    done=keyboard([keys.done]),
)
# meme=keyboard([keys.meme]))

def proc_keys(chatid, vidid, msgid):
    keyboard = {'Process': f'Process {vidid}', 'Link': f'Link {vidid}',
            'Audio 🎵': f'Audio {vidid}', '❌': f'Cancel {vidid}'}
    bot.edit_message_reply_markup(chatid, msgid,
    reply_markup=inline_markup(keyboard, 2))

    
def tags_keys(cdata, back=True):
    mydict = {'#Thot': f'#Thot{cdata}', '#Cosplay': f'#Cosplay{cdata}', '#Nude': f'#Nude{cdata}',
        '#Milf': f'#Milf{cdata}', '#Gymgirl': f'#Gymgirl{cdata}', '#Goth': f'#Goth{cdata}'}
    if back:
        mydict.update({'⬅️': f'Back{cdata}'})
        return mydict
    return mydict
    

def inline_markup(keys, row_width=3):
    buttons = []
    markup = InlineKeyboardMarkup(row_width=row_width)
    for key, value in keys.items():
        button = InlineKeyboardButton(key, callback_data=value)
        buttons.append(button)
    markup.add(*buttons)

    return markup


def inline_url(keys, row_width=1):
    buttons = []
    markup = InlineKeyboardMarkup(row_width=row_width)
    for i in keys.items():
        button = InlineKeyboardButton(i[0], i[1])
        buttons.append(button)
    markup.add(*buttons)

    return markup


def clean_folder(msg_id=None):
    files = glob.glob("./media/*")
    if msg_id == None:
        for f in files:
            os.remove(f)
    elif type(msg_id) == list:
        print(f"files: {list(files)}\npostids: {msg_id}")
        for f in files:
            for i in msg_id:
                if str(i) in f:
                    print(f"found {i} in {f}")
                    os.remove(f)
    else:
        for f in files:
            if str(msg_id) in f:
                os.remove(f)
    return None


def echo(msg):
    pass


help = '''

'''


def movie_data(title, _id, rating, runtime, year, genre, plot, dirs, writers, actors):
    rate, voters = rating.split(' ')
    genre_lis = genre.split(', ')
    genres = ''
    for gnre in genre_lis:
        genres += f'#{gnre} '
    return f"""
{hbold('Title')}: {hlink(title, f'https://www.imdb.com/title/{_id}')}
{hbold('Rating')} ⭐️: {rate} / 10 (based on {voters} user ratings)
{hbold('Duration')}: {runtime}
{hbold('Release year')}: {year}
{hbold('Genre')}: {genres}
{hbold('Plot')}: {plot}
{hbold('Directors')}: {dirs}
{hbold('Writers')}: {writers}
{hbold('Stars')}: {actors}
    """

AWARDS = {'Sundance Film Festival': 'SFF', 'Toronto International Film Festival': 'TIFF', 'Cannes Film Festival': 'Cannes',
          'Berlin International Film Festival': 'Berlinale', 'San Sebastián International Film Festival': 'SanSebastián',
          'Moscow International Film Festival': 'MoscowIFF', 'Melbourne International Film Festival': 'MIFF',
          'International Film Festival Rotterdam': 'IFFR', 'Venice Film Festival': 'Venice',
          'Tallinn Black Nights Film Festival': 'PÖFF', 'International Documentary FilmFestival Amsterdam': 'IDFA',
          'San Francisco International Film Festival': 'SFIFF', 'New York Film Festival': 'NYFF',
          'Indie Memphis Film Festival': 'IndieMemphis', 'Locarno International Film Festival': 'Locarno',
          'Thessaloniki Film Festival': 'TFF', 'Thessaloniki Documentary Festival': 'TDF',
          'Karlovy Vary International Film Festival': 'KVIFF', 'Riga International Film Festival': 'RIFF',
          'Vienna International Film Festival': 'Viennale', 'Zurich Film Festival': 'ZFF',
          'Mar del Plata International Film Festival': 'MdPIFF', 'David di Donatello Awards': 'DaviddiDonatello',
          'Vancouver International Film Festival': 'VIFF', 'Cairo International Film Festival': 'CIFF',
          'Faro Island Film Festival': 'FIFF', 'Shanghai International Film Festival': 'SIFF'}



from telebot.handler_backends import State, StatesGroup


class MyStates(StatesGroup):
    file_imdb_id = State()
    confirmation = State()
    series = State()
    movie = State()
    file = State()


bot.add_custom_filter(custom_filters.StateFilter(bot))

    
    
def is_channel_member(user_id):
    try:
        join = bot.get_chat_member(-1001752415662, int(user_id))
    except Exception as e:
        if "user not found" in str(e):
            return False

    if (join.status == "kicked") or (join.status == "left"):
        return False
    return True


USER_DATA = {}


def media_markup(movieid, type, userid):
    markup = {'📥 Download': f'dl {movieid} {type}'}
    if userid in ADMINS:
        markup['📝 Edit'], markup['🗑 Del Files'] = f'ed {movieid} {type}', f'delf {movieid} {type}'
        markup['🗑 Del All'] = f'dela {movieid} {type}'
    return markup


#* -------------------------------------------------------------------------------------------------------------
#* custom filters

#          pedram      Dan     Kariminia   Antony     Behnam       Tree        Saeed      Peyman
ADMINS = 247768888, 713105930, 388889006, 105836127, 725782668, 5612476807, 2056384239, 2056384239,


class IsAdmin(custom_filters.SimpleCustomFilter):
    key='bot_admin'
    @staticmethod
    def check(message: Message):
        return message.chat.id in ADMINS


class IsVIP(custom_filters.SimpleCustomFilter):
    key='bot_vip'
    @staticmethod
    def check(inline_query: InlineQuery):
        return inline_query.from_user.id in ADMINS #ToDO: in vips not in admins


bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(IsVIP())

# bot.setup_middleware(Middleware())