from telegram import ForceReply, Update
# from telegram.ext import Updater, MessageHandler, Filters
# from telegram.ext import CallbackContext, CommandHandler
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import csv

TOKEN = '5937916941:AAG3x4o-lWgr5NJPE704U7dqxawZyB9F9eI'

variables = ["texts", "length", "photos"]
users = dict()
username_by_id = dict()
id_by_username = dict()


class User:
    def __init__(self):
        self.count = {variables[0] : 0, variables[1] : 0, variables[2] : 0}


def add_new_user(update, context):
    text = update.message.text
    chat = update.message.chat
    user = update.message.from_user
    chat_id = chat.id
    user_id = user.id
    username = user.username
    username_by_id[user_id] = username
    id_by_username[username] = user_id
    if chat_id not in users:
        users[chat_id] = dict()
    if user_id not in users[chat_id]:
        users[chat_id][user_id] = User()


def add_text_message(update, context):
    add_new_user(update, context)
    text = update.message.text
    chat = update.message.chat
    user = update.message.from_user
    users[chat.id][user.id].count["texts"] += 1
    users[chat.id][user.id].count["length"] += len(text)


async def text_processor(update, context):
    add_text_message(update, context)


async def photo_processor(update, context):
    add_new_user(update, context)
    text = update.message.text
    chat = update.message.chat
    user = update.message.from_user
    users[chat.id][user.id].count["photos"] += 1
    if text is not None:
        users[chat.id][user.id].count["length"] += len(text)


async def start(update, context):
    add_text_message(update, context)
    await update.message.reply_text(
        "Привет! Я статистик-бот. По вашим запросам я буду выдавать различную статистику этого чата. "
        "Чтобы показать список моих команд, отправьте /help")


async def help(update, context):
    add_text_message(update, context)
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start : приветственное сообщение\n"
        "/help : помощь\n"
        "/stats : статистика по кол-ву отправленных сообщений всех участников чата\n"
        "/stats [@vasya @masha ...] : только по заданным пользователям\n"
        "/stats [texts length photos] : выбор параметров"
        "/stats [texts length photos] [@vasya @masha ...] : комбинированные параметры\n"
        "/hello приветствие"
        "/bye прощание")

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


async def messages_by_users(update, context):
    add_text_message(update, context)
    chat_id = update.message.chat.id
    search = []
    do_not_search = []
    ans = ''

    string_args = [str(s) for s in context.args]
    current_vars = list(filter(lambda x : x in string_args, variables))
    if len(current_vars) == 0:
        current_vars = ['texts', 'photos']
    string_args = list(filter(lambda x : x not in variables, string_args))

    if len(string_args) == 0:
        string_args = ['@' + username_by_id[user_id] for user_id in users[chat_id]]
    for s in string_args:
        if s[0] != '@':
            await update.message.reply_text('Аргумент {} не поддерживается'.format(s))
            return
        s = str(s[1::])
        if s in id_by_username and id_by_username[s] in users[chat_id]:
            user_id = id_by_username[s]
            count = 0
            for var in current_vars:
                count += users[chat_id][user_id].count[var]
            search.append([count, username_by_id[user_id]])
        else:
            do_not_search.append('@' + s)
    if len(search) != 0:
        ans = 'Статистика по всем указанным участникам:\n'
    if len(search) != 0:
        search.sort(reverse=True)
        s = []
        names = []
        values = []
        for i in search:
            s.append(''.join(['@', i[1], ': ', str(i[0])]))
            names.append('@' + i[1])
            values.append(i[0])
        diagramm(names, values)
        await messages_by_users_image(update, context)
        ans += '\n'.join(s)
    else:
        ans += "Не был найден ни один участник из указанных выше"
        await update.message.reply_text(ans)
        return
    if len(do_not_search) != 0:
        ans += "\nНайдены не были следующие участники:\n"
        ans += '\n'.join(do_not_search)
    await update.message.reply_text(ans)


async def messages_by_users_image(update, context):
    doc = open('pie.png', 'rb')
    caption = "Статистика"
    await context.bot.send_photo(update.message.chat.id, doc, caption)


async def hellooo(update, context):
    await update.message.reply_text("Hello!")


async def byebye(update, context):
    await update.message.reply_text("Bye!")


def main():
    file = open('token.txt', 'r')
    token = file.readlines()[0]
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("stats", messages_by_users))
    application.add_handler(CommandHandler("hello", hellooo))
    application.add_handler(CommandHandler("bye", byebye))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_processor))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, photo_processor))

    application.run_polling()


if __name__ == '__main__':
    main()
