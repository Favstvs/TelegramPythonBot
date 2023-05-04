import schedule
import time

'''
TODO:

- be able to use the command only once a day

- check if the user already use the command

OPTIONS:
-use run_daily() from JobQueue class

context.job_queue.run_daily(func, context=update.message.chat_id, days=(0, 1, 2, 3, 4, 5, 6,)))
'''


def func(update: Update, context: CallbackContext):

    ID_Supergruppo = str(update.message.chat.id)
    ID_User = str(update.message.from_user.id)
    Username = str(update.message.from_user.username)

    UpdateGroup(ID_Supergruppo, context)
    CheckUser(ID_User, Username)
    
    Daily = update.message.text
    
    def funcdaily():
	 try:
    	 	mycursor.execute("""UPDATE daily SET Coins=Coins+100 WHERE ID_User=%s;""", (ID_User))
    	 	
    	 	mycursor.execute("""SELECT Coins FROM daily WHERE ID_User=%s""", (ID_User))
    	 	data = mycursor.fetchone()
    	 	if data: 
    	 	Total_Coins = data[0]
    	 
    		update.message.reply_text("💰 Hai riscattato i coins giornalieri\n\n Ora i tuoi coins totali sono " + Total_Coins + " 🪙 " )
    	 
    	 else:
    	 	update.message.reply_text("Hai già riscatto i tuoi coins ")
    
    schedule.every(1).minutes.do(funcdaily)
    
    while True:
    	schedule.run_pending()
    	time.sleep(10)
   
    	 
    
    
  


#dp.add_handler(CommandHandler("daily", daily, Filters.group & Filters.update.message))
