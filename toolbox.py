import json
import sys
import os
#import sqlite3
from datetime import datetime, timedelta
import sqlite_handler as sql

import config
import tg

boot_time=datetime.now()


def debug(text):
    if config.verbose:
        print(text)

def count_away_users(amount):
    if amount==1:
        return("\n\n1 user away.")
    else:
        return("\n\n"+str(amount)+" users away.")

def seconds_to_string(i, include_seconds=True, longform=True):
    if type(i)==timedelta:
        duration=round(i.total_seconds())
    elif type(i)==int:
        duration=i
    elif type(i)==float:
        duration=round(i)

    outputlist=[]
    output=""
    hours = duration//3600
    minutes = (duration%3600)//60
    seconds = duration%60
    elements = []


    if not include_seconds:
        seconds = 0

    if longform: #probably should break this out into a method idk
        if hours == 1:
            elements.append('1 hora')
        elif hours != 0:
            elements.append(str(hours)+' horas')

        if minutes == 1:
            elements.append('1 minuto')
        elif minutes != 0:
            elements.append(str(minutes)+' minutos')

        if seconds == 1:
            elements.append('1 segundo')
        elif seconds != 0:
            elements.append(str(seconds)+' segundos')


        if len(elements) == 3:
            output = (elements[0]+', '+
                     elements[1]+' y '+
                     elements[2]
                     )
        elif len(elements) == 2:
            output = (elements[0]+' y '+
                     elements[1]
                     )

        elif len(elements) == 1:
            output = elements[0]

        else:
            notify_owner('something went wrong: len(elements) == '+
                         len(elements)+
                         "\n"+
                         '\nhours='+str(hours)+
                         '\nminutes='+str(minutes)+
                         '\nseconds='+str(seconds)
                         )
    else:
        if hours != 0:
            output += str(hours)+"h"
        if minutes != 0:
            output += str(minutes)+"m"
        if seconds != 0:
            output += str(seconds)+"s"

    return(output)

#takes a list of user dicts such as those provided by the sql.db.get_help_users function
def list_users(id_list, mention=True): #db'd
    output=""
    for i in id_list:
        output += list_user(i, mention=mention)
        output+="\n"
    return(output)


#takes a user ID as a string
def list_user(user_id,mention=True):
    output=""
    user_name = sql.db.get_user(user_id)[0]['name']
    try:
        if mention:
            output+="["+user_name+"](tg://user?id="+str(user_id)+")"
        else:
            output = output + user_name
    except IndexError:
        return("unrecognized id: "+str(user_id))
    return(output)

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def user_is_in_group_or_admin(group, user):
    if group in config.approved_groups:
        return(True)
    elif user in config.admins:
        return(True)
    else:
        return(False)

def user_is_admin(user):
    if user in config.admins:
        return(True)
    else:
        return(False)

def load_json(file):
    with open(file+'.json') as f:
        data=json.load(f)
    return(data)

def save_json(file,data):
    with open(file+'.json','w') as f:
        json.dump(data,f)
    return()



def register_user(update, context): #db'd
    """add user from a json string sent by the user"""
    #todo: allow using ini syntax (plaintext with equal sign or colon)

    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_admin(user_id):
        return()
    data=remove_prefix(update.message.text, "/register_user")
    resultlist=sql.db.register_user(data)
    if len(resultlist)==1:
        result=resultlist[0]
    else:
        raise(Exception("tried to register one user and got several results back"))
    output="Added the following user:\n\n"
    for key, value in result.items():
        output+="*"+str(key)+"*: "+str(value)+"\n"
    context.bot.send_message(chat_id=chat_id, text=output.replace("_"," "), parse_mode='Markdown')
    return()






def vozdivina(update,context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_admin(user_id):
        return()
    new_message=remove_prefix(update.message.text,"/vozdivina")
    keyboard = [[telegram.InlineKeyboardButton("ok", callback_data="DELETETHIS")]]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=config.ponche_group, text=new_message, reply_markup=reply_markup)
    return()

def voztesting(update,context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_admin(user_id):
        return()
    new_message=remove_prefix(update.message.text,"/voztesting ")
    context.bot.send_message(chat_id=config.ponche_group, text=new_message, reply_markup=reply_markup)
    return()

def vozpueblo(update,context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_admin(user_id):
        return()
    new_message=remove_prefix(update.message.text,"/vozpueblo ")
    new_entities=update.message.parse_entities()
    current_offset=0
    message_with_entities=""
    for i in new_entities:
        if i.user==None:
            pass
        else:
            true_offset=i.offset-len('/vozpueblo ')
            message_with_entities=message_with_entities+new_message[current_offset:true_offset]+\
                        "["+new_message[true_offset:true_offset+i.length]+"](tg://user?id="\
                        +str(i.user['id'])+")"
            current_offset=true_offset+i.length
            print(i.user)
            print(i.offset)
            print(i.length)
            print(true_offset)
            print(message_with_entities)
    message_with_entities+=new_message[current_offset:]


    context.bot.send_message(chat_id=config.ponche_group, text=message_with_entities, entities=new_entities, parse_mode='Markdown')
    return()

def pingall(update, context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_admin(user_id):
        return()
    context.bot.send_message(chat_id=chat_id, text=list_users(config.all_users.keys() ,config.all_users), parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)












def ping(update,context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_in_group_or_admin(chat_id, user_id):
        return()
    context.bot.send_message(chat_id=chat_id, text="pong", parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)
    
def reboot(update,context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_in_group_or_admin(chat_id, user_id):
        return()
    context.bot.send_message(chat_id=chat_id, text="rebooting...", parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)
    sys.stdout.flush() 
    os.execv(sys.argv[0],[sys.argv[0],str(chat_id)])

def uptime(update,context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_in_group_or_admin(chat_id, user_id):
        return()
    now=datetime.now()
    output="Bot has been up for "+seconds_to_string(now-boot_time)
    output+=", since "+boot_time.strftime("%Y-%m-%d %H:%M:%S")
    context.bot.send_message(chat_id=chat_id, text=output, parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)
    return()

def notify_owner(message):
    tg.updater.bot.send_message(chat_id=config.main_admin, text=message)
    return()

def test(update, context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not user_is_admin(user_id):
        return()
    command=remove_prefix(update.message.text, '/test ')
    exec(command)
    return()
