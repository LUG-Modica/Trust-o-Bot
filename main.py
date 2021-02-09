#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

import logging
import random
import configparser
import string
from captcha.image import ImageCaptcha
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
parser = configparser.ConfigParser()
parser.read('config.ini')
CAPTCHA_FILE=parser["Settings"]["foto"]
NUMBER_TEMPTS=int(parser["Settings"]["tentativi"])
REPLY = range(1)
captcha_maps = dict()
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def ping(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Pong')

# kick member
def kick(update: Update, context: CallbackContext) -> None:
    update.effective_chat.kick_member(update.message.reply_to_message.from_user.id)
def captcha(update: Update, context: CallbackContext) -> None:
    print("Sono in captcha")
    # captcha function
    captcha_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(5))
    image = ImageCaptcha()
    image.write(str(captcha_string),CAPTCHA_FILE)
    fd = open(CAPTCHA_FILE,'rb')
    update.message.reply_photo(fd)
    #append to map user_id - captcha_string
    captcha_maps[str(update.effective_user.id)] = [str(captcha_string),NUMBER_TEMPTS]
    return REPLY

def verify_captcha(update: Update, context: CallbackContext) -> None:
    print("Sono in verify captcha")
    captcha_to_verify = captcha_maps[str(update.effective_user.id)]
    if captcha_to_verify is None:
        return None
    if str(captcha_to_verify[0]) == update.message.text:
        captcha_maps.pop(str(update.effective_user.id))
        update.message.reply_text("Benvenuto nel gruppo!")
        return ConversationHandler.END
    elif captcha_to_verify[1] > 0:
        captcha_to_verify[1] -= 1
        update.message.reply_text("Tentativi rimasti: " + str(captcha_to_verify[1]))
    else:
        update.effective_chat.kick_member(update.effective_user.id)
        update.message.reply_text("Kick!")
        return ConversationHandler.END

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    tok = str(parser["Settings"]["Token"])
    updater = Updater(token=str(tok), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("ping", ping))
    # kick a member
    dispatcher.add_handler(CommandHandler("kick", kick))
    #captcha handling for new members
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.status_update.new_chat_members,captcha)],
        states={
            REPLY: [MessageHandler(Filters.all,verify_captcha)]
        },
        fallbacks=[None]
    ))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
