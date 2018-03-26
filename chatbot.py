#method to train chatbot
from chatterbot.trainers import ListTrainer
#import the chatbot
from chatterbot import ChatBot
#Importing Google Text to Speech
from gtts import gTTS

import os



#create the chatbot
bot = ChatBot('Ndali')

bot.set_trainer(ListTrainer)


while True:
    message = input('You: ')
   
    if message.strip()  != 'Bye':
        reply = bot.get_response(message)
        confidence = reply.confidence
        
      
		
		##TEXT TO SPEECH
        speech = (message)
        tts = gTTS(text=speech, lang='en')
        tts.save("Speech/speech.mp3")
        os.system("start Speech/speech.mp3")

        if confidence >  0.7:
            print('Ndali: ', reply)
        else:
            print ('Ndali: I do not understand')        
    
    if message.strip() == 'Bye':
        print('Ndali:  ')
        break
