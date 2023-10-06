def UpdatePacks(ID_Supergruppo, context: CallbackContext):
 ##########################################################
 #[ATTENZIONE] Però con il metoodo di /daily, l'esecuzione del comando si basa sull'utilizzo dell'utente e non di un parametro globale
 # dunque il comando potrebbe essere ripetuto una volta ogni tot ore per ogni utente nel gruppo
 # managament.sql dovrebbe essere universale 
 # ESEMPIO: colonna Time_Mess_Packs che funziona come il Time_Mess per il daily, ma universali per tutto il gruppo
 ##########################################################
 
 '''
 CREATE TABLE `H&Wmanagement` (
  `ID_Supergruppo` bigint NOT NULL,
  `ID_Waifu` int DEFAULT NULL,
  `ID_Husbando` int DEFAULT NULL,
  `Time_Mess` int unsigned NOT NULL,
  
  `Time_Mess_Packs` datetime, <- che si aggiorna con l'uso del nuovo comando
  
  `Started` tinyint NOT NULL,
  `Time_reset` int unsigned NOT NULL,
  PRIMARY KEY (`ID_Supergruppo`),
  KEY `management_ibfk_2` (`ID_Waifu`),
  KEY `management_ibfk_3` (`ID_Husbando`),
  CONSTRAINT `management_ibfk_1` FOREIGN KEY (`ID_Supergruppo`) REFERENCES `supergruppo` (`ID_Supergruppo`),
  CONSTRAINT `management_ibfk_2` FOREIGN KEY (`ID_Waifu`) REFERENCES `waifu` (`ID_Waifu`),
  CONSTRAINT `management_ibfk_3` FOREIGN KEY (`ID_Husbando`) REFERENCES `husbando` (`ID_Husbando`)
 
 '''

 
    ID_Supergruppo = str(update.message.chat.id)
    ID_User = str(update.message.from_user.id)
    Username = str(update.message.from_user.username)
    
    UpdateGroup(ID_Supergruppo, context)
    CheckUser(ID_User, Username)
    
    Time_Mess = update.message.date
    Time_Mess = Time_Mess.replace(tzinfo=None)
    
    mycursor.execute("""SELECT Time_Mess_Packs FROM management WHERE ID_Supergruppo=%s""", (ID_Supergruppo,)) 
    data = mycursor.fetchone()
    
    if data[0] == None:
        mycursor.execute("""UPDATE managament SET Time_Mess_Packs=now() WHERE ID_Supergruppor=%s""",(ID_Supergruppo,))
        mycursor.execute("""SELECT Time_Mess_Packs FROM managament WHERE ID_Supergruppo=%s""", (ID_Supergruppo,))
        data1 = mycursor.fetchone()
        date_1 = data1[0]
    else:
        date_1 = data[0]
        date_2 = Time_Mess
        date_format_str = "%Y-%m-%d %H:%M:%S"
        date_1_start = datetime.strptime(str(date_1), date_format_str)
        date_2_end = datetime.strptime(str(date_2), date_format_str)
        
        diff = date_2_end - date_1_start
        diff_in_hours = diff.total_seconds()/3600
        
        if diff_in_hours > 8: #Ogni 8 ore, altrimenti RIFIUTA
 
            context.bot.send_photo(chat_id=ID_Supergruppo, photo=open('/home/enrico/Immagini/w&h.jpeg', 'rb'), caption="Hey Hey <b>Appare finalmente un pack</b> 📦\n Scegli se vuoi <i>waifu</i> oppure <i>husbando<i>\n", parse_mode='HTML')
            # Creo i pulsanti per la selezione
            keyboard = [[InlineKeyboardButton('WAIFU', callback_data='Waifu@Waifu_Bot'),
                         InlineKeyboardButton('HUSBANDO', callback_data='Husbando@Waifu_Bot')],
                         [InlineKeyboardButton('Quit', callback_data='Esci@Waifu_Bot')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if CallBackRequest == "Waifu@Waifu_Bot":
                for x in range(3):
                 mycursor.execute("""SELECT ID_Waifu
                                    FROM waifu
                                    ORDER BY ID_Waifu desc""")
                 data = mycursor.fetchone()
                 MAX_WAIFU_ID = int(data[0])

                 ID_WAIFU = random.randrange(1, MAX_WAIFU_ID + 1)

                 mycursor.execute("""SELECT ID_Waifu, PATH_IMG
                                    FROM waifu
                                    WHERE ID_Waifu = %s
                                 """, (ID_WAIFU,))
                 data = mycursor.fetchone()
                 ID_Waifu = data[0]
                 PATH_IMG = data[1]

                 mycursor.execute("""UPDATE Wmanagement
                                    SET Time_Mess = 25,
                                    Started = 1,
                                    ID_Waifu = %s,
                                    WHERE ID_Supergruppo = %s""",
                                    (ID_Waifu, ID_Supergruppo,))
                 context.bot.send_photo(chat_id=ID_Supergruppo, photo=open(PATH_IMG, 'rb'), caption="OwO <b>Appare una waifu!</b>\nAggiungila al tuo harem con /protecc <i>nome waifu</i>\n", parse_mode='HTML')
            elif CallBackRequest == "Husbando@Waifu_Bot":
                for x in range(3):
                 mycursor.execute("""SELECT ID_Husbando
                                    FROM husbandi
                                    ORDER BY ID_Husbando desc""")
                 data = mycursor.fetchone()
                 MAX_HUSBANDO_ID = int(data[0])
                
                 ID_HUSBANDO = random.randrange(1, MAX_HUSBANDO_ID + 1)

                 mycursor.execute("""SELECT ID_Husbando, PATH_IMG
                                    FROM husbandi
                                    WHERE ID_Husbando = %s""", (ID_HUSBANDO,))
                 data = mycursor.fetchone()
                 ID_Husbando = data[0]
                 PATH_IMG = data[1]

                 mycursor.execute("""UPDATE Hmanagement
                                    SET Time_Mess = 25,
                                    Started = 1,
                                    ID_Husbando = %s
                                    WHERE ID_Supergruppo = %s""",
                                    (ID_Husbando, ID_Supergruppo,))
                 context.bot.send_photo(chat_id=ID_Supergruppo, photo=open(PATH_IMG, 'rb', caption="Owo <b>Appare un husbando!</b>\nAggiungilo al tuo harem con /protecc <i>nome husbando</i>\n", parse_mode='HTML'))
            elif CallBackRequest == "Esci@Waifu_Bot":
                update.callback_query.answer(text="Nada...")
  
        else:
            update.message.reply_text("❌HaiAvete già richesto un Pack. Dovete aspettare 8 ore ")
