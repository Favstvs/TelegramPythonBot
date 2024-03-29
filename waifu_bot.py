"""
PROBLEMI CON MYSQL:
-inserire SET FOREIGN_KEY_CHECKS = 0;

caused error "'NoneType' object is not subscriptable"

NOTE E CORREZZIONI:
-Verificare se /gift funziona
-Sistemare creazione dei pulsanti callback in harem()

v. 20 Python-Telegram_Bot:
-TypeError: Updater.__init__() missing 1 required positional argument: 'update_queue'
  sudo pip3 install python-telegram-bot==13.13

DEPRECATION:
-TelegramDeprecationWarning: The @run_async decorator is deprecated. Use the `run_async` parameter of your Handler or `Dispatcher.run_async` instead.
-TelegramDeprecationWarning: Filters.group is deprecated. Use Filters.chat_type.groups instead.
"""
import mysql.connector
import random
import logging
import unidecode
from datetime import datetime, timezone
import re
import time
from telegram.ext import *
from telegram import *
from telegram.ext import MessageHandler, filters

db = mysql.connector.connect(
    host="localhost",
    user="enrico",
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
    update.message.reply_text(text="Questo non è un gruppo dio cane\n"
                                   "Aggiungimi ad un gruppo e fammi amministratore per iniziare\n")
                                 


# INFORMAZIONI SUL BOT
def help(update: Update, context: CallbackContext):
    update.message.reply_text(text="Aggiungi waifu al tuo harem con /protecc <i>nome del personaggio</i>\n"
                                   "/listawaifu per vedere il tuo harem\n"
                                   "/gruppowaifu visualizza gli harem più grandi del gruppo\n"
                                   "/changetime <i>number</i> per cambiare il numero di messaggi per lo spawn"
                                
                              , parse_mode='HTML')


# COMANDI INTERAZIONE CON IL BOT
#############################################

'''
/daily
message.update.date e' con +00:00 alla fine della data (ex: 2023-05-09 22:49:44+00:00)
che rappresenta la time zone UTC, ma genera errore con la data inserita nella tabella sql,
SOLUZIONE: rimuovere la timezone con data_del_messaggio.replace(tzinfo=None) di datetime

ULTIMI DUE PROBLEMI:
-registrare in automatico il Time_Mess nella tabella users del nuovo utente che usa il comando, perche' il mio 
 l'ho inserito manualmente nella tabella sql
 
-sistemare il fuso orario, perche' risulta indietro di 2 ore
 <<orario del messaggio : 2023-05-09 23:09:41
 <<sudo date 
 <<Wed May 10 01:10:47 AM UTC 2023


'''
def daily(update: Update, context: CallbackContext):

    ID_Supergruppo = str(update.message.chat.id)
    ID_User = str(update.message.from_user.id)
    Username = str(update.message.from_user.username)

    UpdateGroup(ID_Supergruppo, context)
    CheckUser(ID_User, Username)
    
    #prendo la data del messaggio
    Time_Mess = update.message.date
    Time_Mess = Time_Mess.replace(tzinfo=None)
   
   

    #estraggo l'ultima data registrata
    mycursor.execute("""SELECT Time_Mess FROM users WHERE ID_User=%s""", (ID_User,))
    data = mycursor.fetchone()
    
    
    #confronto le due date
    
    date_1 = data[0]
    date_2 = Time_Mess
    date_format_str = "%Y-%m-%d %H:%M:%S"
    
    date_1_start = datetime.strptime(str(date_1), date_format_str)
    date_2_end = datetime.strptime(str(date_2), date_format_str)
    
    
    diff = date_2_end - date_1_start
    
    diff_in_hours = diff.total_seconds()/3600   
    
    if diff_in_hours < 5:
 
            mycursor.execute("""UPDATE users SET Coins=Coins+100 WHERE ID_User=%s;""", (ID_User,))
            mycursor.execute("""SELECT Coins FROM users WHERE ID_User=%s""", (ID_User,))
            data = mycursor.fetchone()
            if data: 
                Total_Coins = str(data[0])
                update.message.reply_text("💰 Hai riscattato i coins giornalieri\n\n Ora i tuoi coins totali sono " + Total_Coins + " 🪙 " )
                print("orario del messaggio : " + str(Time_Mess))
                mycursor.execute("""SELECT Time_Mess FROM users WHERE ID_User=%s""", (ID_User,))
                data1 = mycursor.fetchone()
                print("orario dell'ultimo utilizzo del comando : " + str(data1[0]))
    		#inserico la nuova data nella colonna apposita della tabella
                mycursor.execute("""UPDATE users SET Time_Mess=%s WHERE ID_User=%s""", (Time_Mess, ID_User,))
  
    else:
        update.message.reply_text("❌Hai già riscatto i tuoi coins. Devi aspettare 24 ore ")


# Proteggi waifu
def proteccwaifu(update: Update, context: CallbackContext):
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

    # Verifico se c'è una waifu ottenibile nel gruppo
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
            mycursor.execute("""SELECT Nome_Waifu, Nome_Anime
                                        FROM waifu
                                        WHERE ID_Waifu = %s
                                        """, (ID_Waifu,))
            data = mycursor.fetchone()
            original_Waifu = str(data[0])
            nome_anime = str(data[1])
            Waifu = str(data[0]).upper()

            # Rimuovo eventuali lettere accentate da entrambi i nomi
            protecc = unidecode.unidecode(protecc)
            Waifu = unidecode.unidecode(Waifu)

            # Rimuovo eventuali simboli
            # 1 - Sostituisco i trattini con spazi
            protecc = re.sub('-', ' ', protecc)
            Waifu = re.sub('-', ' ', Waifu)
            # 1.2 - Sostituisco gli slash con spazi
            protecc = re.sub('/', ' ', protecc)
            Waifu = re.sub('/', ' ', Waifu)
            # 2 - Il resto con vuoto
            protecc = re.sub('[^a-zA-Z0-9 \n\.]', '', protecc)
            Waifu = re.sub('[^a-zA-Z0-9 \n\.]', '', Waifu)
            # 3 Multipli spaces
            protecc = re.sub(' +', ' ', protecc)
            Waifu = re.sub(' +', ' ', Waifu)
                
            # Verifico se corrisponde
            if findWholeWord(protecc, Waifu):

                # Verifica se l'account è registrato nel db
                CheckUser(ID_User, Username)

                # Aggiungo la waifu all'harem dell'utente
                # Verifico se l'utente ha già protetto questa waifu
                mycursor.execute("""SELECT *
                                    FROM relazioni
                                    WHERE ID_User= %s AND
                                    ID_Supergruppo = %s AND
                                    ID_Waifu = %s
                                    """, (ID_User, ID_Supergruppo, ID_Waifu,))
                data = mycursor.fetchone()
                # if - Se esiste aggiungo un NP
                # else - Se non esiste creo la relazione
                if data:
                    mycursor.execute("""UPDATE relazioni
                                        SET NP = NP + 1
                                        WHERE ID_User= %s AND
                                        ID_Supergruppo = %s AND
                                        ID_Waifu = %s
                                        """, (ID_User, ID_Supergruppo, ID_Waifu,))
                else:
                    # Cerco il numero di relazione strette finora dall'utente
                    mycursor.execute("""SELECT count(*)
                                        FROM relazioni
                                        WHERE ID_User = %s AND
                                        ID_Supergruppo = %s""",
                                     (ID_User, ID_Supergruppo,))
                    data = mycursor.fetchone()
                    NUMERO_RELAZIONI = data[0]

                    # Setto i dati della nuova relazione
                    mycursor.execute("INSERT INTO relazioni (ID_User, ID_Supergruppo, ID_Waifu, NP, Place) "
                                     "VALUES(%s, %s, %s, 1, %s)",
                                     (ID_User, ID_Supergruppo, ID_Waifu, NUMERO_RELAZIONI + 1,))

                # Chiudo la partita e ripristino il timer dei messaggi
                mycursor.execute("""UPDATE management
                                    SET Time_mess = Time_reset,
                                    Started = 0,
                                    ID_Waifu = NULL
                                    WHERE ID_Supergruppo = %s""",
                                 (ID_Supergruppo,))

                # Avverto che è riuscito a proteggere la waifu
                context.bot.send_message(chat_id=ID_Supergruppo, text="✅ OwO <b>Hai protetto</b> " + original_Waifu + " di " + nome_anime + ".\n"
                                                                     "Questa waifu è stata aggiunta al tuo harem.", parse_mode='HTML',
                                         reply_to_message_id=ID_Mess)
                return
        # Avverto l'errore e aggiorno il gruppo
        update.message.reply_text("Nope, non è giusto...")
        UpdateGroup(ID_Supergruppo, context)
    else:
        # Aggiorna i dati gruppo
        UpdateGroup(ID_Supergruppo, context)


# Lista waifu
def harem(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)
    Supergruppo_nome = str(update.message.chat.title)
    ID_User = str(update.message.from_user.id)
    ID_Mess = int(update.message.message_id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)

    # Cerco le relazioni
    mycursor.execute("""SELECT relazioni.Place, waifu.Nome_Waifu, relazioni.NP, waifu.ID_Waifu
                        FROM waifu, relazioni
                        WHERE relazioni.ID_User= %s AND
                        relazioni.ID_Supergruppo = %s AND
                        relazioni.ID_Waifu= waifu.ID_Waifu
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
            Harem = str(Harem + str(row[0]) + ". " + row[1] + " NP: " + str(row[2]) + " ID: " + str(row[3]) + "\n")
            if i == 20:
                break

        # Formulo il resto del messaggio
        Username = str(update.message.from_user.username)
        Harem = "Harem di " + Username + " in " + Supergruppo_nome + "\n\n" + Harem

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
                                FROM waifu, relazioni
                                WHERE relazioni.ID_User= %s AND
                                relazioni.ID_Supergruppo = %s AND
                                relazioni.ID_Waifu = waifu.ID_Waifu""",
                         (ID_User, ID_Supergruppo,))
        data = mycursor.fetchone()
        NUMERO_RELAZIONI = data[0]

        # Se esistono più di 20 relazioni aggiungo i bottoni, altrimenti no
        if NUMERO_RELAZIONI > 20:
            # Creazione pulsanti callback
            keyboard = [[InlineKeyboardButton('⏩', callback_data='Next-0')]]
            """keyboard = [[InlineKeyboardButton('⏪', callback_data='Indietro'),
                         InlineKeyboardButton('⏩', callback_data='Avanti')]]"""
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = ""

        # Prendo la waifu preferita
        mycursor.execute("""SELECT PATH_IMG
                            FROM waifu, relazioni, harem
                            WHERE relazioni.ID_User= %s AND
                            relazioni.ID_Supergruppo = %s AND
                            relazioni.ID_Waifu = waifu.ID_Waifu AND
                            harem.Waifu_Preferita = waifu.ID_Waifu AND
                            harem.ID_Supergruppo = relazioni.ID_Supergruppo AND
                            harem.ID_User = relazioni.ID_User
                            """,
                         (ID_User, ID_Supergruppo,))
        data = mycursor.fetchone()
        # Se non ha una waifu preferita prendo la prima della lista
        if data:
            PATH_IMG = data[0]
        else:
            mycursor.execute("""SELECT PATH_IMG
                                FROM relazioni, waifu 
                                WHERE relazioni.ID_Supergruppo = %s
                                AND relazioni.ID_User = %s
                                AND relazioni.ID_Waifu = waifu.ID_Waifu
                                AND relazioni.Place = 1""",
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
        update.message.reply_text("Non hai ancora protetto nessuna waifu ...")


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
        if Request == "Indietro":
            New_Page = Page_contents - 20

        elif Request == "Avanti":
            New_Page = Page_contents + 20
        else:
            New_Page = 0

        # Richiedo la pagina e relativi dati al db
        mycursor.execute("""SELECT relazioni.Place, waifu.Nome_Waifu, relazioni.NP 
                                    FROM waifu, relazioni
                                    WHERE relazioni.ID_User= %s AND
                                    relazioni.ID_Supergruppo = %s AND
                                    relazioni.ID_Waifu = waifu.ID_Waifu AND
                                    relazioni.Place > %s
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
                                        SELECT relazioni.ID_Waifu
        	                            FROM waifu, relazioni
        	                            WHERE relazioni.ID_User= %s AND
        	                            relazioni.ID_Supergruppo = %s AND
        	                            relazioni.Place > %s + 20 AND
        	                            relazioni.ID_Waifu = waifu.ID_Waifu
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
                                                    SELECT relazioni.ID_Waifu
                    	                            FROM waifu, relazioni
                    	                            WHERE relazioni.ID_User= %s AND
                    	                            relazioni.ID_Supergruppo = %s AND
                    	                            relazioni.Place > %s - 20 AND
                    	                            relazioni.ID_Waifu = waifu.ID_Waifu
                    	                            LIMIT 20
                                                    ) AS count""",
                                 (ID_User, ID_Supergruppo, New_Page,))
                data = mycursor.fetchone()
                BEFORE = data[0]
            else:
                BEFORE = 0

            # Aggiungo i bottoni
            if AFTER and BEFORE:
                keyboard = [[InlineKeyboardButton('⏪', callback_data='Indietro-' + str(New_Page)),
                             InlineKeyboardButton('⏩', callback_data='Avanti-' + str(New_Page))]]
            elif AFTER:
                keyboard = [[InlineKeyboardButton('⏩', callback_data='Avanti-' + str(New_Page))]]
            elif BEFORE:
                keyboard = [[InlineKeyboardButton('⏪', callback_data='Indietro-' + str(New_Page))]]
            else:
                keyboard = ""
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Invio definitivamente la lista aggiornata
            context.bot.edit_message_caption(chat_id=ID_Supergruppo, message_id=Mess_ID, reply_markup=reply_markup,
                                             caption=Harem)
    else:
        update.callback_query.answer(text="Non è il tuo harem...")


# Classifica dei 10 utenti con piu' waifu
def topfatewaifugram(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)

    # Cerco tutti gli utenti registrati in uqesto gruppo con un harem
    mycursor.execute(
        """SELECT users.Username, sum(relazioni.NP) as MAX_NP
            FROM relazioni, users, waifu, supergruppo
            WHERE relazioni.ID_Supergruppo=%s  
            AND relazioni.ID_Supergruppo = supergruppo.ID_Supergruppo 
            AND relazioni.ID_User = users.ID_User 
            AND relazioni.ID_Waifu = waifu.ID_Waifu
            GROUP BY relazioni.ID_User
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
        update.message.reply_text("Spiace, non ci sono harem in sto gruppo...")


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
            if 5 <= NewTime <= 20:
                mycursor.execute("""UPDATE management
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


# Scambia waifu
def tradewaifu(update: Update, context: CallbackContext):
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
                    Scambio_1 = ""
                    Scambio_2 = ""
                    try:
                        Scambio_1 = int(NewTrade[0])
                        Scambio_2 = int(NewTrade[1])
                    except:
                        pass

                    # Verifico che entrambi i numeri siano stati dati
                    if Scambio_1 and Scambio_2:

                        # Verifico se esiste un altro trade e nel caso eliminarlo
                        mycursor.execute("""SELECT Mess_ID_Trade
                                            FROM scambi
                                            WHERE ID_User_1 = %s AND
                                            ID_Supergruppo = %s""",
                                         (ID_User_1, ID_Supergruppo))
                        data = mycursor.fetchone()
                        if data:
                            try:
                                # Rimuovo il vecchio trade
                                mycursor.execute("""DELETE FROM scambi WHERE ID_Supergruppo = %s AND ID_User_1=%s""",
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
                                         (ID_Supergruppo, ID_User_1, Scambio_1,))
                        data = mycursor.fetchone()
                        if data:
                            Name_Waifu_1 = data[0]
                            mycursor.execute("""SELECT Nome_Waifu
                                                                            FROM relazioni, waifu 
                                                                            WHERE relazioni.ID_Supergruppo = %s
                                                                            AND relazioni.ID_User = %s
                                                                            AND relazioni.ID_Waifu = waifu.ID_Waifu
                                                                            AND relazioni.Place = %s""",
                                             (ID_Supergruppo, ID_User_2, Scambio_2,))
                            data = mycursor.fetchone()
                            if data:
                                Name_Waifu_2 = data[0]

                                # Creo i pulsanti
                                keyboard = [[InlineKeyboardButton('No :(', callback_data='No@Waifu_Bot'),
                                             InlineKeyboardButton('Yes!', callback_data='Sì@Waifu_Bot')],
                                            [InlineKeyboardButton('Quit', callback_data='Esci@Waifu_Bot')]]
                                reply_markup = InlineKeyboardMarkup(keyboard)

                                # Recupero gli Username per la creazione del messaggio
                                Username_1 = str(update.message.from_user.username)
                                Username_2 = str(update.message.reply_to_message.from_user.username)

                                # Invio il messaggio
                                Mess_ID_Trade = context.bot.send_message(
                                    text="Ti è stato offerto uno scambio!\n\n" +
                                         Username_1 + " vuole la tua waifu " + Name_Waifu_2 +
                                         "\nin cambio, ti vuole dare " + Name_Waifu_1 +
                                         "\nAccetti lo scambio, " + Username_2 + "?"
                                    , chat_id=ID_Supergruppo,
                                    reply_to_message_id=ID_Mess,
                                    reply_markup=reply_markup)

                                # Digito i dati nel db
                                mycursor.execute(
                                    "INSERT INTO scambi"
                                    "(ID_Supergruppo, Mess_ID_Trade, ID_User_1, ID_User_2, Scambio_1, Scambio_2)"
                                    "VALUES(%s,%s,%s,%s,%s,%s)",
                                    (ID_Supergruppo, Mess_ID_Trade.message_id, ID_User_1, ID_User_2, Scambio_1, Scambio_2))

                                return
                            else:
                                update.message.reply_text(
                                    "Sembra che questo utente non abbia waifu da scambiare..")
                                return
                        else:
                            update.message.reply_text(
                                "Sembra che tu non abbia waifu da scambiare...")
                            return
    # Avverto dell'errore
    update.message.reply_text("Non è proprio giusto. <b>Rispondi</b> a qualcuno così:\n\n"
                              "<b>/tradewaifu</b> <i>{ID della Waifu che vuoi dare} {ID della Waifu che vuoi avere}</i>\n\n"
                              "esempio: <b>/tradewaifu 12 8</b>", parse_mode='HTML')


def checktradewaifu(update: Update, context: CallbackContext):
    # Raccolgo dati utente
    ID_User = int(update.callback_query.from_user.id)
    ID_Supergruppo = str(update.callback_query.message.chat.id)
    Mess_ID_Trade = update.callback_query.message.message_id
    CallBackRequest = str(update.callback_query.data)

    # Verifica che il bottone sia stato premuto da
    # - creatore
    # - partecipante
    # - esterno
    mycursor.execute("""SELECT ID_User_1, ID_User_2
                        FROM scambi
                        WHERE ID_Supergruppo = %s AND Mess_ID_Trade = %s""", (ID_Supergruppo, Mess_ID_Trade))
    data = mycursor.fetchone()
    ID_User_Trade = [data[0], data[1]]
    if ID_User != ID_User_Trade[0] and ID_User != ID_User_Trade[1]:
        # Avverto che non fa parte dello scambio
        update.callback_query.answer(text="Questo non è il tuo scambio...")
    elif ID_User == ID_User_Trade[0]:
        if CallBackRequest == "Esci@Waifu_Bot":
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
        if CallBackRequest == "Sì@Waifu_Bot":
            # Effettuo lo scambio
            # 1 - Rimuovo le rispettive waifu dal db

            # 1.1 - Recupero i place delle waifu
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
                # Controllo se entrambe le waifu sono disponibili
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
            # Abbasso l'NP delle waifu coinvolte
            # Se raggiungono zero li deleto
            i = 0
            for Place in Trade:
                if NP[i] == 1:
                    # Rimuovo la waifu dalla tabella
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
            # Aggiungo la waifu
            # Se hanno già la stessa waifu aumento NP altrimenti aggiungo con insert
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
            Name_Waifu = []
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
                Name_Waifu.append(data[0])
                i += 1
            # Invio messaggio in cui confermo il trade
            update.callback_query.message.edit_text("OwO lo scambio è completato!\n\n" + Username[0] + " ha dato " +
                                                    Name_Waifu[0] + " a " + Username[1] + "\ne\n" +
                                                    Username[1] + " ha dato " +
                                                    Name_Waifu[1] + " a " + Username[0])
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
        elif CallBackRequest == "Esci@Waifu_Bot":
            update.callback_query.answer(text="Non puoi premere questo...")
            
            
def gift(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)
    ID_User_1 = int(update.message.from_user.id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)

    # Prendo il messaggio
    NewGift = update.message.text

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
                        # Verifico se esiste un altro regalo e nel caso eliminarlo
                        mycursor.execute("""SELECT Mess_ID_Gift
                                            FROM regali
                                            WHERE ID_User_1 = %s AND
                                            ID_Supergruppo = %s""",
                                         (ID_User_1, ID_Supergruppo))
                        data = mycursor.fetchone()
                        if data:
                            try:
                                # Rimuovo il vecchio regalo
                                mycursor.execute("""DELETE FROM regali WHERE ID_Supergruppo = %s AND ID_User_1=%s""",
                                                 (ID_Supergruppo,
                                                  ID_User_1,))

                                # Cancello il vecchio messaggio
                                context.bot.delete_message(ID_Supergruppo, message_id=data[0])
                            except:
                                pass

                        # Verifico l'identità della waifu
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
                            Name_Waifu_1 = data[0]
                            '''
                            mycursor.execute("""SELECT Nome_Waifu
                                                                            FROM relazioni, waifu 
                                                                            WHERE relazioni.ID_Supergruppo = %s
                                                                            AND relazioni.ID_User = %s
                                                                            AND relazioni.ID_Waifu = waifu.ID_Waifu
                                                                            AND relazioni.Place = %s""",
                                             (ID_Supergruppo, ID_User_2, Scambio_2,))
                            data = mycursor.fetchone()
                            if data:
                                Name_Waifu_2 = data[0]
                            '''

                                # Creo i pulsanti
                            keyboard = [[InlineKeyboardButton('No :(', callback_data='No@Waifu_Bot'),
                                         InlineKeyboardButton('Sì!', callback_data='Sì@Waifu_Bot')],
                                         [InlineKeyboardButton('Esci', callback_data='Esci@Waifu_Bot')]]
                            reply_markup = InlineKeyboardMarkup(keyboard)

                                # Recupero gli Username per la creazione del messaggio
                            Username_1 = str(update.message.from_user.username)
                            Username_2 = str(update.message.reply_to_message.from_user.username)

                                # Invio il messaggio
                            Mess_ID_Gift= context.bot.send_message(
                                    text="Ti è stato offerto un regalo!\n\n" +
                                          Username_1 + " vuole darti la sua waifu " + Name_Waifu_1 + "\n"
                                         "Accetti il regalo, " + Username_2 + "?"
                                    , chat_id=ID_Supergruppo,
                                    reply_to_message_id=ID_Mess,
                                    reply_markup=reply_markup)

                                # Digito i dati nel db
                            mycursor.execute(
                                    "INSERT INTO regali"
                                    "(ID_Supergruppo, Mess_ID_Gift, ID_User_1, ID_User_2, Regalo)"
                                    "VALUES(%s,%s,%s,%s,%s)",
                                    (ID_Supergruppo, Mess_ID_Gift.message_id, ID_User_1, ID_User_2, Regalo))

                            return
                        else:
                                update.message.reply_text(
                                    "Sembra che questo utente non abbia waifu da regalare..")
                                return
                    else:
                           update.message.reply_text(
                               "Sembra che tu non abbia waifu da regalare...")
                           return
    # Avverto dell'errore
    update.message.reply_text("Non è proprio giusto. <b>Rispondi</b> a qualcuno così:\n\n"
                              "<b>/gift</b> <i>{ID della Waifu che vuoi dare}</i>\n\n"
                              "esempio: <b>/gift 10</b>", parse_mode='HTML')


def checkgift(update: Update, context: CallbackContext):
    # Raccolgo dati utente
    ID_User = int(update.callback_query.from_user.id)
    ID_Supergruppo = str(update.callback_query.message.chat.id)
    Mess_ID_Gift = update.callback_query.message.message_id
    CallBackRequest = str(update.callback_query.data)

    mycursor.execute("""SELECT ID_User_1, ID_User_2
                        FROM regali
                        WHERE ID_Supergruppo = %s AND Mess_ID_Gift = %s""", (ID_Supergruppo, Mess_ID_Gift))
    data = mycursor.fetchone()
    ID_User_Gift = [data[0], data[1]]
    if ID_User != ID_User_Gift[0] and ID_User != ID_User_Gift[1]:
        # Avverto che non fa parte del regalo
        update.callback_query.answer(text="Questo regalo non è per te...")
    elif ID_User == ID_User_Gift[0]:
        if CallBackRequest == "Esci@Waifu_Bot":
            # Rimuovo il vecchio regalo
            mycursor.execute("""DELETE FROM regali WHERE ID_Supergruppo = %s AND Mess_ID_Gift=%s""", (ID_Supergruppo,
                                                                                                      Mess_ID_Gift,))
            # Cancello il vecchio messaggio
            try:
                context.bot.delete_message(ID_Supergruppo, message_id=Mess_ID_Gift)
            except:
                pass

            # Annullo il regalo
        else:
            update.callback_query.answer(text="Non puoi rispondere al tuo stesso regalo...")
            # Avverto che non può rispondere al proprio scambio
    else:
        # Raccolgo la richiesta del callback
        if CallBackRequest == "Sì@Waifu_Bot":
            # Effettuo il regalo
            # 1 - Rimuovo la waifu regalata

            # 1.1 - Recupero i place della waifu
            mycursor.execute("""SELECT Regalo 
                                FROM regali
                                WHERE ID_Supergruppo = %s AND Mess_ID_Gift = %s""",
                             (ID_Supergruppo, Mess_ID_Gift,))
            data = mycursor.fetchone()
            Gift = data[0]
            NP = []
            ID_Waifu_Gift = []
            i = 0

            for Place in Gift:
                # Verifico se la waifu e' disponibile
                mycursor.execute("""SELECT NP, ID_Waifu
                                    FROM relazioni
                                    WHERE ID_Supergruppo = %s AND ID_User = %s 
                                    AND Place = %s""", (ID_Supergruppo, ID_User_Gift[i], Place))

                data = mycursor.fetchone()
                if data:
                    NP.append(data[0])
                    ID_Waifu_Gift.append(data[1])
                else:
                    # Annullo lo scambio ed avverto che una delle waifu non è più disponibile
                    return
                i += 1
            # Abbasso l'NP della waifu
            # Se raggiungono zero li deleto
            i = 0
            for Place in Gift:
                if NP[i] == 1:
                    # Rimuovo la waifu
                    mycursor.execute("""DELETE FROM relazioni 
                                        WHERE ID_Supergruppo = %s 
                                        AND ID_User = %s
                                        AND Place = %s""", (ID_Supergruppo, ID_User_Gift[i], Place,))
                    # Abbasso il place dei successivi
                    mycursor.execute("""UPDATE relazioni
                                        SET Place = Place - 1
                                        WHERE ID_Supergruppo = %s AND
                                        ID_User = %s AND
                                        Place > %s""", (ID_Supergruppo, ID_User_Gift[i], Place,))
                else:
                    # Abbasso l'NP
                    mycursor.execute("""UPDATE relazioni
                                        SET NP = NP - 1
                                        WHERE ID_User= %s AND
                                        ID_Supergruppo = %s AND
                                        Place = %s
                                        """, (ID_User_Gift[i], ID_Supergruppo, Place,))
                i += 1
            # Aggiungo la waifu
            # Se Hanno già la waifu aumento l'NP altrimenti aggiungo con insert
            i = 1
            for ID_Waifu in ID_Waifu_Gift:
                # Verifico l'ID della waifu
                # Aggiungo la waifu all'harem dell'utente
                # Verifico se l'utente ha già protetto questa waifu
                mycursor.execute("""SELECT *
                                    FROM relazioni
                                    WHERE ID_User= %s AND
                                    ID_Supergruppo = %s AND
                                    ID_Waifu = %s
                                                    """, (ID_User_Gift[i], ID_Supergruppo, ID_Waifu,))
                data = mycursor.fetchone()
                # if - Se esiste aggiungo un NP
                # else - Se non esiste creo la relazione
                if data:
                    mycursor.execute("""UPDATE relazioni
                                                        SET NP = NP + 1
                                                        WHERE ID_User= %s AND
                                                        ID_Supergruppo = %s AND
                                                        ID_Waifu = %s
                                                        """, (ID_User_Gift[i], ID_Supergruppo, ID_Waifu,))
                else:
                    # Cerco il numero di relazione strette finora dall'utente
                    mycursor.execute("""SELECT count(*)
                                                        FROM relazioni
                                                        WHERE ID_User = %s AND
                                                        ID_Supergruppo = %s""",
                                     (ID_User_Gift[i], ID_Supergruppo,))
                    data = mycursor.fetchone()
                    NUMERO_RELAZIONI = data[0]

                    # Setto i dati della nuova relazione
                    mycursor.execute("INSERT INTO relazioni(ID_User, ID_Supergruppo, ID_Waifu, NP, Place) "
                                     "VALUES(%s, %s, %s, 1, %s)",
                                     (ID_User_Gift[i], ID_Supergruppo, ID_Waifu, NUMERO_RELAZIONI + 1,))
                i -= 1
            Username = []
            Name_Waifu = []
            i = 0

            # Rimuovo il regalo
            mycursor.execute("""DELETE FROM regali WHERE ID_Supergruppo = %s AND Mess_ID_Gift=%s""", (ID_Supergruppo,
                                                                                                      Mess_ID_Gift,))

            for ID_User in ID_User_Gift:
                mycursor.execute("""SELECT Username
                                        FROM users
                                        WHERE ID_User = %s""", (ID_User,))
                data = mycursor.fetchone()
                Username.append(data[0])
                mycursor.execute("""SELECT Nome_Waifu
                                        FROM waifu
                                        WHERE ID_Waifu = %s""", (ID_Waifu_Gift[i],))
                data = mycursor.fetchone()
                Name_Waifu.append(data[0])
                i += 1
            # Invio messaggio in cui confermo il regalo
            update.callback_query.message.edit_text("OwO il regalo è completato!\n\n" + Username[0] + " ha dato " +
                                                    Name_Waifu[0] + " a " + Username[1])
        elif CallBackRequest == "No@Waifu_Bot":
            # Rimuovo il regalo
            mycursor.execute("""DELETE FROM regali WHERE ID_Supergruppo = %s AND Mess_ID_Gift=%s""", (ID_Supergruppo,
                                                                                                      Mess_ID_Gift,))
            Username = []
            for ID_User in ID_User_Gift:
                mycursor.execute("""SELECT Username
                                        FROM users
                                        WHERE ID_User = %s""", (ID_User,))
                data = mycursor.fetchone()
                Username.append(data[0])

            update.callback_query.message.edit_text(
                "Ahhh niente, " + Username[1] + " ha rifiutato il regalo di  " + Username[0])
            # Annullo il regalo
        elif CallBackRequest == "Esci@Waifu_Bot":
            update.callback_query.answer(text="Non puoi premere questo...")


# Scegli waifu preferita da tenere in copertina harem
def favoritewaifu(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)
    ID_User = str(update.message.from_user.id)

    # Aggiorna i dati gruppo
    UpdateGroup(ID_Supergruppo, context)

    # Rimuovo il comando
    Favorite_Waifu = update.message.text
    try:
        # Rimozione comando dal messaggio
        Favorite_Waifu = int(Favorite_Waifu.partition(' ')[2])

        # Cerco la waifu tramite il place dato
        mycursor.execute("""SELECT waifu.ID_Waifu, waifu.Nome_Waifu
                            FROM relazioni, waifu 
                            WHERE relazioni.ID_Supergruppo = %s
                            AND relazioni.ID_User = %s
                            AND relazioni.ID_Waifu = waifu.ID_Waifu
                            AND relazioni.Place = %s""",
                         (ID_Supergruppo, ID_User, Favorite_Waifu))
        data = mycursor.fetchone()
        if data:
            ID_Favorite_Waifu = data[0]
            Name_Favorite_Waifu = data[1]

            # Inserisco la nuova waifu preferita nella table
            mycursor.execute("""UPDATE harem 
                                        SET Waifu_Preferita = %s
                                        WHERE ID_Supergruppo = %s
                                        AND ID_User = %s""",
                             (ID_Favorite_Waifu, ID_Supergruppo, ID_User))

            update.message.reply_text("Ho messo " + Name_Favorite_Waifu + " come waifu preferita")
        else:
            update.message.reply_text("rip, non c'è una waifu con questo id nel tuo harem...")
    except:
        update.message.reply_text("rip, non è giusto...\n<b>/favoritewaifu</b> <i>{numero id waifu "
                                  "come preferita}</i>", parse_mode='HTML')

    

# ZONA CHECK
# ---------------------------------------------
def VerifyListIdentity(Mess_ID_List, ID_Supergruppo, ID_User):
    # Ricerca master nel DB
    mycursor.execute(
        """SELECT ID_User 
           FROM harem 
           WHERE Mess_ID_List = %s AND 
           ID_Supergruppo=%s""", (Mess_ID_List, ID_Supergruppo,))
    data = mycursor.fetchone()
    if data:
        Original_ID_User = data[0]
        if int(ID_User) == int(Original_ID_User):
            return True
        else:
            return False


def CheckMessages(ID_Supergruppo, ID_User, Mess_ID_List):
    # Inserisco il Mess_ID del suo trade nei dati utente
    mycursor.execute("SELECT ID_User "
                     "FROM harem "
                     "WHERE ID_User=%s AND ID_Supergruppo = %s",
                     (ID_User, ID_Supergruppo,))
    data = mycursor.fetchone()
    if data:
        # Aggiorno i dati
        mycursor.execute("""UPDATE harem
                            SET Mess_ID_List = %s
                            WHERE ID_Supergruppo = %s AND
                            ID_User = %s""", (Mess_ID_List,
                                              ID_Supergruppo, ID_User,))
    else:
        # Setto i dati della nuova relazione
        mycursor.execute("INSERT INTO harem(ID_Supergruppo, ID_User, Mess_ID_List) "
                         "VALUES(%s, %s, %s)",
                         (ID_Supergruppo, ID_User, Mess_ID_List))


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


def UpdateGroup(ID_Supergruppo, context: CallbackContext):
    # Aggiorno il numero di messaggi prima del prossimo spawn
    mycursor.execute("""SELECT Time_mess, Started
                        FROM management
                        WHERE ID_Supergruppo = %s""",
                     (ID_Supergruppo,))
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
                                WHERE ID_Supergruppo = %s""",
                             (ID_Supergruppo,))
            context.bot.send_message(chat_id=ID_Supergruppo, text="RIP, la waifu è scappata via...")
        else:
            # Selezionare il valore massimo dell'id waifu
            mycursor.execute("""SELECT ID_Waifu
                                FROM waifu
                                ORDER BY ID_Waifu desc""")
            data = mycursor.fetchone()
            MAX_WAIFU_ID = int(data[0])

            # Selezionare randomicamente un id
            ID_WAIFU = random.randrange(1, MAX_WAIFU_ID + 1)

            # Selezionare la waifu trovata
            mycursor.execute("""SELECT ID_Waifu, PATH_IMG
                                FROM waifu
                                WHERE ID_Waifu = %s
                                                """, (ID_WAIFU,))
            data = mycursor.fetchone()
            ID_Waifu = data[0]
            PATH_IMG = data[1]

            # Registro la waifu nelle impostazioni del gruppo e quindi l'attivazione della partita
            mycursor.execute("""UPDATE management
                                                SET Time_mess = 25,
                                                Started = 1,
                                                ID_Waifu = %s
                                                WHERE ID_Supergruppo = %s""",
                             (ID_Waifu, ID_Supergruppo,))

            # Avverto agli utenti la comparsa di una waifu
            context.bot.send_photo(chat_id=ID_Supergruppo, photo=open(PATH_IMG, 'rb'),
                                   caption="OwO <b>Appare una waifu!</b>\nAggiungila al tuo harem con /protecc <i>nome waifu</i>\n", parse_mode='HTML')
    else:
        mycursor.execute("""UPDATE management
                        SET Time_mess = Time_mess - 1
                        WHERE ID_Supergruppo = %s""",
                     (ID_Supergruppo,))

        
def findWholeWord(protecc, waifu):
    for protecc_word in protecc.split(" "):
        for waifu_word in waifu.split(" "):
            if protecc_word == waifu_word:
                return True
    return False


# ---------------------------------------------
# REGISTRAZIONE NUOVO GRUPPO
def Welcomechat(update: Update, context: CallbackContext):
    # Prendo i dati di riferimento
    ID_Supergruppo = str(update.message.chat.id)
    Supergruppo_nome = str(update.message.chat.title)
    # Verifico se l'utente entrato è il bot
    if update.message.new_chat_members[0].id == context.bot.id:
        NewGroup(ID_Supergruppo, Supergruppo_nome)
        # Invio informazioni sul bot al gruppo
        update.message.reply_text(text="<b>Ciao chat!</b> Grazie per avermi aggiunto! "
        		 		"Da ora un sacco di waifu bellissime appariranno in questo gruppo "
                                       "Puoi aggiungerle al tuo harem personale indovinando per primo il loro nome\n "
                                       "Scrivi /help per tutte le infromazioni!\n"
                                  , parse_mode='HTML')


def NewGroup(ID_Supergruppo, Supergruppo_nome):
    # Cercare se il gruppo è registrato nel db
    mycursor.execute("SELECT ID_Supergruppo FROM supergruppo WHERE ID_Supergruppo=" + str(ID_Supergruppo))
    data = mycursor.fetchone()

    # if - Se il gruppo non è registrato vienne registrato
    # else - iene aggiornato il contatore per lo spawn della waifu
    if not data:
        mycursor.execute("INSERT INTO supergruppo (ID_Supergruppo, Supergruppo_nome) VALUES(%s,%s)",
                         (ID_Supergruppo, Supergruppo_nome))
        mycursor.execute(
            "INSERT INTO management(ID_Supergruppo, Time_mess, Time_reset, Started) VALUES (%s,%s,%s,%s)",
            (ID_Supergruppo, 1, 100, 0))



#############################################

def main():
    dp = updater.dispatcher
    '''
     TelegramDeprecationWarning: The @run_async decorator is deprecated. Use the `run_async` parameter of your Handler or `Dispatcher.run_async` instead.
     https://docs.python-telegram-bot.org/en/v13.3/telegram.ext.dispatcher.html?highlight=run_async#telegram.ext.Dispatcher.run_async
    '''
    
    dp.process_update = run_async(dp.process_update)
    

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("protecc", proteccwaifu, Filters.chat_type.supergroup))
    dp.add_handler(CommandHandler("gruppowaifu", topfatewaifugram, Filters.chat_type.supergroup & Filters.update.message))
    dp.add_handler(CommandHandler("changetime", changetime, Filters.chat_type.supergroup & Filters.update.message))
    dp.add_handler(CommandHandler("tradewaifu", tradewaifu, Filters.chat_type.supergroup & Filters.update.message))
    dp.add_handler(CommandHandler("daily", daily, Filters.chat_type.supergroup & Filters.update.message))
    dp.add_handler(CommandHandler("gift", gift, Filters.chat_type.supergroup & Filters.update.message))
    dp.add_handler(CommandHandler("favoritewaifu", favoritewaifu, Filters.chat_type.supergroup & Filters.update.message))
    dp.add_handler(CallbackQueryHandler(checktradewaifu, pattern="No@Waifu_Bot"))
    dp.add_handler(CallbackQueryHandler(checktradewaifu, pattern="Sì@Waifu_Bot"))
    dp.add_handler(CallbackQueryHandler(checktradewaifu, pattern="Esci@Waifu_Bot"))
    dp.add_handler(CallbackQueryHandler(checkgift, pattern="No@Waifu_Bot"))
    dp.add_handler(CallbackQueryHandler(checkgift, pattern="Sì@Waifu_Bot"))
    dp.add_handler(CallbackQueryHandler(checkgift, pattern="Esci@Waifu_Bot"))

    # Gestione lista waifu
    dp.add_handler(CommandHandler("harem", harem, Filters.chat_type.supergroup & Filters.update.message))
    dp.add_handler(CallbackQueryHandler(PageSelection))

    # Registrazione gruppo
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, callback=Welcomechat))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.chat_type.supergroup & Filters.update.message, callback=maindef))
    dp.add_handler(MessageHandler(Filters.private & Filters.update.message, callback=private))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
