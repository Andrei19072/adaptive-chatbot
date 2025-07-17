from api_call import api_call
from chatbot import Chatbot

chatbot = Chatbot()
print(chatbot.get_personality_prompt())

while True:
    user_input = input()
    chatbot.add_history(user_input, "user")
    response = api_call(chatbot.get_conversation()).text
    chatbot.add_history(response, "model")
    print(response)
