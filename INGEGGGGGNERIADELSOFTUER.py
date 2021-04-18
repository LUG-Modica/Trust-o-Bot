import json
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


FILENAME = "meetings.json"

def write_json(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)

def remember_meeting(update: Update, context: CallbackContext) -> None:
    messaggio = update.message.text
    campi = messaggio.split(" ") #/remembermeeting <titolo> <data>
    add_meeting(campi[1], campi[2])
    update.message.reply_text("Ho aggiornato il database!")
    return
def delete_meeting(update: Update, context: CallbackContext) -> None:
    messaggio = update.message.text
    campi = messaggio.split(" ") #/delete <titolo> <data>
    del_meeting(campi[1])
    update.message.reply_text("Ho aggiornato il database!")
    return

def show_meeting(update: Update, context: CallbackContext) -> None:
    messaggio =  ""
    with open(FILENAME, "r+") as f:
            data = json.load(f)
            temp = data['meetings']
            meeting_string = ""
            for object in temp:
                meeting_string += "Titolo: " + object['title'] + "\n"
                meeting_string += "Data: " + object['date'] + "\n"
            messaggio += meeting_string + "\n"
    update.message.reply_text(messaggio)

    return
def add_meeting(title, date):
    meeting = {'title' : title, 'date' : date}
    with open(FILENAME, "r+") as f:
        data = json.load(f)
        temp = data['meetings']
        temp.append(meeting)
    write_json(data)
    return

def del_meeting(title):
    with open(FILENAME, "r+") as f:
        data = json.load(f)
        temp = data['meetings']
        for object in temp:
            if object['title'] == title:
                temp.remove(object)
    write_json(data)
    return

def edit_title(old_title, new_title):
    with open(FILENAME, "r+") as f:
            data = json.load(f)
            temp = data['meetings']
            for object in temp:
                if object['title'] == old_title:
                    object['title'] = new_title
    write_json(data)
    return

def edit_date(title, new_date):
    with open(FILENAME, "r+") as f:
            data = json.load(f)
            temp = data['meetings']
            for object in temp:
                if object['title'] == title:
                    object['date'] = new_date
    write_json(data)
    return

del_meeting("DISTROWAR")
add_meeting("ciao", "domani")
edit_title("ciao", "CIAO")
edit_date("CIAO", "dopodomani" )
