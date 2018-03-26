#method to train chatbot
from chatterbot.trainers import ListTrainer
#import the chatbot
from chatterbot import ChatBot

import os

#create the chatbot
bot = ChatBot(
    'Ndali'#,
    #storage_adapter="chatterbot.storage.SQLStorageAdapter",
    #input_adapter="chatterbot.input.TerminalAdapter",
    #output_adapter="chatterbot.output.TerminalAdapter"
    )

bot.set_trainer(ListTrainer)

for _file in os.listdir('Data'):
     data = open('Data/' + _file, 'r' ).readlines()
     bot.train(data)

##def bot_training():
##    for _file in os.listdir('Data'):
##     data = open('Data/' + _file, 'r' ).readlines()
##     bot.train(data)
    

while True:
    message = input('You: ')
   # if message.strip() == "train-bot":
        #bot_training()    
    if message.strip()  != 'Bye':
        reply = bot.get_response(message)
        confidence = reply.confidence
        if confidence >  0.7:
            print('Ndali: ', reply)
        else:
            print ('Ndali: I do not understand')        
    #elif message.strip() == 'Can I teach you: ':
      #  print('yes' )  
    if message.strip() == 'Bye':
        print('Ndali:  ')
        break
