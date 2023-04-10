#import telepot
from random import choice
from glob import glob
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes



TOKEN = "6093171238:AAFl4q-S1Wp-bBQJV4c1luvpTTKXVFHQD7c"
chat_id = ""
'''
bot = telepot.Bot(TOKEN)
bot.sendMessage(chat_id, "uwu, è apparsa una waifu! Aggiungila al tuo harem con /protecc nome ")
bot.sendMessage(chat_id, "OwO, hai catturato " + + ". Questo personaggio è stato aggiunto al tuo harem.")
bot.sendMessage(chat_id, "Spiase ma no, il nome non è corretto. Riprova!")
'''

# APPARE WAIFU
#######################

def appare_waifu(update, context):
	image = choice(glob("waifu/*.jpg"))
	update.message.reply_photo(open(image, 'rb'))
	update.message.reply_text("uwu, è apparsa una waifu! Aggiungila al tuo harem con /protecc nome ")


# COMANDI
#######################

def protecc():
