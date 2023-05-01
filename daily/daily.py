import schedule
import time



def daily(update: Update, context: CallbackContext):

    ID_Supergruppo = str(update.message.chat.id)
    ID_User = str(update.message.from_user.id)
    Username = str(update.message.from_user.username)

    UpdateGroup(ID_Supergruppo, context)
    CheckUser(ID_User, Username)
    
    Daily = update.message.text
    
    def funcdaily():
	 try:
    	 	mycursor.execute("""UPDATE users SET Coins=Coins+100 WHERE ID_User=%s;""", (ID_User))
    	 
    		update.message.reply_text("💰 Hai riscattato i coins giornalieri ")
    	 
    	 else:
    	 	update.message.reply_text("Hai già riscatto i tuoi coins ")
    
    schedule.every(1).minutes.do(funcdaily)
    
    while True:
    	schedule.run_pending()
    	time.sleep(10)
   
    	 
    
    
  


#dp.add_handler(CommandHandler("daily", daily, Filters.group & Filters.update.message))
