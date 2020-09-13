#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telegram
import schedule 
import sqlite3
import random
import locale
import json
import math
import time
import sys
import os

import config
import toolbox
import ponche
import helpbot
import breaks
import sqlite_handler as sql
import tg

from datetime import datetime, timedelta


import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)


locale.setlocale(locale.LC_TIME, "es_DO.utf-8") 


#TODO: Improve the ponche log format.

#TODO: Make approved groups be an array instead of a list. 

break_users={}
break_alarms={}





def echo(update, context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    text=update.message.text
    # egg counter added 2020-08-05 02:23:36 on a whim
    if "🥚" in text:
        count=text.count("🥚")
        if count==1:
            output="1 huevo."
        else:
            output=str(count)+" huevos."
        keyboard = [[telegram.InlineKeyboardButton("+🥚", callback_data="+🥚"),
                     telegram.InlineKeyboardButton("-🥚", callback_data="-🥚")
                    ]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text=output, reply_markup=reply_markup)
    if "$" in text:
        if user_is_admin(user_id):
            print("\n\nUPDATE:")
            print(str(update))
            print("\n\nCONTEXT:")
            print(str(context))
    return()







def start(update, context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_admin(user_id):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Pueblo dominicano...")
        return()
    if context.args[0]:
        context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0])
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No argument but no exception.")

    print(str(update.effective_chat.id))




#DONE: make the bot send unpinging list when adding/removing people


def sim_action_from_name(name):
    r=random.randrange(5)
    output=""
    if r==0:
        output+="{0} no volvió a su casa anoche.".format(name)
    elif r==1:
        output+="{0} está en la parte de atrás de una camioneta con rumbo desconocido.".format(name)
    elif r==2:
        output+="Cuatro militares entraron a la casa de {0}, y salieron con una bolsa negra.".format(name)
    elif r==3:
        output+="{0} ha cometido suicidio con dos tiros en la espalda.".format(name)
    elif r==4:
        output+="{0} ha recibido un cocotazo.".format(name)
    return(output)

def sim_action_no_name():
    r=random.randrange(5)
    output=""
    if r==0:
        output+="Pero te colgaron."
    elif r==1:
        output+="Se cayó la línea."
    elif r==2:
        output+="Se te acabaron los minutos."
    elif r==3:
        output+="Están de cuarentena."
    elif r==4:
        output+="Se dieron un jumo anoche y siguen durmiendo."
    return(output)


def sim(update, context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_admin(user_id):
        return()
    output="Llamando al SIM....\n\n"
    try:
        name=context.args[0].title()
        output+=sim_action_from_name(name)
    except IndexError:
        try:
            reply_user_id=update.effective_message.reply_to_message.from_user.id #holy mother of objects
            name=toolbox.list_user(reply_user_id,config.all_users,mention=False)
            output=sim_action_from_name(name)
        except AttributeError:
            output+=sim_action_no_name()
    context.bot.send_message(chat_id=chat_id, text=output)












def hack(update, context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_admin(user_id):
        return()
    output="Hackeando....\n\n"
    try:
        name=context.args[0].title()
        output="{0} ha sido hackeado.".format(name)
    except IndexError:
        try:
            reply_user_id=update.effective_message.reply_to_message.from_user.id #holy mother of objects
            name=toolbox.list_user(reply_user_id,config.all_users,mention=False)
            output="{0} ha sido hackeado.".format(name)
        except AttributeError:
            name=toolbox.list_user(user_id, config.all_users, mention=False)
            output="{0} ha sido hackeado.".format(name)
    context.bot.send_message(chat_id=chat_id, text=output)





tg.dispatcher.add_handler(tg.CommandHandler('start', start)) #allow_edited = false https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.commandhandler.html?highlight=commandhandler#telegram.ext.tg.CommandHandler

tg.dispatcher.add_handler(tg.CommandHandler('voztesting', toolbox.voztesting))
tg.dispatcher.add_handler(tg.CommandHandler('vozdivina', toolbox.vozdivina))
tg.dispatcher.add_handler(tg.CommandHandler('vozpueblo', toolbox.vozpueblo))
tg.dispatcher.add_handler(tg.CommandHandler('pingall', toolbox.pingall))
tg.dispatcher.add_handler(tg.CommandHandler('reboot', toolbox.reboot))
tg.dispatcher.add_handler(tg.CommandHandler('uptime', toolbox.uptime))
tg.dispatcher.add_handler(tg.CommandHandler('ping', toolbox.ping))
tg.dispatcher.add_handler(tg.CommandHandler('register_user', toolbox.register_user))

tg.dispatcher.add_handler(tg.CommandHandler('listusers', helpbot.listusers))
tg.dispatcher.add_handler(tg.CommandHandler('addme', helpbot.addme))
tg.dispatcher.add_handler(tg.CommandHandler('removeme', helpbot.removeme))
tg.dispatcher.add_handler(tg.CommandHandler('helpme', helpbot.helpme))
tg.dispatcher.add_handler(tg.CommandHandler('adduser', helpbot.adduser))
tg.dispatcher.add_handler(tg.CommandHandler('removeuser', helpbot.removeuser))

tg.dispatcher.add_handler(tg.CommandHandler('sim', sim))
tg.dispatcher.add_handler(tg.CommandHandler('hack', hack))

tg.dispatcher.add_handler(tg.CommandHandler('break', breaks.taking_break))
tg.dispatcher.add_handler(tg.CommandHandler('lunch', breaks.taking_lunch))
tg.dispatcher.add_handler(tg.CommandHandler('back', breaks.back))
tg.dispatcher.add_handler(tg.CommandHandler('quien', breaks.quien))


tg.dispatcher.add_handler(tg.CommandHandler('test', test))
tg.dispatcher.add_handler(tg.CommandHandler('ponche', ponche.punchin))



tg.dispatcher.add_handler(tg.CallbackQueryHandler(ponche.button))
tg.dispatcher.add_handler(tg.MessageHandler(tg.Filters.text, echo))

























print("Starting balaguer_bot v"+str(config.version))
tg.updater.start_polling()
print("Bot started at "+toolbox.boot_time.strftime("%Y-%m-%d %H:%M:%S"))
breaks.rebuild_schedule()
print("Successfully scheduled the ponche.")

if len(sys.argv)>1:
    tg.updater.bot.send_message(chat_id=sys.argv[1], text='Reboot successful.\n\nStarting balaguer_bot v'+str(config.version))



while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e: #catches everything except keyboard interrupt
        toolbox.notify_owner("got an error: " +repr(e))
