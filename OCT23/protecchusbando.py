def protecchusbando(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento messaggio
    # Verifico se il messaggio è editato
    if update.edited_message:
        ID_Supergruppo = str(update.edited_message.chat.id)
        ID_User = int(update.edited_message.from_user.id)
        Username = str(update.edited_message.from_user.username)
        protecc = str(update.edited_message.text).upper()
        ID_Mess = int(update.edited_message.message_id)
    else:
        ID_Supergruppo = str(update.message.chat.id)
        ID_User = int(update.message.from_user.id)
        Username = str(update.message.from_user.username)
        protecc = str(update.message.text).upper()
        ID_Mess = int(update.message.message_id)

    # Verifico se c'è un husbando ottenibile nel gruppo
    mycursor.execute("""SELECT ID_Husbando
                        FROM management
                        WHERE ID_Supergruppo = %s""",
                     (ID_Supergruppo,))
    data = mycursor.fetchone()
    if data[0]:
        # Registro il ID_Husbando
        ID_Husbando = data[0]

        # Rimozione comando dal messaggio
        protecc = protecc.partition(' ')[2]

        if protecc:
            # Prendo hsubando
            # Cerco il suo nome nel db
            mycursor.execute("""SELECT Nome_Husbando, Nome_Anime
                                        FROM husbandi
                                        WHERE ID_Husbando = %s
                                        """, (ID_Husbando,))
            data = mycursor.fetchone()
            original_Husbando = str(data[0])
            nome_anime = str(data[1])
            Husbando = str(data[0]).upper()

            # Rimuovo eventuali lettere accentate da entrambi i nomi
            protecc = unidecode.unidecode(protecc)
            Husbando = unidecode.unidecode(Husbando)

            # Rimuovo eventuali simboli
            # 1 - Sostituisco i trattini con spazi
            protecc = re.sub('-', ' ', protecc)
            Husbando = re.sub('-', ' ', Husbando)
            # 1.2 - Sostituisco gli slash con spazi
            protecc = re.sub('/', ' ', protecc)
            Husbando = re.sub('/', ' ', Husbando)
            # 2 - Il resto con vuoto
            protecc = re.sub('[^a-zA-Z0-9 \n\.]', '', protecc)
            Husbando = re.sub('[^a-zA-Z0-9 \n\.]', '', Husbando)
            # 3 Multipli spaces
            protecc = re.sub(' +', ' ', protecc)
            Husbando = re.sub(' +', ' ', Husbando)
                
            # Verifico se corrisponde
            if findWholeWord(protecc, Husbando):

                # Verifica se l'account è registrato nel db
                CheckUser(ID_User, Username)

                # Aggiungo la waifu all'harem dell'utente
                # Verifico se l'utente ha già protetto questa waifu
                mycursor.execute("""SELECT *
                                    FROM relation
                                    WHERE ID_User= %s AND
                                    ID_Supergruppo = %s AND
                                    ID_Husbando = %s
                                    """, (ID_User, ID_Supergruppo, ID_Husbando,))
                data = mycursor.fetchone()
                # if - Se esiste aggiungo un NP
                # else - Se non esiste creo la relazione
                if data:
                    mycursor.execute("""UPDATE relation
                                        SET NP = NP + 1
                                        WHERE ID_User= %s AND
                                        ID_Supergruppo = %s AND
                                        ID_Husbando = %s
                                        """, (ID_User, ID_Supergruppo, ID_Husbando,))
                else:
                    # Cerco il numero di relazione strette finora dall'utente
                    mycursor.execute("""SELECT count(*)
                                        FROM relation
                                        WHERE ID_User = %s AND
                                        ID_Supergruppo = %s""",
                                     (ID_User, ID_Supergruppo,))
                    data = mycursor.fetchone()
                    NUMERO_RELAZIONI = data[0]

                    # Setto i dati della nuova relazione
                    mycursor.execute("""INSERT INTO relation (ID_User, ID_Supergruppo, ID_Husbando, NP, Place)
                                     VALUES(%s, %s, %s, 1, %s)""",
                                     (ID_User, ID_Supergruppo, ID_Husbando, NUMERO_RELAZIONI + 1,))

                # Chiudo la partita e ripristino il timer dei messaggi
                mycursor.execute("""UPDATE management
                                    SET Time_mess = Time_reset,
                                    Started = 0,
                                    ID_Husbando = NULL
                                    WHERE ID_Supergruppo = %s""",
                                 (ID_Supergruppo,))

                # Avverto che è riuscito a proteggere la waifu
                context.bot.send_message(chat_id=ID_Supergruppo, text="✅ OwO <b>Hai protetto</b> " + original_Husbando + " di " + nome_anime + ".\n"
                                                                     "Questo husbando è stato aggiunto al tuo harem.", parse_mode='HTML',
                                         reply_to_message_id=ID_Mess)
                return
        # Avverto l'errore e aggiorno il gruppo
        update.message.reply_text("Nope, non è giusto...")
        UpdateGroup(ID_Supergruppo, context)
    else:
        # Aggiorna i dati gruppo
        UpdateGroup(ID_Supergruppo, context)
