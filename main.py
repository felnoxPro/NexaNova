import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re
import os

# Bot token from BotFather
TOKEN = '7829325332:AAFGZxuP-2z0RMscXLpuEBLEH-C5nzdCKzg'

# Initialize bot
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

# Basic commands
def start(update: telegram.Update, context: CallbackContext):
    update.message.reply_text('Hello! I’m your bot. Use /help for commands.')

def help_command(update: telegram.Update, context: CallbackContext):
    update.message.reply_text('Commands: /start, /help, /info')

def info(update: telegram.Update, context: CallbackContext):
    update.message.reply_text('I’m a bot with GC management, music, and more!')

# Greetings
def greet_new_member(update: telegram.Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        update.message.reply_text(f'Welcome, {member.first_name}! Enjoy the group!')

def goodbye(update: telegram.Update, context: CallbackContext):
    update.message.reply_text(f'Goodbye, {update.message.left_chat_member.first_name}!')

# Anti-spam (basic: mute if user sends >5 messages in 10 seconds)
spam_tracker = {}
def anti_spam(update: telegram.Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    current_time = update.message.date.timestamp()

    if user_id not in spam_tracker:
        spam_tracker[user_id] = []

    spam_tracker[user_id].append(current_time)
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 10]

    if len(spam_tracker[user_id]) > 5:
        context.bot.restrict_chat_member(chat_id, user_id, until_date=current_time+60)  # Mute for 60s
        update.message.reply_text(f'{update.message.from_user.first_name} muted for spamming!')
        spam_tracker[user_id] = []

# NSFW protection (basic keyword filter)
nsfw_keywords = ['nsfw', 'adult', 'porn']  # Expand this list
def nsfw_protection(update: telegram.Update, context: CallbackContext):
    message = update.message.text.lower()
    if any(keyword in message for keyword in nsfw_keywords):
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        context.bot.restrict_chat_member(
            update.message.chat_id, update.message.from_user.id, until_date=update.message.date.timestamp()+60
        )
        update.message.reply_text(f'{update.message.from_user.first_name} muted for NSFW content!')

# Handlers
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', help_command))
dp.add_handler(CommandHandler('info', info))
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_new_member))
dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, goodbye))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, anti_spam))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, nsfw_protection))

# Start the bot
updater.start_polling()
updater.idle()
