from matplotlib import pyplot as plt

from api_call import api_call
from chatbot import Chatbot

chatbot = Chatbot()

while True:
    user_input = input()
    if user_input == "exit":
        break
    chatbot.add_history(user_input, "user")
    if len(chatbot.history) >= 2:
        response = api_call(chatbot.get_eval_query()).text
        chatbot.learn(response)
    response = api_call(chatbot.get_conversation()).text
    chatbot.add_history(response, "model")
    print(response)

for trait, data in chatbot.personality_drift.items():
    plt.plot(data, label=trait)

plt.title("Personaity drift")
plt.xlabel("Timestep")
plt.ylabel("Trait value")
plt.ylim(ymin=0, ymax=10.5)
plt.legend()
plt.show()
