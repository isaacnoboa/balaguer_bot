from datetime import datetime
import random

import telegram
import tg
import toolbox
import config
import sqlite_handler as sql

ponche_motd ="Pueblo dominicano... hoy es {0}, y es hora de reportarse a sus labores.\n\n"\
             "Bébete tu ponche y poncha para que no te ponchen.\n\nUsuarios:"

def scheduled_punchin(update=None, context=None):
    now=datetime.now()
    if now.hour < 17:
        output="No es como un chin temprano?"
        reply_markup=None
    else:
        daytext=now.strftime("%Y-%m-%d")
        longdaytext=now.strftime("%A %-d de %B del año %Y")
        output=(ponche_motd.format(longdaytext))
        keyboard = [[telegram.InlineKeyboardButton("👊 Poncha 🍷", callback_data=daytext)]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        users_who_work_today = sql.db.get_users_who_work_today(now)
        random.shuffle(users_who_work_today)
        output+= "\n"
        for i in users_who_work_today:
            output+= "\n🕟 "
            output += toolbox.list_user(i['user_id'], mention=False)
    tg.updater.bot.send_message(chat_id=config.ponche_group, text=output, reply_markup=reply_markup)#chat id is the destroyers group
    return()

def punchin(update, context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_admin(chat_id, user_id):
        context.bot.send_message(chat_id=chat_id, text="no", parse_mode="Markdown")    
    scheduled_punchin(update, context) 
    return()

def button(update, context):
    # i should probably split this into different functions to make it
    # easier to understand. This can happen along with the raw api
    # rewrite - i'm tired of dealing with the telegram abstractions. 
    
    # some would say that's too much effort, but this is a learning
    # project after all, so if i'm gonna learn about webhooks i gotta
    # learn the right way. 





    now=datetime.now()
    daytext=now.strftime("%Y-%m-%d")
    longdaytext=now.strftime("%A %-d de %B del año %Y")
    message_data=update.callback_query.data
    user_id=update.callback_query.from_user.id
    reply_markup = update.callback_query.message.reply_markup
    query_id=update.callback_query.id
    output=ponche_motd.format(longdaytext)+"\n"



    
    if "🥚" in message_data:
        current_eggs = int(update.callback_query.message.text.split(" ")[0])
        if "+" in message_data:
            new_eggs = current_eggs+1
        elif "-" in message_data:
            new_eggs = current_eggs-1
        else:
            print("bruh")
            return()

        if new_eggs == 1:
            output="1 huevo."
        else:
            output=str(new_eggs)+" huevos."
        context.bot.answer_callback_query(query_id)
        update.callback_query.edit_message_text(text=output,reply_markup=reply_markup)
        return()




    if message_data=="DELETETHIS":
        context.bot.answer_callback_query(query_id,text='no has visto nada')
        context.bot.delete_message(chat_id=update.callback_query.message.chat.id,message_id=update.callback_query.message.message_id)
        return()




    if message_data == daytext:
        if now.hour>=19:
            context.bot.answer_callback_query(query_id,text='tu no estás como tarde o algo así')
            return()


        try:
            sql.db.add_ponched_user(user_id,now.timestamp())
            context.bot.answer_callback_query(query_id, text="welcome to the jungle, LET'S GET READY TO RUMBLE!!!")
        except sql.AlreadyAdded:
            context.bot.answer_callback_query(query_id, text="usted ya está ponchado")
        ponched_users = sql.db.get_ponched_users(now.timestamp())

        ponched_ids=[]
        for i in ponched_users:
            output+= "\n✅ "
            output+=datetime.fromtimestamp(i['timestamp']).strftime("%I:%M:%S %p") + ": "
            output+=toolbox.list_user(i['user_id'], mention=False)
            ponched_ids.append(i['user_id'])

        users_who_work_today = sql.db.get_users_who_work_today(now)
        random.shuffle(users_who_work_today)
        for i in users_who_work_today:
            if i['user_id'] not in ponched_ids:
                output+= "\n🕟 "
                output += toolbox.list_user(i['user_id'], mention=False)

        update.callback_query.edit_message_text(output, reply_markup = reply_markup)
    else:
       update.callback_query.edit_message_text(text=update.callback_query.message.text,reply_markup="")
       context.bot.answer_callback_query(query_id,text='ok')
       return()







