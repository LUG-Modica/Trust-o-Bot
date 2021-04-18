#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

import logging
import os
import subprocess
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
from csv_handling import * # our module for csv data
from INGEGGGGGNERIADELSOFTUER import *

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

def ping(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Pong')
def everyone(update: Update, context: CallbackContext) -> None: #notifies everyone about a message
    update.message.pin(disable_notification=False)

def source(update: Update, context: CallbackContext) -> None:  #display help output
    update.message.reply_markdown("[Codice Sorgente](https://github.com/LUG-Modica/Trust-o-Bot)")

def help(update: Update, context: CallbackContext) -> None:  #display help output
    update.message.reply_text("Ecco una lista dei comandi:\n"
                                  "/ping : Usalo per vedere se il bot è attivo\n"
                                  "/compile <nome_output>: Usalo per compilare un file in C\n"
                                  "/everyone <messaggio> : Usalo per menzionare tutti in un messaggio\n"
                                  "/kick in risposta : Usalo in risposta ad un messaggio per kickare un intruso\n"
                                  "/source : Usalo per ottenere il link al codice sorgente del bot\n"
                                  "/halloffame : Usalo per ottenere una lista con la reputazione di tutti i membri\n"
                                  "/add in risposta ad un messaggio : Usalo per incrementare di 1 la reputazione dell'utente\n"
                                  "/dec in risposta ad un messaggio : Usalo per decrementare di 1 la reputazione dell'utente\n"
                                  "/addmeeting <titolo> <data> : Usalo per aggiungere un meeting\n"
                                  "/deletemmeting <titolo> (si è un id) : Usalo per rimuovere almeno un meeting\n"
                                  "/showmeeting : Usalo per vedere i meeting schedulati\n"
                                  "/help : Usalo per mostrare questo messaggio\n"
                                  )
#compile a given C file
def compiler(update: Update, context: CallbackContext) -> None:
    params=update.message.text.split(" ")
    if len(params) >= 2:
        output_bin=params[1]
    else:
        output_bin="a.out"
    update.message.reply_text('Compiling...')
    print("Saving file in local directory")
    update.message.reply_to_message.document.get_file().download("tmp.c")
    print("Starting compilation...")
    ret=os.system("gcc tmp.c -o " + output_bin)
    try:
        output_str=subprocess.check_output(['gcc','tmp.c','-Wall','-o',output_bin],stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(e.output)
    if ret == 0:
        fd=open(output_bin,"rb")
        if len(output_str) != 0:
            update.message.reply_text(output_str.decode("utf-8"))
        update.message.reply_document(fd)
        fd.close()
    else:
        update.message.reply_text("Errore durante la compilazione: " + ret)
    print("End of compilation...")
    os.system("rm tmp.c " + output_bin)
    print("Cleaned, exiting...")
    return

# kick member
def kick(update: Update, context: CallbackContext) -> None:
    update.effective_chat.kick_member(update.message.reply_to_message.from_user.id)

# shows reputation about all members
def hall_of_fame(update: Update, context: CallbackContext) -> None:
    message = "Reputazione di tutti i membri\n" # creating the message
    data = get_users_reputation()
    message += data
    update.message.reply_text(message)

# increase reputation of given user
def add(update: Update, context: CallbackContext) -> None:
    username=update.message.reply_to_message.from_user.username
    add_reputation(username,1) # add reputation
    message = "Reputazione aggiornata!\n"
    message += get_user_reputation(username)
    update.message.reply_text(message)

# decrease reputation of given user
def dec(update: Update, context: CallbackContext) -> None:
    username=update.message.reply_to_message.from_user.username
    add_reputation(username,-1) # add reputation
    message = "Reputazione aggiornata!\n"
    message += get_user_reputation(username)
    update.message.reply_text(message)

def captcha(update: Update, context: CallbackContext) -> None:
    #append to map user_id - captcha_string,attempts_number
    if not update.message.new_chat_members: #if list is empty
        captcha_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(5))
        image = ImageCaptcha()
        image.write(str(captcha_string),CAPTCHA_FILE)
        fd = open(CAPTCHA_FILE,'rb')
        update.message.reply_photo(fd).reply_markdown("Benvenuto nel gruppo " + update.effective_user.mention_markdown() + "!\n"
                                                "Per favore completa il CAPTCHA")
        captcha_maps[str(update.effective_user.id)] = [str(captcha_string),NUMBER_TEMPTS]
    else: #if list is not empty, then users were added and we need to iterate over them and generate captchas
        for user in update.message.new_chat_members:
            captcha_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(5))
            image = ImageCaptcha()
            image.write(str(captcha_string),CAPTCHA_FILE)
            fd = open(CAPTCHA_FILE,'rb')
            update.message.reply_photo(fd).reply_markdown("Benvenuto nel gruppo " + user.mention_markdown() + "!\n"
                                                    "Per favore completa il CAPTCHA")
            captcha_maps[str(user.id)] = [str(captcha_string),NUMBER_TEMPTS]
    return

def verify_captcha(update: Update, context: CallbackContext) -> None:
    captcha_to_verify = captcha_maps[str(update.effective_user.id)]
    if captcha_to_verify is None:
        return None
    if str(captcha_to_verify[0]) == update.message.text:
        captcha_maps.pop(str(update.effective_user.id))
        update.message.reply_text("Benvenuto nel gruppo!")
    elif captcha_to_verify[1] > 0: # If message is wrong
        captcha_to_verify[1] -= 1
        update.message.reply_text("Tentativi rimasti: " + str(captcha_to_verify[1]))
        update.message.delete() #deletes the message if wrong, in order to avoid spammers
    else:
        update.effective_chat.kick_member(update.effective_user.id)
        captcha_maps.pop(str(update.effective_user.id))
        update.message.reply_text("Kick!")
    return

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
    # display source code link
    dispatcher.add_handler(CommandHandler("source", source))
    # display help output
    dispatcher.add_handler(CommandHandler("help", help))
    # calls everyone in the group
    dispatcher.add_handler(CommandHandler("everyone", everyone))
    # info about the server
    dispatcher.add_handler(CommandHandler("compile", compiler))
    # kick a member
    dispatcher.add_handler(CommandHandler("kick", kick))
    # get csv data from all members
    dispatcher.add_handler(CommandHandler("halloffame", hall_of_fame))
    # increase reputation
    dispatcher.add_handler(CommandHandler("add", add))
    # decrease reputation
    dispatcher.add_handler(CommandHandler("dec", dec))
    # meetings scheduling
    dispatcher.add_handler(CommandHandler("remembermeeting", remember_meeting))
    # delete meeting
    dispatcher.add_handler(CommandHandler("deletemeeting", delete_meeting))
    # show meeting
    dispatcher.add_handler(CommandHandler("showmeeting", show_meeting))


    #Greeter : Generates captchas only
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.status_update.new_chat_members,captcha)],
        states={
        },
        fallbacks=[None],per_chat=True,per_user=False #everyone in the chat can trigger the state REPLY, but if not in the list of unverified then nothing happens
    ))
    # Verifier : If you still have to verify captcha then this will check for it
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.all,verify_captcha)],
        states={
        },
        fallbacks=[None],per_chat=True,per_user=False #everyone in the chat can trigger the state REPLY, but if not in the list of unverified then nothing happens
    ))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
