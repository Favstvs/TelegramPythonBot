def gift(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)
    ID_User_1 = int(update.message.from_user.id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)

    # Prendo il messaggio
    NewTrade = update.message.text

    # Rimozione comando dal messaggio
    NewGift = str(NewGift.partition(' ')[2])

    # Verifico se esiste testo dopo il comando
    if NewGift:
        # Verifico se il comando è il risposta ad un altro messaggio
        try:
            ID_Mess = int(update.message.reply_to_message.message_id)
        except:
            ID_Mess = ""

        if ID_Mess:
            if not update.message.reply_to_message.from_user.is_bot:

                # Verifico che l'utente non abbia risposto a sè stesso
                ID_User_2 = int(update.message.reply_to_message.from_user.id)

                if ID_User_1 != ID_User_2:
                    # Divido i due numeri in lista
                    NewGift = NewGift.split(" ")

                    # Salvo i 2 numeri trade
                    Regalo = ""
       
                    try:
                        Regalo = int(NewGift[0])
                      
                    except:
                        pass

                    # Verifico che entrambi i numeri siano stati dati
                    if Regalo:
                        # Verifico se esiste un altro trade e nel caso eliminarlo
                        mycursor.execute("""SELECT Mess_ID_Gift
                                            FROM regali
                                            WHERE ID_User_1 = %s AND
                                            ID_Supergruppo = %s""",
                                         (ID_User_1, ID_Supergruppo))
                        data = mycursor.fetchone()
                        if data:
                            try:
                                # Rimuovo il vecchio trade
                                mycursor.execute("""DELETE FROM regali WHERE ID_Supergruppo = %s AND ID_User_1=%s""",
                                                 (ID_Supergruppo,
                                                  ID_User_1,))

                                # Cancello il vecchio messaggio
                                context.bot.delete_message(ID_Supergruppo, message_id=data[0])
                            except:
                                pass

                        # Verifico l'identità delle  2 waifu
                        # Se non esistono invio l'avviso
                        mycursor.execute("""SELECT Nome_Waifu
                                                                        FROM relazioni, waifu 
                                                                        WHERE relazioni.ID_Supergruppo = %s
                                                                        AND relazioni.ID_User = %s
                                                                        AND relazioni.ID_Waifu = waifu.ID_Waifu
                                                                        AND relazioni.Place = %s""",
                                         (ID_Supergruppo, ID_User_1, Regalo))
                        data = mycursor.fetchone()
                        if data:
                        '''
                        CHECK THIS ONE Name_Servant_1 e Name_Servant_2
                        
                        
                        '''
                            Name_Servant_1 = data[0]
                            mycursor.execute("""SELECT Nome_Waifu
                                                                            FROM relazioni, waifu 
                                                                            WHERE relazioni.ID_Supergruppo = %s
                                                                            AND relazioni.ID_User = %s
                                                                            AND relazioni.ID_Waifu = waifu.ID_Waifu
                                                                            AND relazioni.Place = %s""",
                                             (ID_Supergruppo, ID_User_2, Scambio_2,))
                            data = mycursor.fetchone()
                            if data:
                                Name_Servant_2 = data[0]

                                # Creo i pulsanti
                                keyboard = [[InlineKeyboardButton('No :(', callback_data='No@Waifu_Bot'),
                                             InlineKeyboardButton('Yes!', callback_data='Yes@Waifu_Bot')],
                                            [InlineKeyboardButton('Quit', callback_data='Quit@Waifu_Bot')]]
                                reply_markup = InlineKeyboardMarkup(keyboard)

                                # Recupero gli Username per la creazione del messaggio
                                Username_1 = str(update.message.from_user.username)
                                Username_2 = str(update.message.reply_to_message.from_user.username)

                                # Invio il messaggio
                                Mess_ID_Gift= context.bot.send_message(
                                    text="Ti è stato offerto un regalo!\n\n" +
                                          Username_1 + " vuole darti la sua waifu " + Name_Servant_1 + "\n"
                                         "Accetti il regalo, " + Username_2 + "?"
                                    , chat_id=ID_Supergruppo,
                                    reply_to_message_id=ID_Mess,
                                    reply_markup=reply_markup)

                                # Digito i dati nel db
                                mycursor.execute(
                                    "INSERT INTO regali"
                                    "(ID_Supergruppo, Mess_ID_Gift, ID_User_1, ID_User_2, Regalo)"
                                    "VALUES(%s,%s,%s,%s,%s,%s)",
                                    (ID_Supergruppo, Mess_ID_Gift.message_id, ID_User_1, ID_User_2, Regalo))

                                return
                            else:
                                update.message.reply_text(
                                    "Sembra che questo utente nona abbia waifu da regalare..")
                                return
                        else:
                            update.message.reply_text(
                                "Sembra che tu non abbia waifu da regalare...")
                            return
    # Avverto dell'errore
    update.message.reply_text("Non è proprio giusto. <b>Rispondi</b> a qualcuno così:\n\n"
                              "<b>/tradewaifu</b> <i>{ID della Waifu che vuoi dare} {ID della Waifu che vuoi avere}</i>\n\n"
                              "esempio: <b>/tradewaifu 12 8</b>", parse_mode='HTML')


def checkgift(update: Update, context: CallbackContext):
    # Raccolgo dati utente
    ID_User = int(update.callback_query.from_user.id)
    ID_Supergruppo = str(update.callback_query.message.chat.id)
    Mess_ID_Trade = update.callback_query.message.message_id
    CallBackRequest = str(update.callback_query.data)

    mycursor.execute("""SELECT ID_User_1, ID_User_2
                        FROM scambi
                        WHERE ID_Supergruppo = %s AND Mess_ID_Trade = %s""", (ID_Supergruppo, Mess_ID_Trade))
    data = mycursor.fetchone()
    ID_User_Trade = [data[0], data[1]]
    if ID_User != ID_User_Trade[0] and ID_User != ID_User_Trade[1]:
        # Avverto che non fa parte dello scambio
        update.callback_query.answer(text="Questo non è il tuo scambio...")
    elif ID_User == ID_User_Trade[0]:
        if CallBackRequest == "Quit@Waifu_Bot":
            # Rimuovo il vecchio trade
            mycursor.execute("""DELETE FROM scambi WHERE ID_Supergruppo = %s AND Mess_ID_Trade=%s""", (ID_Supergruppo,
                                                                                                      Mess_ID_Trade,))
            # Cancello il vecchio messaggio
            try:
                context.bot.delete_message(ID_Supergruppo, message_id=Mess_ID_Trade)
            except:
                pass

            # Annullo lo scambio
        else:
            update.callback_query.answer(text="Non puoi rispondere al tuo stesso scambio...")
            # Avverto che non può rispondere al proprio scambio
    else:
        # Raccolgo la richiesta del callback
        if CallBackRequest == "Yes@Waifu_Bot":
            # Effettuo lo scambio
            # 1 - Rimuovo i rispettivi servant

            # 1.1 - Recupero i place dei servant
            mycursor.execute("""SELECT Scambio_1, Scambio_2 
                                FROM scambi
                                WHERE ID_Supergruppo = %s AND Mess_ID_Trade = %s""",
                             (ID_Supergruppo, Mess_ID_Trade,))
            data = mycursor.fetchone()
            Trade = [data[0], data[1]]
            NP = []
            ID_Waifu_Trade = []
            i = 0

            for Place in Trade:
                # Verifico se entrambi i servant sono disponibili
                mycursor.execute("""SELECT NP, ID_Waifu
                                    FROM relazioni
                                    WHERE ID_Supergruppo = %s AND ID_User = %s 
                                    AND Place = %s""", (ID_Supergruppo, ID_User_Trade[i], Place))

                data = mycursor.fetchone()
                if data:
                    NP.append(data[0])
                    ID_Waifu_Trade.append(data[1])
                else:
                    # Annullo lo scambio ed avverto che una delle waifu non è più disponibile
                    return
                i += 1
            # Abbasso l'NP dei servant coinvolti
            # Se raggiungono zero li deleto
            i = 0
            for Place in Trade:
                if NP[i] == 1:
                    # Rimuovo il Servant
                    mycursor.execute("""DELETE FROM relazioni 
                                        WHERE ID_Supergruppo = %s 
                                        AND ID_User = %s
                                        AND Place = %s""", (ID_Supergruppo, ID_User_Trade[i], Place,))
                    # Abbasso il place dei successivi
                    mycursor.execute("""UPDATE relazioni
                                        SET Place = Place - 1
                                        WHERE ID_Supergruppo = %s AND
                                        ID_User = %s AND
                                        Place > %s""", (ID_Supergruppo, ID_User_Trade[i], Place,))
                else:
                    # Abbasso l'NP
                    mycursor.execute("""UPDATE relazioni
                                        SET NP = NP - 1
                                        WHERE ID_User= %s AND
                                        ID_Supergruppo = %s AND
                                        Place = %s
                                        """, (ID_User_Trade[i], ID_Supergruppo, Place,))
                i += 1
            # Aggiungo il servant
            # Se Hanno già il servant aumento l'NP altrimenti aggiungo con insert
            i = 1
            for ID_Waifu in ID_Waifu_Trade:
                # Verifico l'ID della waifu
                # Aggiungo la waifu all'harem dell'utente
                # Verifico se l'utente ha già protetto questa waifu
                mycursor.execute("""SELECT *
                                    FROM relazioni
                                    WHERE ID_User= %s AND
                                    ID_Supergruppo = %s AND
                                    ID_Waifu = %s
                                                    """, (ID_User_Trade[i], ID_Supergruppo, ID_Waifu,))
                data = mycursor.fetchone()
                # if - Se esiste aggiungo un NP
                # else - Se non esiste creo la relazione
                if data:
                    mycursor.execute("""UPDATE relazioni
                                                        SET NP = NP + 1
                                                        WHERE ID_User= %s AND
                                                        ID_Supergruppo = %s AND
                                                        ID_Waifu = %s
                                                        """, (ID_User_Trade[i], ID_Supergruppo, ID_Waifu,))
                else:
                    # Cerco il numero di relazione strette finora dall'utente
                    mycursor.execute("""SELECT count(*)
                                                        FROM relazioni
                                                        WHERE ID_User = %s AND
                                                        ID_Supergruppo = %s""",
                                     (ID_User_Trade[i], ID_Supergruppo,))
                    data = mycursor.fetchone()
                    NUMERO_RELAZIONI = data[0]

                    # Setto i dati della nuova relazione
                    mycursor.execute("INSERT INTO relazioni(ID_User, ID_Supergruppo, ID_Waifu, NP, Place) "
                                     "VALUES(%s, %s, %s, 1, %s)",
                                     (ID_User_Trade[i], ID_Supergruppo, ID_Waifu, NUMERO_RELAZIONI + 1,))
                i -= 1
            Username = []
            Name_Servant = []
            i = 0

            # Rimuovo il trade
            mycursor.execute("""DELETE FROM scambi WHERE ID_Supergruppo = %s AND Mess_ID_Trade=%s""", (ID_Supergruppo,
                                                                                                      Mess_ID_Trade,))

            for ID_User in ID_User_Trade:
                mycursor.execute("""SELECT Username
                                        FROM users
                                        WHERE ID_User = %s""", (ID_User,))
                data = mycursor.fetchone()
                Username.append(data[0])
                mycursor.execute("""SELECT Nome_Waifu
                                        FROM waifu
                                        WHERE ID_Waifu = %s""", (ID_Waifu_Trade[i],))
                data = mycursor.fetchone()
                Name_Servant.append(data[0])
                i += 1
            # Invio messaggio in cui confermo il trade
            update.callback_query.message.edit_text("OwO lo scambio è completato!\n\n" + Username[0] + " ha dato " +
                                                    Name_Servant[0] + " a " + Username[1] + "\ne\n" +
                                                    Username[1] + " ha dato " +
                                                    Name_Servant[1] + " a " + Username[0])
        elif CallBackRequest == "No@Waifu_Bot":
            # Rimuovo il trade
            mycursor.execute("""DELETE FROM scambi WHERE ID_Supergruppo = %s AND Mess_ID_Trade=%s""", (ID_Supergruppo,
                                                                                                      Mess_ID_Trade,))
            Username = []
            for ID_User in ID_User_Trade:
                mycursor.execute("""SELECT Username
                                        FROM users
                                        WHERE ID_User = %s""", (ID_User,))
                data = mycursor.fetchone()
                Username.append(data[0])

            update.callback_query.message.edit_text(
                "Ahhh niente, " + Username[1] + " ha rifiutato lo scambio " + Username[0])
            # Annullo lo scambio
        elif CallBackRequest == "Quit@Waifu_Bot":
            update.callback_query.answer(text="Non puoi premere questo...")
