import tg 
import sqlite_handler as sql
import ponche
import toolbox
from datetime import datetime, timedelta
import schedule 

def rebuild_schedule():
    schedule.clear()
    #first the ponche lol
    schedule.every().day.at("17:15").do(ponche.scheduled_punchin)
    #then get every pending break
    current_breaks=sql.db.get_current_breaks()
    for i in current_breaks: #calculate how many mins left on each event
        now=datetime.now().timestamp()
        elapsed_time=now-i['start_time']
        expected_seconds=i['expected_length']*60
        next_alarm_in=expected_seconds-(elapsed_time % expected_seconds)
        schedule.every(next_alarm_in).seconds.do(alarm,i)
    return()

def break_duration_calculator(expected_length):
    if expected_length == 30:
        break_type="lunch"
    elif expected_length == 15:
        break_type="break"
    elif expected_length == 1:
        break_type="break (1 minuto)"
    else:
        break_type="break ("+str(expected_length)+" minutos)"
    return(break_type)

def taking_break(update, context, lunch=False):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_in_group_or_admin(chat_id, user_id):
        return()
    timestamp=datetime.now().timestamp()
    
    break_users=sql.db.get_current_breaks()
    
    toolbox.debug(break_users)
    username = toolbox.list_user(user_id, mention=False)

    try:
        expected_length=int(context.args[0])
    except:
        expected_length=15

    if lunch:
        expected_length=30


    for i in break_users:
        if i['user_id'] == user_id:
            break_type=break_duration_calculator(i['expected_length'])
            output=username+" ya está de "+break_type+" desde las "+\
                   datetime.fromtimestamp(i['start_time']).strftime("%H:%M:%S")
            output+=toolbox.count_away_users(len(break_users))
            context.bot.send_message(chat_id=chat_id, text=output, parse_mode="Markdown")
            return()

    else:# yo this was an accident but apparently you can have an else after a for loop? wtf
        break_type=break_duration_calculator(expected_length)
        sql.db.send_user_away(user_id=user_id,
                              timestamp=timestamp,
                              expected_length=expected_length,
                              alarm_channel=chat_id,
                              )
        output=username+" se ha ido de "+break_type+" a las "+\
                        datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

    output+=toolbox.count_away_users(len(break_users)+1) #break user was only updated _before_ adding the current user.
    context.bot.send_message(chat_id=chat_id, text=output, parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)
    
    rebuild_schedule()    
    return()


def taking_lunch(update, context): 
    taking_break(update, context, lunch=True)
    return


def alarm(break_data):
    now=datetime.now().timestamp()
    diff=now-break_data['start_time']
    break_type=break_duration_calculator(break_data['expected_length'])
    output=""
    output+=toolbox.list_user(break_data['user_id'],mention=True)
    output+=" lleva ya "
    output+=toolbox.seconds_to_string(diff, include_seconds=False)
    output+=" de "+break_type+"."
    output+="\n\nUsa /back para salirte de "+break_type
    tg.updater.bot.send_message(chat_id=break_data['alarm_channel'], text=output, parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)
    rebuild_schedule()
    return

def back(update, context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_in_group_or_admin(chat_id, user_id):
        return()
    timestamp=datetime.now().timestamp()
    
    break_users=sql.db.get_current_breaks()
    
    toolbox.debug(break_users)
    username = toolbox.list_user(user_id, mention=False)

    user_is_on_break = False
    for i in break_users:
        if i['user_id'] == user_id:
            sql.db.bring_user_back(i['id'], timestamp)
            break_type=break_duration_calculator(i['expected_length'])
            output=username+" ha vuelto de "+break_type+" a las "+\
                   datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")+\
                   ", después de "+toolbox.seconds_to_string(timestamp-i['start_time'])
            output+=toolbox.count_away_users(len(break_users)-1) #one user was removed after checking 
            context.bot.send_message(chat_id=chat_id, text=output, parse_mode="Markdown")
            rebuild_schedule()
            return()

    else:
        output=username+" no está de break."



    output+=toolbox.count_away_users(len(break_users))
    context.bot.send_message(chat_id=chat_id, text=output, parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)
    
    return

def quien(update,context):
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_in_group_or_admin(chat_id, user_id):
        return()
    output=""
    break_users=sql.db.get_current_breaks()
    timestamp=datetime.now().timestamp()
    if not break_users:
        output="0 users away.\n\n"
    else:
        if len(break_users)==1:
            output+="1 user away.\n\n"
        else:
            output+=str(len(break_users))+" users away.\n\n"
    for i in break_users:
        break_type=break_duration_calculator(i['expected_length'])
        output+="*"+toolbox.list_user(i['user_id'],mention=False)+"*"
        output+=" - "+datetime.fromtimestamp(i['start_time']).strftime("%H:%M")
        output+=" "+break_type
        output+=" ("+toolbox.seconds_to_string(timestamp-i['start_time'], longform=False)+")"
        output+="\n"
    context.bot.send_message(chat_id=chat_id, text=output, parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)
    #toolbox.save_json("break_users",break_users)
    return
