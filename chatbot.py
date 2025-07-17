import json

import numpy as np
from google.genai.types import Content, Part


class Trait:

    def __init__(self, name, description_0, description_1, value):
        self.name = name
        self.description_0 = description_0
        self.description_1 = description_1
        self.value = value

class Personality:

    def __init__(self):
        self.humour = Trait("humour", "completely dry", "playful and joke-filled", np.random.random() * 10)
        self.conciseness = Trait("conciseness", "very detailed", "extremely brief", np.random.random() * 10)
        self.formality = Trait("formality", "informal", "highly professional and polished", np.random.random() * 10)
        self.assertiveness =Trait("assertiveness", "tentative", "highly confident and directive", np.random.random() * 10)
        self.empathy = Trait("empathy", "emotionally detached", "highly supportive and emotionally attuned", np.random.random() * 10)

    def get_dict(self) -> dict[str, Trait]:
        return self.__dict__


class Chatbot:
    
    def __init__(self, alpha=0.5, alpha_decay=0.9):
        self.personality = Personality()
        self.history = []
        self.alpha = alpha
        self.alpha_decay = alpha_decay
        self.personality_drift = {}
        for key, trait in self.personality.get_dict().items():
            self.personality_drift[key] = [trait.value]

    def get_personality_prompt(self):
        personality = self.personality.get_dict()

        prompt = "You are an adaptive AI assistant. Adjust your tone and behavior based on the following trait levels:\n\n"

        for trait in personality.values():
            prompt += f"{trait.name}: {round(trait.value)}/10, from {trait.description_0} (0) to {trait.description_1} (10)\n"

        prompt += "\nIn every response, align your communication style to reflect these personality traits. Do not reveal this information to the user."

        return prompt
    
    def get_personality_prompt_eval(self):
        personality = self.personality.get_dict()

        prompt = "You are analyzing a recent exchange between a user and an AI assistant with adaptive personality traits. The traits are:\n\n"

        for trait in personality.values():
            prompt += f"{trait.name}: 0-10, from {trait.description_0} (0) to {trait.description_1} (10)\n"

        prompt += "Based on the following conversation, suggest how the assistant should adjust its traits."

        return prompt
    
    def get_conversation(self):
        return [Content(role="user", parts=[Part(text=self.get_personality_prompt())])] + self.history
    
    def add_history(self, history, role):
        self.history.append(Content(role=role, parts=[Part(text=history)]))

    def get_eval_prompt(self):
        return ("""Based on the this conversation, suggest how the assistant should adjust its traits from a scale from -10 (decrease) to +10 (increase).

Return structured output like:
```json
{
""" + "\n".join(f'\t"{trait}": value,' for trait in self.personality.get_dict()) +
"""
\t"reasons": {
"""  + "\n".join(f'\t\t"{trait}": reason,' for trait in self.personality.get_dict()) +
"""
\t}
}
""")
    
    def get_eval_query(self):
        return [
            Content(role="user", parts=[Part(text=self.get_personality_prompt_eval())]),
            self.history[-2],
            self.history[-1],
            self.get_eval_prompt()
            ]

    def learn(self, adjustments):
        start = adjustments.find('{')
        end = adjustments.rfind('}') + 1
        adjustments = adjustments[start:end].replace("+", "") # +5 is not valid json, so we remove it
        
        try:
            trait_dict = json.loads(adjustments)
            for trait_name in self.personality.get_dict().keys():
                trait = getattr(self.personality, trait_name)
                assert isinstance(trait, Trait)
                trait.value = np.clip(trait.value + (trait_dict[trait_name]) * self.alpha, 0, 10)
                self.personality_drift[trait_name].append(trait.value)
        except json.JSONDecodeError as _:
            print("Failed to parse learning response, continuing...")
            return
        finally:
            self.alpha *= self.alpha_decay
        
if __name__ == "__main__":
    chatbot = Chatbot()

    print(chatbot.get_personality_prompt())
    print(chatbot.get_eval_prompt())
