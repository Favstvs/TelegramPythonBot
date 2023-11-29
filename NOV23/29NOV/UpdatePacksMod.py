def UpdatePacks(update: Update, context: CallbackContext):
    ID_Supergruppo = str(update.effective_message.chat.id)
    ID_User = str(update.effective_message.from_user.id)
    Username = str(update.effective_message.from_user.username)
    
    CheckUser(ID_User, Username)
    
    keyboard = [[InlineKeyboardButton('WAIFU', callback_data='Waifu@Tel_Bot'),
                         InlineKeyboardButton('HUSBANDO', callback_data='Husbando@Tel_Bot')],
                         [InlineKeyboardButton('Quit', callback_data='Esci@Tel_Bot')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_photo(chat_id=ID_Supergruppo, photo=open('/home/enrico/Immagini/w&h.jpeg', 'rb'), caption="Hey Hey <b>Appare finalmente un pack</b> 📦\n Scegli se vuoi <i>waifu</i> oppure <i>husbando</i>\n", reply_markup=reply_markup, parse_mode='HTML')
            CallBackRequest = str(update.callback_query.data)
            
    if CallBackRequest == "Waifu@Tel_Bot":
        for x in range(3):
            UpdateGroup(ID_Supergruppo, context)
    elif CallBackRequest == "Husbando@Tel_Bot":
        for x in range(3):
            HUpdateGroup(ID_Supergruppo, context)
    elif CallBackRequest == "Esci@Tel_Bot":
        update.callback_query.answer(text="Nada...")
