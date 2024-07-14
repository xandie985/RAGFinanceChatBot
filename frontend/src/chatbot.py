import os
import re
import ast
import html
import time
import gradio as gr
from openai import OpenAI
from typing import List, Tuple
from src.load_config import LoadConfig
from langchain.vectorstores import Chroma

APP_CONFIG = LoadConfig()
client = OpenAI()

class ChatBot:
    """
    Class representing a chatbot with document retrieval and response generation capabilities.

    This class provides static methods for responding to user queries, handling feedback, and
    cleaning references from retrieved documents.
    """
    @staticmethod
    def respond(chatbot: List, message: str, data_type: str = "Preprocessed doc", temperature: float = 0.0) -> Tuple:
        """
        Generate a response to a user query using document retrieval and language model completion.

        Parameters:
            chatbot (List): List representing the chatbot's conversation history.
            message (str): The user's query.
            data_type (str): Type of data used for document retrieval ("Preprocessed doc" or "Upload doc: Process for RAG").
            temperature (float): Temperature parameter for language model completion.

        Returns:
            Tuple: A tuple containing an empty string, the updated chat history, and references from retrieved documents.
        """
        if data_type == "Preprocessed doc":
            # directories
            if os.path.exists(APP_CONFIG.persist_directory):
                vectordb = Chroma(persist_directory=APP_CONFIG.persist_directory,
                                  embedding_function=APP_CONFIG.embedding_model)
            else:
                chatbot.append(
                    (message, f"VectorDB does not exist. Please first execute the 'upload_data_manually.py' module. For further information please visit README.md of this repository."))
                return "", chatbot, None

        elif data_type == "Upload doc for RAG Processing":
            if os.path.exists(APP_CONFIG.custom_persist_directory):
                vectordb = Chroma(persist_directory=APP_CONFIG.custom_persist_directory,
                                  embedding_function=APP_CONFIG.embedding_model)
            else:
                chatbot.append(
                    (message, f"No file uploaded. Please first upload your files using the 'upload' button."))
                return "", chatbot, None

        docs = vectordb.similarity_search(message, k=APP_CONFIG.k)
        print(docs)
        question = "# User new question:\n" + message
        retrieved_content = ChatBot.clean_references(docs)
        # Memory: previous  Q-n-A pairs
        chat_history = f"Chat history:\n {str(chatbot[-APP_CONFIG.qa_pair_count:])}\n\n"
        prompt = f"{chat_history}{retrieved_content}{question}"
        print("========================")
        print(prompt)
        response = client.chat.completions.create(model=APP_CONFIG.llm_model,
                                                  messages=[
                                                      {"role": "system", "content": APP_CONFIG.llm_system_role},
                                                      {"role": "user", "content": prompt}
                                                      ],
                                                      temperature=temperature)
        print(response)
        chatbot.append(
            (message, response.choices[0].message.content))
        time.sleep(2)

        return "", chatbot, retrieved_content

    @staticmethod
    def extract_content(input_text):
        begin_pattern = r"""page_content='"""
        end_pattern = r"""'\s*metadata="""

        between_pattern = rf'{begin_pattern}(.*?){end_pattern}'
        from_end_pattern = rf"{end_pattern}(.*)"

        between_match = re.search(between_pattern, input_text, re.DOTALL)
        from_end_match = re.search(from_end_pattern, input_text, re.DOTALL)

        between_text = between_match.group(1) if between_match else None
        from_end_text = from_end_match.group(1) if from_end_match else None

        return between_text, from_end_text

    @staticmethod
    def clean_references(documents: List) -> str:
        """
        Clean and format references from retrieved documents.

        Parameters:
            documents (List): List of retrieved documents.

        Returns:
            str: A string containing cleaned and formatted references.
        """
        server_url = "http://localhost:8000"
        documents = [str(x)+"\n\n" for x in documents]
        markdown_documents = ""
        counter = 1
        for doc in documents:
            # Extract content and metadata
            content, metadata = ChatBot.extract_content(doc)
            metadata_dict = ast.literal_eval(metadata)

            # Decode newlines and other escape sequences
            print("content: ", content)
            content = bytes(content, "utf-8").decode("unicode_escape")

            # Replace escaped newlines with actual newlines
            content = re.sub(r'\\n', '\n', content)
            # Remove special tokens
            content = re.sub(r'\s*<EOS>\s*<pad>\s*', ' ', content)
            # Remove any remaining multiple spaces
            content = re.sub(r'\s+', ' ', content).strip()

            # Decode HTML entities
            content = html.unescape(content)

            # Replace incorrect unicode characters with correct ones
            content = content.encode('latin1').decode('utf-8', 'ignore')

            pdf_url = f"{server_url}/{os.path.basename(metadata_dict['source'])}"

            # Append cleaned content to the markdown string with two newlines between documents
            markdown_documents += f"# Retrieved content {counter}:\n" + content + "\n\n" + \
                f"Source: {os.path.basename(metadata_dict['source'])}" + " | " +\
                f"Page number: {str(metadata_dict['page'])}" + " | " +\
                f"[View PDF]({pdf_url})" "\n\n"
            counter += 1

        return markdown_documents