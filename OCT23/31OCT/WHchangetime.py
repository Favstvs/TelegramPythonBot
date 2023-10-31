#changetime() per Husbando e Waifu

def changetime(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)
    ID_User = str(update.message.from_user.id)
    status = context.bot.get_chat_member(ID_Supergruppo, ID_User).status

    if status == "administrator" or status == "creator":
        # Prendo il messaggio
        NewTime = update.message.text
        try:
            # Rimozione comando dal messaggio
            NewTime = int(NewTime.partition(' ')[2])
            if 5 <= NewTime <= 20:
                mycursor.execute("""UPDATE Wmanagement
                                    SET Time_reset = %s
                                    WHERE ID_Supergruppo = %s
                                    """, (NewTime, ID_Supergruppo,))
                mycursor.execute("""UPDATE Hmanagement
                                    SET Time_reset = %s
                                    WHERE ID_Supergruppo = %s
                                    """, (NewTime, ID_Supergruppo,))
                                    
                update.message.reply_text(
                    "Tempo cambiato!\nDa ora le waifu appariranno dopo " + str(NewTime) + " messaggi")
            else:
                update.message.reply_text("No, non è giusto...\nIl nuovo tempo deve essere tra 100 e 10000")
        except:
            update.message.reply_text("No, non è giusto...\nControlla come usare correttamente il tasto")
    else:
        update.message.reply_text("Mi spiace, non hai i permessi per usare questo comando...")
