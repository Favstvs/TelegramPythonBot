import json
from random import choice
from glob import glob
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "6093171238:AAFl4q-S1Wp-bBQJV4c1luvpTTKXVFHQD7c"

def start(update, context):
	update.message.reply_text("Bot avviato")

def appare_waifu(update, context):
	with open('waifu_list.json', 'r') as waifu_file:
		waifu_pic = json.load(waifu_file)
		testo = update.message.text.lower()
		if "waifu" in testo:
			image = waifu_pic['pic']#choice(glob("waifu/*.jpg"))
			update.message.reply_photo(open(image, 'rb'))
			update.message.reply_text("uwu, è apparsa una waifu! Aggiungila al tuo harem con /protecc nome ")


updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, appare_waifu))
print("bot in ascolto ...")
updater.start_polling()
