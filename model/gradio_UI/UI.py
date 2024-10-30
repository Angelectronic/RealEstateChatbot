import gradio as gr
import sys
sys.path.append('..')
from model.gradio_UI.chat_layout import ChatLayout

css="""
a {
    display: block;
    width: 200px;
    height: auto;
    border: 1px solid #ddd;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    margin-bottom: 10px;
    transition: transform 0.2s;
}

img:hover {
    transform: scale(1.05);
    filter: brightness(90%);
    transition: all 0.3s ease;
}

.equal-height { height: 400px; overflow: auto; }
body {
    font-family: 'Roboto', sans-serif;
    color: #333;
}
.cta-button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    border-radius: 5px;
    text-transform: uppercase;
    font-weight: bold;
    transition: background-color 0.3s ease;
}

.cta-button:hover {
    background-color: #0056b3;
}
"""

class Demo:
    def __init__(self):
        self.chat_layout = ChatLayout()

    def launch(self):
        with gr.Blocks(css=css) as interface:
            self.chat_layout.show_layout()

        interface.launch(share=False)


if __name__ == "__main__":
    Demo().launch()
