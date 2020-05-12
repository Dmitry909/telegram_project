# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler

TOKEN = '1237986641:AAGSG9tz7Fefs_1Rua0U-jN2NmNxz78oY4E'

dic = dict()
username_by_id = dict()


def echo(update, context):
    chat = update.message.chat
    text = update.message.text
    from_user = update.message.from_user
    chat_id = chat.id
    user_id = from_user.id
    username = from_user.username
    if chat_id in dic and user_id in dic[chat_id]:
        dic[chat_id][user_id].append(text)
    else:
        if chat_id not in dic:
            dic[chat_id] = dict()
        dic[chat_id][user_id] = [text]
        username_by_id[user_id] = username
    #update.message.reply_text(text)


def start(update, context):
    update.message.reply_text(
        "Привет! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!")


def help(update, context):
    update.message.reply_text(
        "Я пока не умею помогать... Я только ваше эхо.")


def history(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    print(dic)
    update.message.reply_text(' '.join(dic[chat_id][user_id]))


def stat(update, context):
    chat_id = update.message.chat.id
    a = []
    for user_id in dic[chat_id]:
        a.append([len(dic[chat_id][user_id]), username_by_id[user_id]])
    print(a)
    a.sort()
    a.reverse()
    ans = 'Количество сообщений от каждого участника:\n'
    s = []
    for i in a:
        q = '@'
        q += i[1]
        q += ': '
        q += str(i[0])
        s.append(q)
    ans += '\n'.join(s)
    update.message.reply_text(ans)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("history", history))
    dp.add_handler(CommandHandler("stat", stat))

    text_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
