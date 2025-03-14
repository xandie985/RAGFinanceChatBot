"""
    This module uses Gradio to create an interactive web application for a chatbot with various features.

    The application interface is organized into three rows:
    1. The first row contains a Chatbot component that simulates a conversation with a language model, along with a hidden
    reference bar initially. The reference bar can be toggled using a button. The chatbot supports feedback in the form
    of like and dislike icons.

    2. The second row consists of a Textbox for user input. He can also choose the model to work with.

    3. The third row includes buttons for submitting text, toggling the reference bar visibility, uploading PDF/doc files,
    adjusting temperature for GPT responses, selecting the document type, and clearing the input.

    The application processes user interactions:
    - Uploaded files trigger the processing of the files, updating the input and chatbot components.
    - Submitting text triggers the chatbot to respond, considering the selected document type and temperature settings.
    The response is displayed in the Textbox and Chatbot components, and the reference bar may be updated.

    The application can be run as a standalone script, launching the Gradio interface for users to interact with the chatbot.

    Note: The docstring provides an overview of the module's purpose and functionality, but detailed comments within the code
    explain specific components, interactions, and logic throughout the implementation.
"""
import gradio as gr
from src.upload_file import UploadFile
from src.finbot import ChatBot
from src.ui_settings import UISettings


with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("FinGPT"):
            # First ROW:
            with gr.Row() as row_one:
                with gr.Column(visible=False) as reference_bar:
                    ref_output = gr.Markdown()

                with gr.Column() as chatbot_output:
                    chatbot = gr.Chatbot(
                        [],
                        elem_id="chatbot",
                        bubble_full_width=False,
                        height=500,
                        avatar_images=(
                            ("images/user.png"), "images/chatbot.png"),
                    )
                    chatbot.like(UISettings.feedback, None, None)  # feedbacks
            # SECOND ROW:
            with gr.Row():
                input_txt = gr.Textbox(
                    lines=4,
                    scale=8,
                    placeholder="Hi there! Have a question? Ask away! Or, upload your PDFs to find the answers within them.",
                    container=False,
                )
                model_choice = gr.Dropdown(
                    label="Choose model", choices=["gpt-4o-mini", "llama3-70b-8192", "mixtral-8x7b-32768"], value="llama3-70b-8192")

            # Third ROW:
            with gr.Row() as row_two:
                text_submit_btn = gr.Button(value="Ask FinGPT 🤗")
                sidebar_state = gr.State(False)
                btn_toggle_sidebar = gr.Button(
                    value="References")
                btn_toggle_sidebar.click(UISettings.toggle_sidebar, 
                                         [sidebar_state], 
                                         [reference_bar, sidebar_state]
                                         )
                upload_btn = gr.UploadButton(
                    "Upload you pdf/doc file 📄", file_types=[
                        '.pdf',
                        '.doc'
                    ],
                    file_count="multiple")
                temperature_bar = gr.Slider(minimum=0, maximum=1, value=0, step=0.1,
                                            label="Temperature", info="0: Coherent mode, 1: Creative mode")
                rag_with_dropdown = gr.Dropdown(
                    label="RAG with", choices=["Existing database", "Upload new data"], value="Existing database")
                clear_button = gr.ClearButton([input_txt, chatbot])
            # Backend Process:
            file_msg = upload_btn.upload(fn=UploadFile.process_uploaded_files, inputs=[
                upload_btn, chatbot, rag_with_dropdown, model_choice], outputs=[input_txt, chatbot], queue=False)

            txt_msg = input_txt.submit(fn=ChatBot.respond,
                                       inputs=[chatbot,
                                               input_txt,
                                               rag_with_dropdown,
                                               temperature_bar, 
                                               model_choice],
                                       outputs=[input_txt,chatbot,
                                                ref_output],
                                       queue=False).then(lambda: gr.Textbox(interactive=True),
                                                         None, 
                                                         [input_txt], queue=False)

            txt_msg = text_submit_btn.click(fn=ChatBot.respond,
                                            inputs=[chatbot, 
                                                    input_txt,
                                                    rag_with_dropdown, 
                                                    temperature_bar,
                                                    model_choice],
                                            outputs=[input_txt,
                                                     chatbot, ref_output],
                                            queue=False).then(lambda: gr.Textbox(interactive=True),
                                                              None, [input_txt], queue=False)


if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
