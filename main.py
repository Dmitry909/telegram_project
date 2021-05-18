from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import csv

TOKEN = '1237986641:AAGSG9tz7Fefs_1Rua0U-jN2NmNxz78oY4E'

users = dict()
username_by_id = dict()
id_by_username = dict()
main_markup = ReplyKeyboardMarkup([['/stat', '/help', '/history']], one_time_keyboard=True)


class User:
    def __init__(self):
        self.numb_of_textes = 0
        self.numb_of_photos = 0
        self.size_of_textes = 0


def add_new_user(chat, user):
    chat_id = chat.id
    user_id = user.id
    username = user.username
    username_by_id[user_id] = username
    id_by_username[username] = user_id
    if chat_id not in users:
        users[chat_id] = dict()
    if user_id not in users[chat_id]:
        users[chat_id][user_id] = User()


def text_processor(update, context):
    text = update.message.text
    chat = update.message.chat
    user = update.message.from_user
    add_new_user(chat, user)
    users[chat.id][user.id].numb_of_textes += 1
    users[chat.id][user.id].size_of_textes += len(text)


def photo_processor(update, context):
    chat = update.message.chat
    user = update.message.from_user
    add_new_user(chat, user)
    user[chat.id][user.id].numb_of_photos += 1


def start(update, context):
    update.message.reply_text(
        "Привет! Я статистик-бот. По вашим запросам я буду выдавать различную статистику этого чата",
        reply_markup=main_markup)


def help(update, context):
    update.message.reply_text(
        "Для получения меню команд отправьте /start")


def history(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    update.message.reply_text(' '.join(text_messages[chat_id][user_id]))


def diagramm(data_names, data_values):
    dpi = 80
    fig = plt.figure(dpi=dpi, figsize=(512 / dpi, 384 / dpi))
    mpl.rcParams.update({'font.size': 9})

    plt.title('Соотношение сообщений')

    xs = range(len(data_names))

    plt.pie(
        data_values, autopct='%.1f', radius=1.1,
        explode=[0 for i in range(len(data_names))])
    plt.legend(
        bbox_to_anchor=(-0.16, 0.45, 0.25, 0.25),
        loc='lower left', labels=data_names)
    fig.savefig('pie.png')


def messages_by_users(update, context):
    chat_id = update.message.chat.id
    search = []
    do_not_search = []
    ans = ''
    if len(context.args) == 0:
        for user_id in users[chat_id]:
            search.append([users[chat_id][user_id].numb_of_textes, username_by_id[user_id]])
        ans = 'Количество сообщений от каждого участника:\n'
    else:
        for i in context.args:
            s = str(i)
            if s[0] == '@':
                s = str(s[1::])
            if s in id_by_username and id_by_username[s] in users[chat_id]:
                user_id = id_by_username[s]
                search.append([users[chat_id][user_id].numb_of_textes, username_by_id[user_id]])
            else:
                do_not_search.append('@' + s)
        if len(search) != 0:
            ans = 'Количество сообщений от каждого указанного участника:\n'
    if len(search) != 0:
        search.sort(reverse=True)
        s = []
        names = []
        values = []
        for i in search:
            s.append(''.join(['@', i[1], ': ', str(i[0])]))
            names.append('@' + i[1])
            values.append(i[0])
        if len(search) > 1:
            diagramm(names, values)
            messages_by_users_image(update, context)
        ans += '\n'.join(s)
    else:
        ans += "Не был найден ни один участник из указанных выше"
        update.message.reply_text(ans)
        return
    if len(do_not_search) != 0:
        ans += "\nНайдены не были следующие участники:\n"
        ans += '\n'.join(do_not_search)
    update.message.reply_text(ans)


def messages_by_users_image(update, context):
    doc = open('pie.png', 'rb')
    caption = "Статистика"
    context.bot.send_photo(update.message.chat.id, doc, caption)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("history", history))
    dp.add_handler(CommandHandler("stat", messages_by_users))

    text_handler = MessageHandler(Filters.text, text_processor)
    dp.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
