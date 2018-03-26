from chatterbot import ChatBot as cb
import sqlite3
from chatterbot.trainers import ListTrainer

#Creating new Chatbot Named Ndali

bot = cb("Ndali")

#Opening the dataset text file
#Going Through DataSet and seperating the english and oshowambo words/sentences 
#Putting all the english words into a list called english
#Putting all the oshiwambo words into a list called oshiwambo

with open('dataset.txt', 'r') as f:
    for line in f.readlines():
           # parts = 
            english = []
            oshiwambo = []

            english,oshiwambo = line.split('------')


##bot = ChatBot(
##    'Norman',
##    storage_adapter='chatterbot.storage.SQLStorageAdapter',
##    database='./database.sqlite3'
##)

#bot = ChatBot('Ndali')

conversation = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]

bot.set_trainer(ListTrainer)
bot.train(conversation)


human = input("Human: ")
response = bot.get_response(human)
print("Bot: ", response)
