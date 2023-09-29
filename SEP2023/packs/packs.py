 '''
DATA: 15 Agosto
FUNZIONE PACK: "Ogni ora riceviamo un pacco che possiamo decidere se aprilo 
in waifu o husbando(quindi con la presenza di 2 scelte) in ogni pacco soni presenti 3 waifu/husbando"

METODO DI APPARIZIONE:
N.B: metodo ancora da decidere, 2 opzioni: o a TEMPO (esempio: ogni ora, ogni 2 o 3) o a MESSAGGI DEL GRUPPO(esempio: ogni 300, 400, 500 messaggi)

[N.B] OPPURE può essere anche un comando utilizzabile ogni tot messaggi

PARTE GRAFICA IN CHAT:
Comparsa in chat del messaggio del pack con due pulsanti di selezione: Waifu(Waifu@Waifu_Bot) o Husbando(Husbando@Waifu_Bot)

PARTE DATABASE:
step 1 - a seconda di cosa si è scelto selezionare la tabella o delle waifu o degli husbandi
step 2 - andare nella tabella selezionata ed estrarre 3 personaggi [Come selezionare inseme 3 dati insieme della tabella WAIFU o HUSBANDO]
step 3 - farli comparire in chat per essere catturati con /protecc(?)

[!?] Per selezionare e mandare 3 waifu/husbandi diversi nella chat gruppo:
        - mettere la selezione ed estraione in ciclo for per 3 volte (forse opzione migliore)
        - QUERY SQL per estrarre 3 elementi dalla tabella

DATA: 26 Settembre
applicare stesso metodo del ./daily per far apparire il pack:
- il comando si può eseguire dopo un determinato lasso di tempo

'''
def UpdatePacks(ID_Supergruppo, context: CallbackContext):
    # Check veloce del gruppo

    # Aggiorno il numero di messaggi prima del prossimo spawn
    # Condizione generale [if (new_message_number - last_message_number = 200) send_packs()]
    mycursor.execute("""SELECT Time_Mess, Started
                        FROM management
                        WHERE ID_Supergruppo = %s""",
                     (ID_Supergruppo,))
    data = mycursor.fetchone()
    Time_Mess = data[0]
    Started = data[1]

    # Verifico il contatore dei messaggi prima dello spawn del Pack
    if Time_Mess == 0:
        if Started:
            mycursor.execute("""UPDATE management
                                SET Time_Mess = Time_reset,
                                Started = 0,
                                ID_Waifu = NULL
                                WHERE ID_Supergruppo = %s""",
                             (ID_Supergruppo,))
            context.bot.send_message(chat_id=ID_Supergruppo, text="RIP, le waifu sono scappate via...")
            

            # Avverto gli utente del gruppo della comparsa del Packs
            context.bot.send_photo(chat_id=ID_Supergruppo, photo=open('/home/enrico/Immagini/w&h.jpeg', 'rb'), caption="Hey Hey <b>Appare finalmente un pack</b> 📦\n Scegli se vuoi <i>waifu</i> oppure <i>husbando<i>\n", parse_mode='HTML')
            # Creo i pulsanti per la selezione
            keyboard = [[InlineKeyboardButton('WAIFU', callback_data='Waifu@Waifu_Bot'),
                         InlineKeyboardButton('HUSBANDO', callback_data='Husbando@Waifu_Bot')],
                         [InlineKeyboardButton('Quit', callback_data='Esci@Waifu_Bot')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Raccolgo la richiesta del callback
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



'''
def main():

dp.add_handler(CallbackQueryHandler(UpdatePacks, pattern="Waifu@Waifu_Bot"))
dp.add_handler(CallbackQueryHandler(UpdatePacks, pattern="Husbando@Waifu_Bot"))
dp.add_handler(CallbackQueryHandler(UpdatePacks, pattern="Esci@Waifu_Bot"))
'''
    
    
                                
