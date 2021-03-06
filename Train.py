from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import os

# Uncomment the following line to enable verbose logging
# import logging
# logging.basicConfig(level=logging.INFO)

# Create a new instance of a ChatBot
bot = ChatBot(
    "Ndali",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    input_adapter="chatterbot.input.TerminalAdapter",
    output_adapter="chatterbot.output.TerminalAdapter"
)
bot.set_trainer(ListTrainer)

for _file in os.listdir('Data'):
     data = open('Data/' + _file, 'r' ).readlines()
     bot.train(data)


CONVERSATION_ID = bot.storage.create_conversation()


def get_feedback():
    from chatterbot.utils import input_function

    text = input_function()

    if 'yes' in text.lower():
        return False
    elif 'no' in text.lower():
        return True
    else:
        print('Please type either "Yes" or "No"')
        return get_feedback()


print("Type something to begin training Ndali...")

# The following loop will execute each time the user enters input
while True:
    try:
        input_statement = bot.input.process_input_statement()
        statement, response = bot.generate_response(input_statement, CONVERSATION_ID)

        bot.output.process_response(response)
        print('\n Is "{}" the correct response to "{}"? \n'.format(response, input_statement))
        if get_feedback():
            print("please teach Ndali the correct answer")
            response1 = bot.input.process_input_statement()
            bot.learn_response(response1, input_statement)
            bot.storage.add_to_conversation(CONVERSATION_ID, statement, response1)
            print("Ndali has Learned the Response!")

    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        break
