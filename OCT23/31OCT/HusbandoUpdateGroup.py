def HusbandoUpdateGroup(ID_Supergruppo, context: CallbackContext):
    # Aggiorno il numero di messaggi prima del prossimo spawn
    mycursor.execute("""SELECT Time_mess, Started
                        FROM Hmanagement
                        WHERE ID_Supergruppo = %s""",
                     (ID_Supergruppo,))
    data = mycursor.fetchone()
    Time_mess = data[0]
    Started = data[1]

    # Verifico il contatore dei messaggi prima dello spawn del husbando
    if Time_mess == 0:
        if Started:
            mycursor.execute("""UPDATE Hmanagement
                                SET Time_mess = Time_reset,
                                Started = 0,
                                ID_Husbando = NULL
                                WHERE ID_Supergruppo = %s""",
                             (ID_Supergruppo,))
            context.bot.send_message(chat_id=ID_Supergruppo, text="RIP, l'husbando è scappato via...")
        else:
            # Selezionare il valore massimo dell'id husbando
            mycursor.execute("""SELECT ID_Husbando
                                FROM husbandi
                                ORDER BY ID_Husbando desc""")
            data = mycursor.fetchone()
            MAX_HUSBANDO_ID = int(data[0])

            # Selezionare randomicamente un id
            ID_HUSBANDO = random.randrange(1, MAX_HUSBANDO_ID + 1)

            # Selezionare hsubando trovato
            mycursor.execute("""SELECT ID_Husbando, PATH_IMG
                                FROM husbandi
                                WHERE ID_Husbando = %s
                                                """, (ID_HUSBANDO,))
            data = mycursor.fetchone()
            ID_Husbando = data[0]
            PATH_IMG = data[1]

            # Registro l'husbando nelle impostazioni del gruppo e quindi l'attivazione della partita
            mycursor.execute("""UPDATE Hmanagement
                                                SET Time_mess = 25,
                                                Started = 1,
                                                ID_Husbando = %s
                                                WHERE ID_Supergruppo = %s""",
                             (ID_Husbando, ID_Supergruppo,))

            # Avverto agli utenti la comparsa di un husbando
            context.bot.send_photo(chat_id=ID_Supergruppo, photo=open(PATH_IMG, 'rb'),
                                   caption="OwO <b>Appare un husbando!</b>\nAggiungilo al tuo harem con /protecc <i>nome husbando</i>\n", parse_mode='HTML')
    else:
        mycursor.execute("""UPDATE Hmanagement
                        SET Time_mess = Time_mess - 1
                        WHERE ID_Supergruppo = %s""",
                     (ID_Supergruppo,))
