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
			images = waifu_pic['waifu']['pic']
			random_pic = choice(images)
			update.message.reply_photo(open(random_pic, 'rb'), caption="OwO<b>Appare una waifu!</b>\nAggiungila al tuo harem con /protecc <i>nome waifu</i>\n", parse_mode='HTML')
				


updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, appare_waifu))
print("bot in ascolto ...")
updater.start_polling()
