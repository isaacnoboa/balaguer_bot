import config
import toolbox
import sqlite_handler as sql


def addme(update,context): #db'd
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_in_group_or_admin(chat_id, user_id):
        return()
    check=sql.db.check_help_user(user_id)
    output="*"
    output+=""+toolbox.list_user(user_id, mention=False)

    if check:
        output+="* is already on the helper list."

        # i don't think there may be duplicates if my bot works correctly,
        # but using a database creates that possibility.

        if len(check)>1 and config.verbose: 
            toolbok.notify_owner("warning: dupligate found for "+ str(check)+"\n"+
                         "\nchat_id: "+chat_id+
                         "\nuser_id: "+user_id
                         )
    else:
        output+="* added to the helper list at index "
        output+=str(sql.db.add_help_user(user_id)[0])+"."

    if config.verbose: 
        print(output)
    context.bot.send_message(chat_id=chat_id, text=str(output), parse_mode="Markdown")
    return()

    # https://stackoverflow.com/a/6977901
    # no idea why i added this comment but too lazy to remove it 



def removeme(update,context): #db'd 
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_in_group_or_admin(chat_id, user_id):
        return()
    check=sql.db.check_help_user(user_id)
    output=""
    output+="*"+toolbox.list_user(user_id, mention=False)

    if check:
        output+="* removed from the helper list."
        sql.db.remove_help_user(user_id)
        ## debugging purposes:
        #check=sql.db.check_help_user(user_id)
        #output+=str(check)
    else:
        output+="* not found on the helper list."
    context.bot.send_message(chat_id=chat_id, text=str(output), parse_mode="Markdown")
    return()


def helpme(update, context): #db'd
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_in_group_or_admin(chat_id, user_id):
        return()
    help_users=sql.db.get_help_users()
    output="Pinging users in the helper list:\n"
    output+=toolbox.list_users(help_users)
    context.bot.send_message(chat_id=chat_id, text=output, parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)

def listusers(update, context): #db'd
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_admin(user_id):
        return()
    output = "Listing users with IDs:\n"
    all_users = sql.db.get_all_users()
    for i in all_users:
        output = output + str(i['user_id']) + " " + i['name']+"\n"
    context.bot.send_message(chat_id=chat_id, text=output)#, parse_mode="Markdown")#, reply_to_message_id=update.message.message_id)


#TODO: use the same add function for both self and  manual add?
#TODO: allow list of users to be added
   #maybe do that by rewriting with context.args[0] instead of stripping the string
def adduser(update, context): #db'd 
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_admin(user_id):
        return()
    #help_users=toolbox.load_json('help_users')
    user_id=int(toolbox.remove_prefix(update.message.text,"/adduser "))
    check=sql.db.check_help_user(user_id)
    output="*"
    output+=""+toolbox.list_user(user_id, mention=False)

    if check:
        output+="* is already on the helper list."

        # i don't think there may be duplicates if my bot works correctly,
        # but using a database creates that possibility.

        if len(check)>1 and config.verbose: 
            toolbox.notify_owner("warning: dupligate found for "+ str(check)+"\n"+
                         "\nchat_id: "+chat_id+
                         "\nuser_id: "+user_id
                         )
    else:
        output+="* added to the helper list at index "
        output+=str(sql.db.add_help_user(user_id)[0])+"."

    if config.verbose: 
        print(output)
    context.bot.send_message(chat_id=chat_id, text=str(output), parse_mode="Markdown")
    return()
    
def removeuser(update, context): #db'd 
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    if not toolbox.user_is_admin(user_id):
        return()
    user_id=int(toolbox.remove_prefix(update.message.text,"/removeuser "))
    check=sql.db.check_help_user(user_id)
    output=""
    output+="*"+toolbox.list_user(user_id, mention=False)

    if check:
        output+="* removed from the helper list."
        sql.db.remove_help_user(user_id)
        ## debugging purposes:
        #check=sql.db.check_help_user(user_id)
        #output+=str(check)
    else:
        output+="* not found on the helper list."
    context.bot.send_message(chat_id=chat_id, text=str(output), parse_mode="Markdown")
    return()