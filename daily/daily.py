from datetime import datetime
import time

'''
TODO:

- be able to use the command only once a day

- check if the user already use the command

OPZIONE #1

- prendo la data del messaggio
- la inserisco nella colonna apposita di sql
(???- usare datetime per convertire la data Unix in  'YYYY-MM-DD HH:MM:SS' string???) 
- confronto, se la differenza tra le due date e' minore di 24h nego i coins
  altrimenti se < 24h, l'user puo' riscattare i coins 


OPTIONS:
-use run_daily() from JobQueue class

context.job_queue.run_daily(func, context=update.message.chat_id, days=(0, 1, 2, 3, 4, 5, 6,)))
'''


def daily(update: Update, context: CallbackContext):

    ID_Supergruppo = str(update.message.chat.id)
    ID_User = int(update.message.from_user.id)
    Username = str(update.message.from_user.username)

    UpdateGroup(ID_Supergruppo, context)
    CheckUser(ID_User, Username)
    
    #prendo la data del messaggio
    Time_Mess = update.message(date)

    #estraggo l'ultima data registrata
    mycursor.execute("""SELECT Time_Mess FROM daily WHERE ID_User=%s""", (ID_User))
    data = mycursor.fetchone()
    
    
    #confronto le due date
    
    date_1 = data[0]
    date_2 = Time_Mess
    date_format_str = "%d/%m/%Y %H:%M:%S"
    
    date_1_start = datetime.strptime(date_1, date_format_str)
    date_2_end = datetime.strptime(date_2, date_format_str)
    
    diff = date_2_end - date_1_start  
    
    diff_in_hours = diff.total_seconds()/3600   
    
    if diff_in_hours < 24:
        try:
            mycursor.execute("""UPDATE daily SET Coins=Coins+100 WHERE ID_User=%s;""", (ID_User))
            mycursor.execute("""SELECT Coins FROM daily WHERE ID_User=%s""", (ID_User))
            data = mycursor.fetchone()
            if data: 
                Total_Coins = data[0]
                update.message.reply_text("💰 Hai riscattato i coins giornalieri\n\n Ora i tuoi coins totali sono " + Total_Coins + " 🪙 " )
    		#inserico la nuova data nella colonna apposita della tabella
                mycursors.execute("""UPDATE daily SET Time_Mess=%s WHERE ID_User=%s""", (Time_Mess, ID_User))
        except:
            pass
    else:
        update.message.reply_text("Hai già riscatto i tuoi coins. Devi aspettare 24 ore ")


    	 
    
    
  


#dp.add_handler(CommandHandler("daily", daily, Filters.group & Filters.update.message))
