from src import bot, constants, sqldb
from telebot.types import Message, CallbackQuery
from telebot.formatting import hcode, hbold


@bot.message_handler(regexp="🏅جشنواره", chat_types=["private"])
def award_choose(msg):
    awards = dict(sorted(constants.AWARDS.items()))
    markup = {k: f'aw {v}' for k, v in awards.items()}
    markup["❌ Cancel"] = 'cancel'
    bot.send_message(msg.chat.id, "جشنواره ی مورد نظر رو انتخاب کنید:", reply_markup=constants.inline_markup(markup, 1))


@ bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'aw')
def media_suggest(call: CallbackQuery):
    _, award_tag = call.data.split(' ')
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.from_user.id, "سال مورد نظر رو وارد کنید:\nمثال: 2017, 1999, 2000")
    bot.set_state(call.from_user.id, constants.MyStates.award)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['award'] = award_tag


@bot.message_handler(state=constants.MyStates.award)
def find_award_movies(message: Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        award_tag = data['award']
    year = message.text
    titles = sqldb.award_finder(award_tag, year)
    titles = sorted(titles, key=lambda x: (x[1], x[0]))
    if not titles:
        bot.send_message(message.chat.id, f"😕 نتیجه ای با فیلتر های مشخص شده یافت نشد!")
    else:
        result, markup = f"{award_tag} {year}:\n\n", None
        i = 1
        for title, movie_year, id in titles:
            if i == 11:
                markup = constants.inline_markup({'Next ➡️': f'Next {award_tag} {year}'})
                break
            result += f'{hbold(str(i))}. {hcode(title)} {movie_year} /dl_{id}\n'
            i += 1
        bot.send_message(message.chat.id, result, reply_markup=markup)
    bot.delete_state(message.from_user.id, message.chat.id)

    
@ bot.callback_query_handler(func= lambda call: call.data.split(' ')[0] == 'Next')
def lb_next(call: CallbackQuery):
    _, award_tag, year = call.data.split(' ')
    last_ietm = call.message.text.split('\n')[-1]
    last_num = int(last_ietm.split('.')[0])
    titles = sqldb.award_finder(award_tag, year)[last_num:]
    titles = sorted(titles, key=lambda x: (x[1], x[0]))
    result, markup = f"{award_tag} {year}:\n\n", {'⬅️ Prev': f'Previous {award_tag} {year}'}
    i = last_num + 10
    for title, movie_year, id in titles:
        if last_num == i:
            markup['Next ➡️'] = f'Next {award_tag} {year}'
            break
        result += f'{hbold(str(i))}. {hcode(title)} {movie_year} /dl_{id}\n'
        last_num += 1
    bot.edit_message_text(result, call.message.chat.id, call.message.message_id, reply_markup=constants.inline_markup(markup, 2))


@ bot.callback_query_handler(func= lambda call: call.data.split(' ')[0] == 'Previous')
def lb_prev(call: CallbackQuery):
    _, award_tag, year = call.data.split(' ')
    first_item = call.message.text.split('\n')[2]
    first_num = int(first_item.split('.')[0])
    titles = sqldb.award_finder(award_tag, year)[first_num-11: first_num-1]
    titles = sorted(titles, key=lambda x: (x[1], x[0]))
    result, markup = f"{award_tag} {year}:\n\n", {}
    i = first_num - 10
    if i > 10:
        markup['⬅️ Prev'] = f'Previous {award_tag} {year}'
    markup['Next ➡️'] = f'Next {award_tag} {year}'
    for title, movie_year, id in titles:
        if first_num == i:
            break
        result += f'{hbold(str(i))}. {hcode(title)} {movie_year} /dl_{id}\n'
        i += 1
    bot.edit_message_text(result, call.message.chat.id, call.message.message_id, reply_markup=constants.inline_markup(markup, 2))


@bot.message_handler(regexp="📞 تماس با ما", chat_types=["private"])
def contact_us(msg):
    bot.send_message(msg.chat.id, "لطفا مسیج خود را ارسال کنید 👇")
    bot.set_state(msg.from_user.id, constants.MyStates.contact)


@bot.message_handler(state=constants.MyStates.contact)
def contact(message: Message):
    admins_id = -1001475842256
    user = message.from_user
    text = f"first name: {user.first_name}\nlast name: {user.last_name}\nusername: @{user.username}\n\n\nmessage:\n{message.text}"
    bot.send_message(admins_id, text)
    bot.send_message(message.chat.id, "مسیج شما ارسال شد 👍")
    bot.delete_state(user.id, message.chat.id)


@bot.message_handler(regexp="🔄 به روز رسانی", chat_types=["private"])
def updates(msg):
    updates = print_updates()
    bot.send_message(msg.chat.id, updates)


def print_updates(display=True):
    updates = ''
    with open('log.txt', 'r') as f:
        data = f.readlines()
        rss = data[::-1][:20]
    for i in rss:
        i = i.rstrip('\n')
        if i not in updates and len(i) > 3:
            updates += f'{i}\n'
            if display:
                print(display)
                updates += f'➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖\n'
    if display:
        updates += "\n🔄این لیست شامل آخرین فیلم و سریال های بروز شده در ربات است. (شامل عناوین جدید و قدیمی)"
    return updates


@bot.message_handler(regexp="⭐️ خرید اشتراک", chat_types=["private"])
def become_vip(msg):
    pass

