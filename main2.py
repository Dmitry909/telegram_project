from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import csv

TOKEN = '1237986641:AAGSG9tz7Fefs_1Rua0U-jN2NmNxz78oY4E'

dic = dict()
username_by_id = dict()


def text_processor(update, context):
    text = update.message.text
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    if chat_id in dic and user_id in dic[chat_id]:
        dic[chat_id][user_id].append(text)
    else:
        if chat_id not in dic:
            dic[chat_id] = dict()
        dic[chat_id][user_id] = [text]
        username_by_id[user_id] = username


def start(update, context):
    update.message.reply_text(
        "Привет! Я статистик-бот. По вашим запросам я буду выдавать различную статистику этого чата")


def help(update, context):
    update.message.reply_text(
        "Для получения меню команд отправьте /stat")


def history(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    update.message.reply_text(' '.join(dic[chat_id][user_id]))


def diagramm(data_names, data_values):
    dpi = 80
    fig = plt.figure(dpi=dpi, figsize=(512 / dpi, 384 / dpi))
    mpl.rcParams.update({'font.size': 9})

    plt.title('Stat')

    xs = range(len(data_names))

    plt.pie(
        data_values, autopct='%.1f', radius=1.1,
        explode=[i / 10 for i in range(len(data_names))])
    plt.legend(
        bbox_to_anchor=(-0.16, 0.45, 0.25, 0.25),
        loc='lower left', labels=data_names)
    fig.savefig('pie.png')


def messages_by_users(update, context):
    chat_id = update.message.chat.id
    a = []
    for user_id in dic[chat_id]:
        a.append([len(dic[chat_id][user_id]), username_by_id[user_id]])
    print(a)
    a.sort(reverse=True)
    ans = 'Количество сообщений от каждого участника:\n'
    s = []
    names = []
    values = []
    for i in a:
        s.append(''.join(['@', i[1], ': ', str(i[0])]))
        names.append('@' + i[1])
        values.append(i[0])
    diagramm(names, values)
    messages_by_users_image(update, context)
    ans += '\n'.join(s)
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
