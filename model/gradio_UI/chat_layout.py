import gradio as gr
from model.gradio_UI.bot import Bot

# BIDV POC DEV

class ChatLayout:
    def __init__(self):
        self.bot = Bot()

    def show_layout(self):
        with gr.Blocks():
            chatbot = gr.Chatbot(height=500, elem_classes="equal-height", type='messages')
            msg = gr.Textbox(label="User")
            clear = gr.Button('Clear')

        msg.submit(self.bot.chat, [msg],
                   [chatbot, msg])
        clear.click(self.clear, None, [chatbot])

    def clear(self):
        return None
