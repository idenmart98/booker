import os
import random
import telebot
from flask import request
from telebot.types import ReplyKeyboardMarkup
from sqlalchemy import tuple_


import config
from models import Category, Count, User


server = config.server
bot = config.bot
db = config.db


def delete_history(message):
    Count.query.filter_by(user=message.from_user.id).delete()
    db.session.commit()
    bot.send_message(message.chat.id, "Очищено")


def create_user(id, username):
    users_ids = [i.id for i in User.query.all()]
    if id not in users_ids:
        user = User(id=id, username=username)
        db.session.add(user)
        db.session.commit()


def get_sum_category(id, user_id):
    return sum([i.summa for i in Count.query.filter_by(category=id, user=user_id)])


def create_id():
    id = random.choice(range(10000000))
    if id not in [i.id for i in Count.query.all()]:
        return id
    return create_id


@server.route("/", methods=["POST"])
def receive_update():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return {"ok": True}


inits = ["F", "I", "S"]


main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
main_markup.add("Добавить")
main_markup.add("Отчет")
main_markup.add("Очистить")

choise = """Выберите категорию \'F\' если еда \'I\' если развлечения и \'S\' если учеба"""



@bot.message_handler(commands=['help', 'start'])
def answer(message):
    create_user(
        message.from_user.id, 
        message.from_user.username)
    bot.send_message(message.chat.id, "Здраствуй друг", reply_markup = main_markup)


categorys_ids = {'F': 4, 'I': 5, 'S': 6}


def add_summ(message):
    count = Count(
        id=create_id(), 
        summa=int(message.text[2:]), 
        category=categorys_ids[message.text[0]], 
        user=message.from_user.id)
    db.session.add(count)
    db.session.commit()
    bot.send_message(message.chat.id, "Добавлено")


def get_sum(message):
    food = get_sum_category(4, message.from_user.id)
    game = get_sum_category(5, message.from_user.id)
    study = get_sum_category(6, message.from_user.id)
    text = f"""еда:{food} развлечения: {game} study: {study}"""
    bot.send_message(message.chat.id, text)
    

@bot.message_handler(content_types=["text"])
def answer(message):
    if message.text == "Добавить":
        bot.send_message(message.chat.id, choise)
    elif message.text[0] in inits:
        add_summ(message)
    elif message.text == "Отчет":
        get_sum(message)
    elif message.text == "Очистить":
        delete_history(message)
    else:
        bot.send_message(message.chat.id, message.text)


@server.route('/' + config.token, methods=['POST'])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(
            request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    s = bot.set_webhook(
        url='https://6489843bfcdf.ngrok.io' + config.token)
    if s:
        return print("webhook setup ok")
    else:
        return print("webhook setup failed")


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
