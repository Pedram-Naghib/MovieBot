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
    ok="/ok",
    finish="/finish",
    award="🏅جشنواره",
    contact="📞 تماس با ما",
    update="🔄 به روز رسانی",
    vip="⭐️ خرید اشتراک",
)
keyboards = SimpleNamespace(
    cancel=keyboard([keys.cancel]),
    done=keyboard([keys.done]),
    ok=keyboard([keys.ok]),
    finish=keyboard([keys.finish]),
    home=keyboard([keys.award, keys.contact, keys.update, keys.vip]),
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
    welcome =  """
✨ به Cinema Dreaming خوش اومدید.

▪️ با تهیهٔ اشتراک از ربات ما، آرشیوی کامل از فیلم‌‌های مهم تاریخ سینما، جشنواره‌های بزرگ دنیا و آثار کمتردیده‌شده در اختیارتون قرار می‌گیره.

⚪️ @CinemDreaming
"""
    bot.send_message(msg.chat.id, welcome, reply_markup=keyboards.home)


help = '''

'''

del_help = """Correct use is /del value. value can be one of below:

cd: to delete from disc table.
extra: to delete from extra table.
episode: to delete a series epsoide.
file: to delete a movie file.

example: /del file
"""

del_step1 = """
Send ImdbID and name of the file to be deleted in 2 lines. example:

tt13845660
WEB-DL 1080p HMAX playWEB
(if it is series write season and episode number in S01.E05 format)
"""

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
    contact = State()
    award = State()
    cd_extra = State()
    cd_extra_confirm = State()
    delete = State()
    del_conf = State()


bot.add_custom_filter(custom_filters.StateFilter(bot))

    
    
def is_channel_member(user_id):
    joined_all = False
    for channel in [-1001461305849, -1001914164671]:
        try:
            join = bot.get_chat_member(channel, int(user_id))
        except Exception as e:
            if "user not found" in str(e):
                return False
            elif "chat not found" in str(e):
                return bot.send_message(247768888, '💩 Bot is not admin in the channel!')

        if (join.status == "kicked") or (join.status == "left"):
            return False
        else:
            joined_all = True
    return joined_all


USER_DATA = {}


def media_markup(movieid, type, userid, cd_extra):
    word = 'dl' if type == 'movie' else 'se'
        
    markup = {'📥 Encodes': f'{word} {movieid} {type}'}
    if cd_extra[0]:
        markup['💿 Disc'] = f'dl {movieid} cd'
    if cd_extra[1]:
        markup['🗂 Extra'] = f'dl {movieid} extra'
    if userid in ADMINS:
        markup['🗑 Delete'] = f'🗑 {movieid} {type}'
    return markup


def season_markup(_id, seasons):
    markup = {}
    for i in seasons:
        markup[f'📂 S{i[0]}'] = f'season {i[0]} {_id}'
    markup[f'⬅️ Back'] = f'back-media series {_id}'
    return markup


def ep_markup(_id, season, eps):
    markup = {}
    for i in eps:
        markup[f'📂 E{i[0]}'] = f'dl {season}.{i[0]} {_id}'
    markup[f'⬅️ Back'] = f'b-s {_id}'
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