from django.core.management.base import BaseCommand
from django.conf import settings
from django.http import request
from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler, CommandHandler
from telegram.ext import Updater
from telegram.utils.request import Request

from base.models import Room
from base.models import User, Telegram
from studybud_my.settings import TG_TOKEN

def key(update: Updater, context: CallbackContext):
    id = update.message.chat_id
    text = update.message.text
    key = text[5:]
    out = ''
    try:
        obj = Telegram.objects.get(key= key)
        
        if obj.authorised_flag:
            out = 'you already authorized'
        else:
            obj.authorised_flag = True
            obj.chat_id = id
            obj.save()
            out = 'Authorized'
    except:
        out = 'key not found, try again'

    update.message.reply_text(
        text = out
    )


def info(update: Updater, context: CallbackContext):
     id = update.message.chat_id
     out = ""
     try:
         obj = Telegram.objects.get(chat_id = id)
        
         if obj.authorised_flag:
             rooms = Room.objects.filter(participants = obj.user)
             if(len(rooms) == 0):
                update.message.reply_text(text = "Список отслеживаемых акций пуст, добавьте их на сайте")
                return
             print(rooms)
             for room in rooms:
                 out = "📈" + (f'Акция: {room.name} ({room.stock})\n\n' + f'Прогноз:\n' + f'\t\t🔮на 5 дней: {room.pred_5_days}\n' 
                 + f'\t\t🔮на 20 дней: {room.pred_20_days}\n\n' + f'Новости:\n' + f'\t\t😊позитивные: {room.pos}\n' 
                 + f'\t\t😞негативные: {room.neg}\n\n' +  f'Рекомендации:\n' + f'\t\t➕покупать: {room.rec_buy}\n' 
                  + f'\t\t⚖️держать: {room.rec_hold}\n' + f'\t\t➖продавать: {room.rec_sell}\n')
                 update.message.reply_text(text = out)
             return
         else:
             out = 'Please, authorise first'
    
     except Exception as ex:
         print(ex)
    
     update.message.reply_text(
         text = out
     )



def authenticate(update: Updater, context: CallbackContext):
    id = update.message.chat_id
    obj = Telegram.objects.get(chat_id = id)
    if obj.authorised_flag:
             obj.authorised_flag = False
             obj.save()
    update.message.reply_text(
        text = 'Введите уникальный ключ:'
    )

class Command(BaseCommand):
    help = 'Telegram Bot'
    
    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout= 1.0
                    )
        bot = Bot(
            request=request,
            token=TG_TOKEN
        )
        updater = Updater(
            bot = bot,
            use_context=True
        )

        message_handler = CommandHandler('key', key)
        updater.dispatcher.add_handler(message_handler)
        
        message_handler_2 = CommandHandler('start', authenticate)
        updater.dispatcher.add_handler(message_handler_2)

        message_handler_3 = CommandHandler('info', info)
        updater.dispatcher.add_handler(message_handler_3)


        updater.start_polling()
        updater.idle()