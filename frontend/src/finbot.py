import os
import re
import ast
import html
import time
import logging
import gradio as gr
from openai import OpenAI
from typing import List, Tuple, Dict, Any, Optional
from src.load_config import LoadConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma

from uuid import uuid4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("finbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FinBot")

APP_CONFIG = LoadConfig()

# Setup LangChain tracing for evaluation
unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Ragas_RAG_Eval"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

class ChatBot:
    """
    Class representing a chatbot with document retrieval and response generation capabilities.

    This class provides methods for responding to user queries by retrieving relevant
    documents from a vector database and generating responses using language models.
    It supports multiple LLM providers (OpenAI and Groq) and handles conversation history.
    """
    vectordb = None 
    
    @staticmethod
    def respond(chatbot: List, message: str, data_type: str = "Existing database", 
                temperature: float = 0.0, model_choice: str = APP_CONFIG.llama3_70bmodel) -> Tuple:
        """
        Generate a response to a user query using document retrieval and language model completion.

        Parameters:
            chatbot (List): List representing the chatbot's conversation history.
            message (str): The user's query.
            data_type (str): Type of data used for document retrieval ("Existing database" or "Upload new data").
            temperature (float): Temperature parameter for language model completion.
            model_choice (str): The language model to use for generating responses.

        Returns:
            Tuple: A tuple containing an empty string, the updated chat history, and references from retrieved documents.
        """
        try:
            # Initialize vector database if needed
            if not ChatBot._initialize_vectordb(chatbot, message, data_type):
                return "", chatbot, None
                
            # Retrieve relevant documents
            docs = ChatBot._retrieve_documents(message)
            
            # Prepare prompt with context
            prompt = ChatBot._prepare_prompt(chatbot, message, docs)
            
            # Generate response using the selected model
            if ChatBot._is_openai_model(model_choice):
                ChatBot._generate_openai_response(chatbot, message, prompt, temperature, model_choice)
            else:
                ChatBot._generate_groq_response(chatbot, message, prompt, temperature, model_choice)
            
            # Add a small delay to prevent rate limiting
            time.sleep(1)
            
            # Return the updated chat history and retrieved content
            retrieved_content = ChatBot.clean_references(docs)
            return "", chatbot, retrieved_content
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg, exc_info=True)
            chatbot.append((message, f"I encountered an error: {error_msg}. Please try again."))
            return "", chatbot, None
    
    @staticmethod
    def _initialize_vectordb(chatbot: List, message: str, data_type: str) -> bool:
        """
        Initialize the vector database based on the selected data type.
        
        Parameters:
            chatbot (List): The chatbot's conversation history.
            message (str): The user's message.
            data_type (str): The type of data to use ("Existing database" or "Upload new data").
            
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        if ChatBot.vectordb is None:
            try:
                if data_type == "Existing database":
                    if os.path.exists(APP_CONFIG.persist_directory):
                        logger.info(f"Loading existing vector database from {APP_CONFIG.persist_directory}")
                        ChatBot.vectordb = Chroma(
                            persist_directory=APP_CONFIG.persist_directory,
                            embedding_function=APP_CONFIG.embedding_model
                        )
                        return True
                    else:
                        error_msg = "VectorDB does not exist. Please first execute the 'upload_data_manually.py' module."
                        logger.warning(error_msg)
                        chatbot.append((message, f"{error_msg} For further information please visit README.md of this repository."))
                        return False

                elif data_type == "Upload new data":
                    if os.path.exists(APP_CONFIG.custom_persist_directory):
                        logger.info(f"Loading custom vector database from {APP_CONFIG.custom_persist_directory}")
                        ChatBot.vectordb = Chroma(
                            persist_directory=APP_CONFIG.custom_persist_directory,
                            embedding_function=APP_CONFIG.embedding_model
                        )
                        return True
                    else:
                        error_msg = "No file uploaded. Please first upload your files using the 'upload' button."
                        logger.warning(error_msg)
                        chatbot.append((message, error_msg))
                        return False
            except Exception as e:
                error_msg = f"Error initializing vector database: {str(e)}"
                logger.error(error_msg, exc_info=True)
                chatbot.append((message, f"Error: {error_msg}"))
                return False
        return True
    
    @staticmethod
    def _retrieve_documents(query: str) -> List:
        """
        Retrieve relevant documents from the vector database.
        
        Parameters:
            query (str): The user's query.
            
        Returns:
            List: List of retrieved documents.
        """
        logger.info(f"Retrieving documents for query: {query}")
        return ChatBot.vectordb.similarity_search(query, k=APP_CONFIG.k)
    
    @staticmethod
    def _prepare_prompt(chatbot: List, message: str, docs: List) -> str:
        """
        Prepare the prompt for the language model with context and history.
        
        Parameters:
            chatbot (List): The chatbot's conversation history.
            message (str): The user's message.
            docs (List): Retrieved documents.
            
        Returns:
            str: The prepared prompt.
        """
        question = "# User new question:\n" + message
        retrieved_content = ChatBot.clean_references(docs)
        
        # Include recent conversation history
        history_limit = min(APP_CONFIG.qa_pair_count, len(chatbot))
        chat_history = f"Chat history:\n {str(chatbot[-history_limit:])}\n\n" if chatbot else ""
        
        prompt = f"{chat_history}{retrieved_content}{question}"
        logger.debug(f"Prepared prompt: {prompt[:500]}...")  # Log first 500 chars to avoid excessive logging
        return prompt
    
    @staticmethod
    def _is_openai_model(model_choice: str) -> bool:
        """
        Check if the selected model is an OpenAI model.
        
        Parameters:
            model_choice (str): The selected model.
            
        Returns:
            bool: True if it's an OpenAI model, False otherwise.
        """
        openai_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        return model_choice in openai_models
    
    @staticmethod
    def _generate_openai_response(chatbot: List, message: str, prompt: str, 
                                 temperature: float, model_choice: str) -> None:
        """
        Generate a response using OpenAI models.
        
        Parameters:
            chatbot (List): The chatbot's conversation history.
            message (str): The user's message.
            prompt (str): The prepared prompt.
            temperature (float): Temperature parameter for response generation.
            model_choice (str): The OpenAI model to use.
        """
        try:
            logger.info(f"Generating response using OpenAI model: {model_choice}")
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=model_choice,
                messages=[
                    {"role": "system", "content": APP_CONFIG.llm_system_role},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            logger.info(f"Response generated successfully with {model_choice}")
            chatbot.append((message, response.choices[0].message.content))
        except Exception as e:
            error_msg = f"Error generating OpenAI response: {str(e)}"
            logger.error(error_msg, exc_info=True)
            chatbot.append((message, f"Error with {model_choice}: {error_msg}"))
    
    @staticmethod
    def _generate_groq_response(chatbot: List, message: str, prompt: str, 
                               temperature: float, model_choice: str) -> None:
        """
        Generate a response using Groq models.
        
        Parameters:
            chatbot (List): The chatbot's conversation history.
            message (str): The user's message.
            prompt (str): The prepared prompt.
            temperature (float): Temperature parameter for response generation.
            model_choice (str): The Groq model to use.
        """
        try:
            logger.info(f"Generating response using Groq model: {model_choice}")
            chat_llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model=model_choice,
                temperature=temperature
            )
            # Prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", APP_CONFIG.llm_system_role),
                ("human", prompt)
            ])
            chain = prompt_template | chat_llm | StrOutputParser()
            response = chain.invoke({})
            logger.info(f"Response generated successfully with {model_choice}")
            chatbot.append((message, response))
        except Exception as e:
            error_msg = f"Error generating Groq response: {str(e)}"
            logger.error(error_msg, exc_info=True)
            chatbot.append((message, f"Error with {model_choice}: {error_msg}"))

    @staticmethod
    def extract_content(input_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract content and metadata from document text representation.
        
        Parameters:
            input_text (str): The text to extract content from.
            
        Returns:
            Tuple[Optional[str], Optional[str]]: Extracted content and metadata.
        """
        try:
            begin_pattern = r"""page_content='"""
            end_pattern = r"""'\s*metadata="""

            between_pattern = rf'{begin_pattern}(.*?){end_pattern}'
            from_end_pattern = rf"{end_pattern}(.*)"

            between_match = re.search(between_pattern, input_text, re.DOTALL)
            from_end_match = re.search(from_end_pattern, input_text, re.DOTALL)

            between_text = between_match.group(1) if between_match else None
            from_end_text = from_end_match.group(1) if from_end_match else None

            return between_text, from_end_text
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}", exc_info=True)
            return None, None
            
    @staticmethod
    def clean_references(documents: List) -> str:
        """
        Format retrieved documents as markdown for display.
        
        Parameters:
            documents (List): List of retrieved documents.
            
        Returns:
            str: Formatted markdown string of document content with metadata.
        """
        server_url = "http://localhost:8000"
        markdown_documents = ""
        counter = 1
        
        if not documents:
            logger.warning("No documents retrieved")
            return "No relevant documents found."
        
        for doc in documents:
            try:
                # Handle Document objects from langchain
                if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                    content = doc.page_content
                    metadata_dict = doc.metadata
                else:
                    # Fall back to string parsing if needed
                    doc_str = str(doc) + "\n\n"
                    match = re.search(r"page_content=[\"']?(.*?)[\"']?\s+metadata=(\{.*\})", doc_str, re.DOTALL)
                    if match:
                        content, metadata_str = match.groups()
                        metadata_dict = ast.literal_eval(metadata_str)
                    else:
                        logger.warning(f"Could not parse document: {doc_str[:100]}...")
                        continue
                
                # Clean up the content
                content = content.replace('\\n', '\n')
                content = re.sub(r'\s*<EOS>\s*<pad>\s*', ' ', content)
                content = re.sub(r'\s+', ' ', content).strip()
                content = html.unescape(content)
                
                # Try to get source and page from metadata
                source = metadata_dict.get('source', 'Unknown source')
                page = metadata_dict.get('page', 'N/A')
                
                pdf_url = f"{server_url}/{os.path.basename(source)}"
                markdown_documents += f"# Retrieved content {counter}:\n" + content + "\n\n" + \
                    f"Source: {os.path.basename(source)}" + " | " +\
                    f"Page number: {str(page)}" + " | " +\
                    f"[View PDF]({pdf_url})" "\n\n"
                counter += 1
            except Exception as e:
                logger.error(f"Error processing document: {str(e)}", exc_info=True)
                continue

        return markdown_documents