import mysql.connector
import random
import logging
import unidecode
import re
import time
from telegram.ext import *
from telegram import *
from telegram.ext import MessageHandler, filters

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="kali123",
    database="waifus",
    autocommit=True)
mycursor = db.cursor(buffered=True)

logger = logging.getLogger(__name__)
updater = Updater('6093171238:AAFl4q-S1Wp-bBQJV4c1luvpTTKXVFHQD7c')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

    
# Creare chiamata sleep che ogni ora fa una chiamata
@run_async
def calldb():
    mycursor.execute("""SELECT Nome_Waifu
                        FROM waifu
                        WHERE ID_Waifu = 1""")
    data = mycursor.fetchone()
    print("ping: " + data[0])
    time.sleep(1800)
    calldb()


calldb()


# CHAT REGOLARE
# Aggiorno il time dei messaggi
def maindef(update: Update, context: CallbackContext):
    # Raccolgo dati gruppo
    Supergruppo_nome = str(update.message.chat.title)
    ID_Supergruppo = str(update.message.chat.id)

    # Verifica se il gruppo è registrato nel db
    NewGroup(ID_Supergruppo, Supergruppo_nome)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)


# CHAT PRIVATA
def private(update: Update, context: CallbackContext):
    update.message.reply_text(text="This doesn't look like a group kek. "
                                   "Add me to one to get start collecting servants waifus OwO. "
                                   "In a group you can use /protecc to catch waifus and "
                                   "/listawaifu to view your waifus. (If this really is a group, "
                                   "try re-adding the bot).")


# INFORMAZIONI SUL BOT
def help(update: Update, context: CallbackContext):
    update.message.reply_text(text="Aggiungi waifu al tuo harem con /protecc <i>nome del personaggio</i>\n"
                                   "<i>The localization names are based on the Spirit Origin List of Fate/Grand Order "
                                   "NA server and from FGO Wiki for unreleased servants</i>\n"
                                   "<b>The only exception is Altria, here reported as Artoria</b>\n"
                                   "/listawaifu per vedere il tuo harem\n"
                                   "/gruppowaifu visualizza gli harem più grandi del gruppo\n"
                                   "/changetime <i>number</i> per cambiare il numero di messaggi per lo spawn"
                                   " (only administrators)\n<i>The new time must be 100 &lt;= new time &lt;= 10000</i>\n"
                              , parse_mode='HTML')


# COMANDI INTERAZIONE CON IL BOT
#############################################

# Proteggi servant
def proteccservant(update: Update, context: CallbackContext):
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

    # Verifico se c'è un servant ottenibile nel gruppo
    mycursor.execute("""SELECT ID_Waifu
                        FROM management
                        WHERE ID_Supergruppo = %s""",
                     (ID_Supergruppo,))
    data = mycursor.fetchone()
    if data[0]:
        # Registro il ID_Waifu
        ID_Waifu = data[0]

        # Rimozione comando dal messaggio
        protecc = protecc.partition(' ')[2]

        if protecc:
            # Prendo la waifu
            # Cerco il suo nome nel db
            mycursor.execute("""SELECT Nome_Waifu
                                        FROM waifu
                                        WHERE ID_Waifu = %s
                                        """, (ID_Waifu,))
            data = mycursor.fetchone()
            original_Servant = str(data[0])
            Servant = str(data[0]).upper()

            # Rimuovo eventuali lettere accentate da entrambi i nomi
            protecc = unidecode.unidecode(protecc)
            Servant = unidecode.unidecode(Servant)

            # Rimuovo eventuali simboli
            # 1 - Sostituisco i trattini con spazi
            protecc = re.sub('-', ' ', protecc)
            Servant = re.sub('-', ' ', Servant)
            # 1.2 - Sostituisco gli slash con spazi
            protecc = re.sub('/', ' ', protecc)
            Servant = re.sub('/', ' ', Servant)
            # 2 - Il resto con vuoto
            protecc = re.sub('[^a-zA-Z0-9 \n\.]', '', protecc)
            Servant = re.sub('[^a-zA-Z0-9 \n\.]', '', Servant)
            # 3 Multipli spaces
            protecc = re.sub(' +', ' ', protecc)
            Servant = re.sub(' +', ' ', Servant)
                
            # Verifico se corrisponde
            if findWholeWord(protecc, Servant):

                # Verifica se l'account è registrato nel db
                CheckUser(ID_User, Username)

                # Aggiungo la waifu all'harem dell'utente
                # Verifico se l'utente ha già protetto questa waifu
                mycursor.execute("""SELECT *
                                    FROM relations
                                    WHERE ID_User= %s AND
                                    ID_Supergruppo = %s AND
                                    ID_Waifu = %s
                                    """, (ID_User, ID_Supergruppo, ID_Waifu,))
                data = mycursor.fetchone()
                # if - Se esiste aggiungo un NP
                # else - Se non esiste creo la relazione
                if data:
                    mycursor.execute("""UPDATE relations
                                        SET NP = NP + 1
                                        WHERE ID_User= %s AND
                                        ID_Supergruppo = %s AND
                                        ID_Waifu = %s
                                        """, (ID_User, ID_Supergruppo, ID_Waifu,))
                else:
                    # Cerco il numero di relazione strette finora dall'utente
                    mycursor.execute("""SELECT count(*)
                                        FROM relations
                                        WHERE ID_User = %s AND
                                        ID_Supergruppo = %s""",
                                     (ID_User, ID_Supergruppo,))
                    data = mycursor.fetchone()
                    NUMERO_RELAZIONI = data[0]

                    # Setto i dati della nuova relazione
                    mycursor.execute("INSERT INTO relations(ID_User, ID_Supergruppo, ID_Waifu, NP, Place) "
                                     "VALUES(%s, %s, %s, 1, %s)",
                                     (ID_User, ID_Supergruppo, ID_Waifu, NUMERO_RELAZIONI + 1,))

                # Chiudo la partita e ripristino il timer dei messaggi
                mycursor.execute("""UPDATE management
                                    SET Time_mess = Time_reset,
                                    Started = 0,
                                    ID_Waifu = NULL
                                    WHERE ID_Supergruppo = %s""",
                                 (ID_Supergruppo,))

                # Avverto che è riuscito ad ottenere il servant
                context.bot.send_message(chat_id=ID_Supergruppo, text="OwO <b>Hai protetto</b>" + original_Servant +
                                                                     ". Questa waifu è stata aggiunta al tuo harem.", parse_mode='HTML',
                                         reply_to_message_id=ID_Mess)
                return
        # Avverto l'errore e aggiorno il gruppo
        update.message.reply_text("Nope, non è giusto...")
        UpdateGroup(ID_Supergruppo, context)
    else:
        # Aggiorna i dati gruppo
        UpdateGroup(ID_Supergruppo, context)


# Lista servants
def haremfatewaifugram(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)
    Supergruppo_nome = str(update.message.chat.title)
    ID_User = str(update.message.from_user.id)
    ID_Mess = int(update.message.message_id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)

    # Cerco le relazioni
    mycursor.execute("""SELECT relations.Place, waifu.Nome_Waifu, relations.NP 
                        FROM waifu, relations
                        WHERE relations.ID_User= %s AND
                        relations.ID_Supergruppo = %s AND
                        relations.ID_Waifu= waifu.ID_Waifu
                        ORDER BY Place asc 
                        LIMIT 21""",
                     (ID_User, ID_Supergruppo,))
    data = mycursor.fetchall()
    # Formulo la lista
    if data:
        i = 0
        Harem = ""
        for row in data:
            i += 1
            Harem = str(Harem + str(row[0]) + ". " + row[1] + " NP" + str(row[2]) + "\n")
            if i == 20:
                break

        # Formulo il resto del messaggio
        Username = str(update.message.from_user.username)
        Harem = Username + "'s harem in " + Supergruppo_nome + "\n\n" + Harem

        # Rimuovo precedente messaggio harem se esiste
        mycursor.execute("""SELECT Mess_ID_List
                            FROM harem
                            WHERE ID_User = %s AND
                            ID_Supergruppo = %s""",
                         (ID_User, ID_Supergruppo,))
        data = mycursor.fetchone()
        if data:
            try:
                context.bot.delete_message(ID_Supergruppo, message_id=data[0])
            except:
                pass

        # Conto quante relazioni ha l'utente
        mycursor.execute("""SELECT count(*)
                                FROM waifu, relations
                                WHERE relations.ID_User= %s AND
                                relations.ID_Supergruppo = %s AND
                                relations.ID_Waifu = waifu.ID_Waifu""",
                         (ID_User, ID_Supergruppo,))
        data = mycursor.fetchone()
        NUMERO_RELAZIONI = data[0]

        # Se esistono più di 20 relazioni aggiungo i bottoni, altrimenti no
        if NUMERO_RELAZIONI > 20:
            # Creazione pulsanti callback
            keyboard = [[InlineKeyboardButton('⏩', callback_data='Next-0')]]
            """keyboard = [[InlineKeyboardButton('⏪', callback_data='Before'),
                         InlineKeyboardButton('⏩', callback_data='Next')]]"""
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = ""

        # Prendo il Servant preferito
        mycursor.execute("""SELECT PATH_IMG
                            FROM waifu, relations, harem
                            WHERE relations.ID_User= %s AND
                            relations.ID_Supergruppo = %s AND
                            relations.ID_Waifu = waifu.ID_Waifu AND
                            harem.Favorite_Servant = waifu.ID_Waifu AND
                            harem.ID_Supergruppo = relations.ID_Supergruppo AND
                            harem.ID_User = relations.ID_User
                            """,
                         (ID_User, ID_Supergruppo,))
        data = mycursor.fetchone()
        # Se non ha un servant preferito stabilito prendo il primo in lista
        if data:
            PATH_IMG = data[0]
        else:
            mycursor.execute("""SELECT PATH_IMG
                                FROM relations, waifu 
                                WHERE relations.ID_Supergruppo = %s
                                AND relations.ID_User = %s
                                AND relations.ID_Waifu = waifu.ID_Waifu
                                AND relations.Place = 1""",
                             (ID_Supergruppo, ID_User,))
            data = mycursor.fetchone()
            PATH_IMG = data[0]

        Mess_ID_List = context.bot.send_document(chat_id=ID_Supergruppo, document=open(PATH_IMG, 'rb'),
                                                 reply_markup=reply_markup, caption=Harem, reply_to_message_id=ID_Mess)
        # Inserisco il Mess_ID della sua lista nei dati utente
        # Se esiste una sua scheda messaggi la aggiorno
        # Altrimenti la creo
        CheckMessages(ID_Supergruppo, ID_User, Mess_ID_List.message_id)
        # Aggiorno le info dell'utente (Username)
        CheckUser(ID_User, Username)
    else:
        update.message.reply_text("You haven't protecc'd any servant yet...")


def PageSelection(update: Update, context: CallbackContext):
    # Raccolgo dati utente
    ID_User = str(update.callback_query.from_user.id)
    ID_Supergruppo = str(update.callback_query.message.chat.id)
    Mess_ID = update.callback_query.message.message_id

    # Verifico se è il proprietario del messaggio
    if VerifyListIdentity(Mess_ID, ID_Supergruppo, ID_User):
        # Raccolgo dati supplementari per la creazione del nuovo messaggio
        Username = str(update.callback_query.from_user.username)
        Supergruppo_nome = str(update.callback_query.message.chat.title)

        # Raccolgo la richiesta del callback
        CallBackRequest = str(update.callback_query.data)
        CallBackRequest = CallBackRequest.split("-")
        Request = str(CallBackRequest[0])
        Page_contents = int(CallBackRequest[1])

        # Verifico la richiesta
        if Request == "Before":
            New_Page = Page_contents - 20

        elif Request == "Next":
            New_Page = Page_contents + 20
        else:
            New_Page = 0

        # Richiedo la pagina e relativi dati al db
        mycursor.execute("""SELECT relations.Place, waifu.Nome_Waifu, relations.NP 
                                    FROM waifu, relations
                                    WHERE relations.ID_User= %s AND
                                    relations.ID_Supergruppo = %s AND
                                    relations.ID_Waifu = waifu.ID_Waifu AND
                                    relations.Place > %s
                                    ORDER BY Place asc
                                    LIMIT 20""",
                         (ID_User, ID_Supergruppo, New_Page,))
        data = mycursor.fetchall()
        # Creazione del messaggio sfruttando 20 righe
        if data:
            i = 0
            Harem = ""
            for row in data:
                i += 1
                Harem = str(Harem + str(row[0]) + ". " + row[1] + " NP" + str(row[2]) + "\n")
                if i == 20:
                    break

            # Formulo il messaggio
            Harem = Username + "'s harem in " + Supergruppo_nome + "\n\n" + Harem

            # Verifico quali bottoni è necessario implementare per il nuovo messaggio

            # |NEXT| - Conto quante relazioni ha l'utente da un numero di partenza
            mycursor.execute("""SELECT COUNT(*) 
                                    FROM ( 
                                        SELECT relations.ID_Waifu
        	                            FROM waifu, relations
        	                            WHERE relations.ID_User= %s AND
        	                            relations.ID_Supergruppo = %s AND
        	                            relations.Place > %s + 20 AND
        	                            relations.ID_Waifu = waifu.ID_Waifu
        	                            LIMIT 20
                                        ) AS count""",
                             (ID_User, ID_Supergruppo, New_Page,))
            data = mycursor.fetchone()
            AFTER = data[0]

            # |BEFORE| - Conto quante relazioni ha l'utente da un numero di partenza
            # if - Se la pagina è 0 significa che siamo alla prima, quindi limitiamo il before
            if New_Page != 0:
                mycursor.execute("""SELECT COUNT(*) 
                                                FROM ( 
                                                    SELECT relations.ID_Waifu
                    	                            FROM waifu, relations
                    	                            WHERE relations.ID_User= %s AND
                    	                            relations.ID_Supergruppo = %s AND
                    	                            relations.Place > %s - 20 AND
                    	                            relations.ID_Waifu = waifu.ID_Waifu
                    	                            LIMIT 20
                                                    ) AS count""",
                                 (ID_User, ID_Supergruppo, New_Page,))
                data = mycursor.fetchone()
                BEFORE = data[0]
            else:
                BEFORE = 0

            # Aggiungo i bottoni
            if AFTER and BEFORE:
                keyboard = [[InlineKeyboardButton('⏪', callback_data='Before-' + str(New_Page)),
                             InlineKeyboardButton('⏩', callback_data='Next-' + str(New_Page))]]
            elif AFTER:
                keyboard = [[InlineKeyboardButton('⏩', callback_data='Next-' + str(New_Page))]]
            elif BEFORE:
                keyboard = [[InlineKeyboardButton('⏪', callback_data='Before-' + str(New_Page))]]
            else:
                keyboard = ""
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Invio definitivamente la lista aggiornata
            context.bot.edit_message_caption(chat_id=ID_Supergruppo, message_id=Mess_ID, reply_markup=reply_markup,
                                             caption=Harem)
    else:
        update.callback_query.answer(text="That's not your harem...")


# Classifica dei 10 utenti con più servants
def topfatewaifugram(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)

    # Cerco tutti gli utenti registrati in uqesto gruppo con un harem
    mycursor.execute(
        """SELECT users.Username, sum(relations.NP) as MAX_NP
            FROM relations, users, waifu, supergruppo
            WHERE relations.ID_Supergruppo=%s  
            AND relations.ID_Supergruppo = supergruppo.ID_Supergruppo 
            AND relations.ID_User = users.ID_User 
            AND relations.ID_Waifu = waifu.ID_Waifu
            GROUP BY relations.ID_User
            ORDER BY MAX_NP DESC
            LIMIT 10""", (ID_Supergruppo,))
    data = mycursor.fetchall()

    # Formulo la lista
    # Ordinati per np
    if data:
        i = 0
        Harem = ""
        for row in data:
            i += 1
            Harem = str(Harem + str(i) + ". " + str(row[0]) + " -- " + str(row[1]) + "\n")

        # Formulo il resto del messaggio
        Supergruppo_nome = str(update.message.chat.title)
        Harem = "Top harems in " + Supergruppo_nome + "\n\n" + Harem

        # Invio il messaggio
        update.message.reply_text(Harem)
    else:
        update.message.reply_text("rip, there are no harems in this group...")


# Cambia tempo spawn
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
            if 10 <= NewTime <= 20:
                mycursor.execute("""UPDATE management
                                    SET Time_reset = %s
                                    WHERE ID_Supergruppo = %s
                                    """, (NewTime, ID_Supergruppo,))
                update.message.reply_text(
                    "Tempo cambiato!\nStart from the next every servant will appear after " + str(NewTime) + " messages")
            else:
                update.message.reply_text("No, non è giusto...\nIl nuovo tempo deve essere tra 100 e 10000")
        except:
            update.message.reply_text("No, non è giusto...\nControlla come usare correttamente il tasto")
    else:
        update.message.reply_text("Mi spiace, non hai i permessi per usare questo comando...")


# Scambia servant
def tradeservant(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)
    ID_User_1 = int(update.message.from_user.id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)

    # Prendo il messaggio
    NewTrade = update.message.text

    # Rimozione comando dal messaggio
    NewTrade = str(NewTrade.partition(' ')[2])

    # Verifico se esiste testo dopo il comando
    if NewTrade:
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
                    NewTrade = NewTrade.split(" ")

                    # Salvo i 2 numeri trade
                    Trade_1 = ""
                    Trade_2 = ""
                    try:
                        Trade_1 = int(NewTrade[0])
                        Trade_2 = int(NewTrade[1])
                    except:
                        pass

                    # Verifico che entrambi i numeri siano stati dati
                    if Trade_1 and Trade_2:

                        # Verifico se esiste un altro trade e nel caso eliminarlo
                        mycursor.execute("""SELECT Mess_ID_Trade
                                            FROM trades
                                            WHERE ID_User_1 = %s AND
                                            ID_Supergruppo = %s""",
                                         (ID_User_1, ID_Supergruppo))
                        data = mycursor.fetchone()
                        if data:
                            try:
                                # Rimuovo il vecchio trade
                                mycursor.execute("""DELETE FROM trades WHERE ID_Supergruppo = %s AND ID_User_1=%s""",
                                                 (ID_Supergroup,
                                                  ID_User_1,))

                                # Cancello il vecchio messaggio
                                context.bot.delete_message(ID_Supergroup, message_id=data[0])
                            except:
                                pass

                        # Verifico l'identità dei 2 servant
                        # Se non esistono invio l'avviso
                        mycursor.execute("""SELECT Nome_Waifu
                                                                        FROM relations, waifu 
                                                                        WHERE relations.ID_Supergroup = %s
                                                                        AND relations.ID_User = %s
                                                                        AND relations.ID_Waifu = waifu.ID_Waifu
                                                                        AND relations.Place = %s""",
                                         (ID_Supergroup, ID_User_1, Trade_1,))
                        data = mycursor.fetchone()
                        if data:
                            Name_Servant_1 = data[0]
                            mycursor.execute("""SELECT Nome_Waifu
                                                                            FROM relations, waifu 
                                                                            WHERE relations.ID_Supergroup = %s
                                                                            AND relations.ID_User = %s
                                                                            AND relations.ID_Waifu = waifu.ID_Waifu
                                                                            AND relations.Place = %s""",
                                             (ID_Supergroup, ID_User_2, Trade_2,))
                            data = mycursor.fetchone()
                            if data:
                                Name_Servant_2 = data[0]

                                # Creo i pulsanti
                                keyboard = [[InlineKeyboardButton('No :(', callback_data='No@FateWaifugram_Bot'),
                                             InlineKeyboardButton('Yes!', callback_data='Yes@FateWaifugram_Bot')],
                                            [InlineKeyboardButton('Quit', callback_data='Quit@FateWaifugram_Bot')]]
                                reply_markup = InlineKeyboardMarkup(keyboard)

                                # Recupero gli Username per la creazione del messaggio
                                Username_1 = str(update.message.from_user.username)
                                Username_2 = str(update.message.reply_to_message.from_user.username)

                                # Invio il messaggio
                                Mess_ID_Trade = context.bot.send_message(
                                    text="Ti è stato offerto uno scmabio!\n\n" +
                                         Username_1 + " vuole la tua waifu " + Name_Servant_2 +
                                         "\nin cambio, ti vuole dare " + Name_Servant_1 +
                                         "\nAccetti lo scambio, " + Username_2 + "?"
                                    , chat_id=ID_Supergroup,
                                    reply_to_message_id=ID_Mess,
                                    reply_markup=reply_markup)

                                # Digito i dati nel db
                                mycursor.execute(
                                    "INSERT INTO trades"
                                    "(ID_Supergroup, Mess_ID_Trade, ID_User_1, ID_User_2, Trade_1, Trade_2)"
                                    "VALUES(%s,%s,%s,%s,%s,%s)",
                                    (ID_Supergroup, Mess_ID_Trade.message_id, ID_User_1, ID_User_2, Trade_1, Trade_2))

                                return
                            else:
                                update.message.reply_text(
                                    "Looks like that person doesn't have any servant to trade with...")
                                return
                        else:
                            update.message.reply_text(
                                "Looks like that you don't have any servant to trade with...")
                            return
    # Avverto dell'errore
    update.message.reply_text("kek that doesn't look right. <b>Reply</b> to someone like this:\n\n"
                              "<b>/tradeservant</b> <i>{servant number you want to give} {servant number "
                              "you want to take}</i>\n\n"
                              "e.g. <b>/tradeservant 12 8</b>", parse_mode='HTML')


def checktradeservant(update: Update, context: CallbackContext):
    # Raccolgo dati utente
    ID_User = int(update.callback_query.from_user.id)
    ID_Supergroup = str(update.callback_query.message.chat.id)
    Mess_ID_Trade = update.callback_query.message.message_id
    CallBackRequest = str(update.callback_query.data)

    # Verifica che il bottone sia stato premuto da
    # - creatore
    # - partecipante
    # - esterno
    mycursor.execute("""SELECT ID_User_1, ID_User_2
                        FROM trades
                        WHERE ID_Supergroup = %s AND Mess_ID_Trade = %s""", (ID_Supergroup, Mess_ID_Trade,))
    data = mycursor.fetchone()
    ID_User_Trade = [data[0], data[1]]
    if ID_User != ID_User_Trade[0] and ID_User != ID_User_Trade[1]:
        # Avverto che non fa parte dello scambio
        update.callback_query.answer(text="That's not your trade...")
    elif ID_User == ID_User_Trade[0]:
        if CallBackRequest == "Quit@FateWaifugram_Bot":
            # Rimuovo il vecchio trade
            mycursor.execute("""DELETE FROM trades WHERE ID_Supergroup = %s AND Mess_ID_Trade=%s""", (ID_Supergroup,
                                                                                                      Mess_ID_Trade,))
            # Cancello il vecchio messaggio
            try:
                context.bot.delete_message(ID_Supergroup, message_id=Mess_ID_Trade)
            except:
                pass

            # Annullo lo scambio
        else:
            update.callback_query.answer(text="You can't reply your trade...")
            # Avverto che non può rispondere al proprio scambio
    else:
        # Raccolgo la richiesta del callback
        if CallBackRequest == "Yes@FateWaifugram_Bot":
            # Effettuo lo scambio
            # 1 - Rimuovo i rispettivi servant

            # 1.1 - Recupero i place dei servant
            mycursor.execute("""SELECT Trade_1, Trade_2 
                                FROM trades
                                WHERE ID_Supergroup = %s AND Mess_ID_Trade = %s""",
                             (ID_Supergroup, Mess_ID_Trade,))
            data = mycursor.fetchone()
            Trade = [data[0], data[1]]
            NP = []
            ID_Waifu_Trade = []
            i = 0

            for Place in Trade:
                # Verifico se entrambi i servant sono disponibili
                mycursor.execute("""SELECT NP, ID_Waifu
                                    FROM relations
                                    WHERE ID_Supergroup = %s AND ID_User = %s 
                                    AND Place = %s""", (ID_Supergroup, ID_User_Trade[i], Place))

                data = mycursor.fetchone()
                if data:
                    NP.append(data[0])
                    ID_Waifu_Trade.append(data[1])
                else:
                    # Annullo lo scambio ed avverto che uno dei servant non è più disponibile
                    return
                i += 1
            # Abbasso l'NP dei servant coinvolti
            # Se raggiungono zero li deleto
            i = 0
            for Place in Trade:
                if NP[i] == 1:
                    # Rimuovo il Servant
                    mycursor.execute("""DELETE FROM relations 
                                        WHERE ID_Supergroup = %s 
                                        AND ID_User = %s
                                        AND Place = %s""", (ID_Supergroup, ID_User_Trade[i], Place,))
                    # Abbasso il place dei successivi
                    mycursor.execute("""UPDATE relations
                                        SET Place = Place - 1
                                        WHERE ID_Supergroup = %s AND
                                        ID_User = %s AND
                                        Place > %s""", (ID_Supergroup, ID_User_Trade[i], Place,))
                else:
                    # Abbasso l'NP
                    mycursor.execute("""UPDATE relations
                                        SET NP = NP - 1
                                        WHERE ID_User= %s AND
                                        ID_Supergroup = %s AND
                                        Place = %s
                                        """, (ID_User_Trade[i], ID_Supergroup, Place,))
                i += 1
            # Aggiungo il servant
            # Se Hanno già il servant aumento l'NP altrimenti aggiungo con insert
            i = 1
            for ID_Waifu in ID_Waifu_Trade:
                # Verifico l'ID della waifu
                # Aggiungo la waifu all'harem dell'utente
                # Verifico se l'utente ha già protetto questa waifu
                mycursor.execute("""SELECT *
                                    FROM relations
                                    WHERE ID_User= %s AND
                                    ID_Supergroup = %s AND
                                    ID_Waifu = %s
                                                    """, (ID_User_Trade[i], ID_Supergroup, ID_Waifu,))
                data = mycursor.fetchone()
                # if - Se esiste aggiungo un NP
                # else - Se non esiste creo la relazione
                if data:
                    mycursor.execute("""UPDATE relations
                                                        SET NP = NP + 1
                                                        WHERE ID_User= %s AND
                                                        ID_Supergroup = %s AND
                                                        ID_Waifu = %s
                                                        """, (ID_User_Trade[i], ID_Supergroup, ID_Waifu,))
                else:
                    # Cerco il numero di relazione strette finora dall'utente
                    mycursor.execute("""SELECT count(*)
                                                        FROM relations
                                                        WHERE ID_User = %s AND
                                                        ID_Supergroup = %s""",
                                     (ID_User_Trade[i], ID_Supergroup,))
                    data = mycursor.fetchone()
                    NUMERO_RELAZIONI = data[0]

                    # Setto i dati della nuova relazione
                    mycursor.execute("INSERT INTO relations(ID_User, ID_Supergroup, ID_Waifu, NP, Place) "
                                     "VALUES(%s, %s, %s, 1, %s)",
                                     (ID_User_Trade[i], ID_Supergroup, ID_Waifu, NUMERO_RELAZIONI + 1,))
                i -= 1
            Username = []
            Name_Servant = []
            i = 0

            # Rimuovo il trade
            mycursor.execute("""DELETE FROM trades WHERE ID_Supergroup = %s AND Mess_ID_Trade=%s""", (ID_Supergroup,
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
        elif CallBackRequest == "No@FateWaifugram_Bot":
            # Rimuovo il trade
            mycursor.execute("""DELETE FROM trades WHERE ID_Supergroup = %s AND Mess_ID_Trade=%s""", (ID_Supergroup,
                                                                                                      Mess_ID_Trade,))
            Username = []
            for ID_User in ID_User_Trade:
                mycursor.execute("""SELECT Username
                                        FROM users
                                        WHERE ID_User = %s""", (ID_User,))
                data = mycursor.fetchone()
                Username.append(data[0])

            update.callback_query.message.edit_text(
                "Ah rip, " + Username[1] + " rejected the trade with " + Username[0])
            # Annullo lo scambio
        elif CallBackRequest == "Quit@FateWaifugram_Bot":
            update.callback_query.answer(text="You can't press this...")


# Scegli servant preferito da tenere in copertina harem
def favoriteservant(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergroup = str(update.message.chat.id)
    ID_User = str(update.message.from_user.id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergroup, context)

    # Rimuovo il comando
    Favorite_Servant = update.message.text
    try:
        # Rimozione comando dal messaggio
        Favorite_Servant = int(Favorite_Servant.partition(' ')[2])

        # Cerco il servant tramite il place dato
        mycursor.execute("""SELECT waifu.ID_Waifu, waifu.Nome_Waifu
                            FROM relations, waifu
                            WHERE relations.ID_Supergroup = %s
                            AND relations.ID_User = %s
                            AND relations.ID_Waifu = waifu.ID_Waifu
                            AND relations.Place = %s""",
                         (ID_Supergroup, ID_User, Favorite_Servant,))
        data = mycursor.fetchone()
        if data:
            ID_Favorite_Servant = data[0]
            Name_Favorite_Servant = data[1]

            # Inserisco il nuovo servant preferito nella table
            mycursor.execute("""UPDATE harem 
                                        SET Favorite_Servant = %s
                                        WHERE ID_Supergroup = %s
                                        AND ID_User = %s""",
                             (ID_Favorite_Servant, ID_Supergroup, ID_User,))

            update.message.reply_text("Ho messo " + Name_Favorite_Servant + " come la tua waifu preferita!")
        else:
            update.message.reply_text("Mi spiace, non c'è nessuna waifu con questo nome nel tuo harem...")
    except:
        update.message.reply_text("No, non è giusto...\n<b>/favoriteservant</b> <i>{id della waifu che vuoi come preferita}</i>", parse_mode='HTML')


# ZONA CHECK
# ---------------------------------------------
def VerifyListIdentity(Mess_ID_List, ID_Supergroup, ID_User):
    # Ricerca master nel DB
    mycursor.execute(
        """SELECT ID_User 
           FROM harem 
           WHERE Mess_ID_List = %s AND 
           ID_Supergroup=%s""", (Mess_ID_List, ID_Supergroup,))
    data = mycursor.fetchone()
    if data:
        Original_ID_User = data[0]
        if int(ID_User) == int(Original_ID_User):
            return True
        else:
            return False


def CheckMessages(ID_Supergroup, ID_User, Mess_ID_List):
    # Inserisco il Mess_ID del suo trade nei dati utente
    mycursor.execute("SELECT ID_User "
                     "FROM harem "
                     "WHERE ID_User=%s AND ID_Supergroup = %s",
                     (ID_User, ID_Supergroup,))
    data = mycursor.fetchone()
    if data:
        # Aggiorno i dati
        mycursor.execute("""UPDATE harem
                            SET Mess_ID_List = %s
                            WHERE ID_Supergroup = %s AND
                            ID_User = %s""", (Mess_ID_List,
                                              ID_Supergroup, ID_User,))
    else:
        # Setto i dati della nuova relazione
        mycursor.execute("INSERT INTO harem(ID_Supergroup, ID_User, Mess_ID_List) "
                         "VALUES(%s, %s, %s)",
                         (ID_Supergroup, ID_User, Mess_ID_List))


# Verifica se l'utente è rgistrato nel db
# if - Nel caso non lo fosse lo registra
# else - Aggiorna lo username se è cambiato
def CheckUser(ID_User, Username):
    # Raccolgo dati utente
    # Cercare se un utente è registrato nel db
    mycursor.execute("SELECT ID_User, Username FROM users WHERE ID_User=" + str(ID_User))
    data = mycursor.fetchone()
    if not data:
        mycursor.execute("INSERT INTO users(ID_User, Username) VALUES(%s,%s)", (ID_User, Username))
    else:
        try:
            old_Username = data[1]
            if Username != old_Username:
                mycursor.execute("""UPDATE users
                                            SET Username = %s
                                            WHERE ID_User = %s""",
                                 (Username, ID_User,))
        except:
            pass


def UpdateGroup(ID_Supergroup, context: CallbackContext):
    # Aggiorno il numero di messaggi prima del prossimo spawn
    mycursor.execute("""SELECT Time_mess, started
                        FROM management
                        WHERE ID_Supergroup = %s""",
                     (ID_Supergroup,))
    data = mycursor.fetchone()
    Time_mess = data[0]
    Started = data[1]

    # Verifico il contatore dei messaggi prima dello spawn della waifu
    if Time_mess == 0:
        if Started:
            mycursor.execute("""UPDATE management
                                SET Time_mess = Time_reset,
                                Started = 0,
                                ID_Waifu = NULL
                                WHERE ID_Supergroup = %s""",
                             (ID_Supergroup,))
            context.bot.send_message(chat_id=ID_Supergroup, text="RIP, la waifu è scappata via...")
        else:
            # Selezionare il valore massimo dell'id servant
            mycursor.execute("""SELECT ID_Waifu
                                FROM waifu
                                ORDER BY ID_Waifu desc""")
            data = mycursor.fetchone()
            MAX_WAIFU_ID = int(data[0])

            # Selezionare randomicamente un id
            ID_WAIFU = random.randrange(1, MAX_WAIFU_ID + 1)

            # Selezionare il servant trovato
            mycursor.execute("""SELECT ID_Waifu, PATH_IMG
                                FROM waifu
                                WHERE ID_Waifu = %s
                                                """, (ID_WAIFU,))
            data = mycursor.fetchone()
            ID_Waifu = data[0]
            PATH_IMG = data[1]

            # Registro il servant nelle impostazioni del gruppo e quindi l'attivazione della partita
            mycursor.execute("""UPDATE management
                                                SET Time_mess = 25,
                                                Started = 1,
                                                ID_Waifu = %s
                                                WHERE ID_Supergroup = %s""",
                             (ID_Waifu, ID_Supergroup,))

            # Avverto agli utenti la comparsa di una waifu
            context.bot.send_photo(chat_id=ID_Supergroup, photo=open(PATH_IMG, 'rb'),
                                   caption="OwO <b>Appare una waifu!</b>\nAggiungila al tuo harem con /protecc <i>nome waifu</i>\n", parse_mode='HTML')
    else:
        mycursor.execute("""UPDATE management
                        SET Time_mess = Time_mess - 1
                        WHERE ID_Supergroup = %s""",
                     (ID_Supergroup,))

        
def findWholeWord(protecc, servant):
    for protecc_word in protecc.split(" "):
        for servant_word in servant.split(" "):
            if protecc_word == servant_word:
                return True
    return False


# ---------------------------------------------
# REGISTRAZIONE NUOVO GRUPPO
def Welcomechat(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergroup = str(update.message.chat.id)
    Supergroup_name = str(update.message.chat.title)
    # Verifico se l'utente entrato è il bot
    if update.message.new_chat_members[0].id == context.bot.id:
        NewGroup(ID_Supergroup, Supergroup_name)
        # Invio informazioni sul bot al gruppo
        update.message.reply_text(text="<b>Ciao chat!</b> Grazie per avermi aggiunto! "
        		 		"Da ora un sacco di waifu bellissime appariranno in questo gruppo "
                                       "Puoi aggiungerle al tuo harem personale indovinando per primo il loro nome\n "
                                       "Scrivi /help per tutte le infromazioni!\n"
                                  , parse_mode='HTML')


def NewGroup(ID_Supergroup, Supergroup_name):
    # Cercare se il gruppo è registrato nel db
    mycursor.execute("SELECT ID_Supergroup FROM supergroups WHERE ID_Supergroup=" + str(ID_Supergroup))
    data = mycursor.fetchone()

    # if - Se il gruppo non è registrato vienne registrato
    # else - iene aggiornato il contatore per lo spawn della waifu
    if not data:
        mycursor.execute("INSERT INTO supergroups(ID_Supergroup, Supergroup_name) VALUES(%s,%s)",
                         (ID_Supergroup, Supergroup_name))
        mycursor.execute(
            "INSERT INTO management(ID_Supergroup, Time_mess, Time_reset, Started) VALUES (%s,%s,%s,%s)",
            (ID_Supergruppo, 1, 100, 0))



#############################################

def main():
    dp = updater.dispatcher
    
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("protecc", proteccservant, Filters.group))
    dp.add_handler(CommandHandler("gruppowaifu", topfatewaifugram, Filters.group & Filters.update.message))
    dp.add_handler(CommandHandler("changetime", changetime, Filters.group & Filters.update.message))
    dp.add_handler(CommandHandler("tradeservant", tradeservant, Filters.group & Filters.update.message))
    dp.add_handler(CommandHandler("favoriteservant", favoriteservant, Filters.group & Filters.update.message))
    dp.add_handler(CallbackQueryHandler(checktradeservant, pattern="No@FateWaifugram_Bot"))
    dp.add_handler(CallbackQueryHandler(checktradeservant, pattern="Yes@FateWaifugram_Bot"))
    dp.add_handler(CallbackQueryHandler(checktradeservant, pattern="Quit@FateWaifugram_Bot"))

    # Gestione lista servants
    dp.add_handler(CommandHandler("listawaifu", haremfatewaifugram, Filters.group & Filters.update.message))
    dp.add_handler(CallbackQueryHandler(PageSelection))

    # Registrazione gruppo
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, callback=Welcomechat))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.group & Filters.update.message, callback=maindef))
    dp.add_handler(MessageHandler(Filters.private & Filters.update.message, callback=private))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
