from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import config

updater = Updater(token=config.api_token, use_context=True)
dispatcher = updater.dispatcher
