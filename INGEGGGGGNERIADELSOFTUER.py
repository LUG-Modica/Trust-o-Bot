import time
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
from datetime import datetime
from datetime import date


FILENAME = "meetings.json"
CHAT_ID = -1001341923208

def write_json(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)

def remember_meeting(update: Update, context: CallbackContext) -> None:
    messaggio = update.message.text
    campi = messaggio.split(" ") #/remembermeeting <titolo> <data> <ora>
    add_meeting(campi[1], campi[2], campi[3])
    update.message.reply_text("Ho aggiornato il database!")
    return
def delete_meeting(update: Update, context: CallbackContext) -> None:
    messaggio = update.message.text
    campi = messaggio.split(" ") #/delete <titolo> <data>
    del_meeting(campi[1])
    update.message.reply_text("Ho aggiornato il database!")
    return
def add_guest_to_meeting(update: Update, context: CallbackContext) -> None:
    messaggio = update.message.text
    campi = messaggio.split(" ") #/addguest <title> <guest1> <guest2> ...
    for i in range(2,len(campi)):
	    add_guest(str(campi[1]),str(campi[i]))
    update.message.reply_text("Ho aggiornato il database!")

def show_meeting(update: Update, context: CallbackContext) -> None:
    messaggio =  ""
    with open(FILENAME, "r+") as f:
            data = json.load(f)
            temp = data['meetings']
            meeting_string = ""
            for object in temp:
                meeting_string += "Titolo: " + object['title'] + "\n"
                meeting_string += "Data: " + object['date'] + "\n"
                meeting_string += "Ora: " + object['time'] + "\n"
                meeting_string += "Partecipanti: "
                for guest in object['guests']:
                    meeting_string += guest + "\n"
            messaggio += meeting_string + "\n"
    update.message.reply_text(messaggio)

    return
def add_meeting(title, date, time):
	meeting = {'title' : title, 'date' : date,'time' : time, 'guests' : [] }
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

def add_guest(title, guest_username):
	with open(FILENAME, "r+") as f:
		data = json.load(f)
		temp = data['meetings']
		meeting = 0
		for object in temp:
			if object['title'] == title:
				meeting = object
				break
		meeting['guests'].append(guest_username)
	write_json(data)


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%d/%m/%Y")
    d2 = datetime.strptime(d2, "%d/%m/%Y")
    return abs((d2 - d1).days)

def today_date():
	today = date.today()
	d1 = today.strftime("%d/%m/%Y")
	return d1

def is_time_to_send():
	now = datetime.now()
	hour = int(now.strftime("%H"))
	if (hour == 12):
		return True
	return False

def notifier_thread(bot):
	while True:
		time.sleep(30*60)

		if is_time_to_send() == False:
			continue

		with open(FILENAME, "r+") as f:
			data = json.load(f)
			temp = data['meetings']
			for meeting in temp:
				print(today_date())
				print(meeting['date'])
				if ( days_between(today_date(),meeting['date'])\
					<= -1):
					del_meeting(meeting['title'])
					continue
				remain = \
				days_between(today_date(),meeting['date'])
				print(remain)
				reminder_text = "Giorni rimanenti a " +\
					str(meeting['title']) + " " +\
						str(remain) +\
						"\nAlle " + str(meeting['time'])
				reminder_text += "\nPartecipanti:\n"
				for guest in meeting['guests']:
					reminder_text += guest + "\n"
				bot.send_message(CHAT_ID,reminder_text)
	pass























