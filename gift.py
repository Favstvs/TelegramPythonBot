def gift(update: Update, context: CallbackContext):

    ID_User = int(update.callback_query.from_user.id)
    ID_Supergruppo = str(update.callback_query.message.chat.id)
    Mess_ID_Gift = update.callback_query.message.message_id
    CallBackRequest = str(update.callback_query.data)
    
    mycursor.execute("""SELECT ID_User_1, ID_User_2
                        FROM regali
                        WHERE ID_Supergruppo = %s AND Mess_ID_Trade = %s""", (ID_Supergruppo, Mess_ID_Gift))
    
    data = mycursor.fetchone()
    ID_User_Gift = [data[0], data[1]]
    if ID_User != ID_User_Gift[0] and ID_User != ID_User_Gift[1]:

        update.callback_query.answer(text="Questo non è il tuo regalo...")
    elif ID_User == ID_User_Gift[0]:
    	if CallBackRequest == "Quit@Waifu_Bot":
           	 mycursor.execute("""DELETE FROM regali WHERE ID_Supergruppo = %s AND Mess_ID_Gift=%s""", (ID_Supergruppo,
                                                                                                      Mess_ID_Gift,))
      	    try:
                context.bot.delete_message(ID_Supergruppo, message_id=Mess_ID_Gift)
            except:
                pass
        else:
            update.callback_query.answer(text="Non puoi rispondere al tuo stesso regalo...")
            
    else:
    	if CallBackRequest == "Yes@Waifu_Bot":
    	
    	   mycursor.execute("""SELECT Regalo
                                FROM regali
                                WHERE ID_Supergruppo = %s AND Mess_ID_Gift = %s""",
                             (ID_Supergruppo, Mess_ID_Gift,))
           data = mycursor.fetchone()
           
           Gift = data[0]
           NP = []
           ID_Waifu_Gift = []
           i = 0
    

                                                                                                      
                                                                                                     
