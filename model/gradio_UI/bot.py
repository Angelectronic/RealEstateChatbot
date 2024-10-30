from model.AI_agent.ai_agent import AIAgent
import gradio as gr
import copy

class Bot():
    def __init__(self):
        self.agent = AIAgent()
        self.chat_history = []

    def chat(self, user_message):
        self.chat_history.append({"role": "user", "content": user_message})

        response = self.agent.chat_complete([m for m in self.chat_history if isinstance(m['content'], str)]) # only send text messages to the agent
        
        for res in response:
            self.chat_history.append({"role": "assistant", "content": res})

        return copy.deepcopy(self.chat_history), ""