import os
from flask import Flask, request
import telebot
from flask_sqlalchemy import SQLAlchemy

token = "1383035947:AAEeeYRAbiN68RCkiqktarp6-7cN1xqH6tA"
DATABASE_URI = 'postgres+psycopg2://idenm:qwerty07@localhost:5432/bot'

server = Flask(__name__)
bot = telebot.TeleBot(token)
server.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(server)
