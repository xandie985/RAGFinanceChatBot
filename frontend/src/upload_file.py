from src.prepare_openAIEmbeddings_vectordb import PrepareVectorDB
from typing import List, Tuple
from src.load_config import LoadConfig

APP_CONFIG = LoadConfig()


class UploadFile:
    """
    Utility class for handling file uploads and processing.

    This class provides static methods for checking directories and processing uploaded files
    to prepare a VectorDB.
    """

    @staticmethod
    def process_uploaded_files(files_dir: List, chatbot: List, rag_with_dropdown: str) -> Tuple:
        """
        Prepares and saves a VectorDB from uploaded files.

        Parameters:
            files_dir (List): List of paths to the uploaded files.
            chatbot (List): An instance of the chatbot for communication.
            rag_with_dropdown (str): provides whether to perform RAG on new docs.
        Returns:
            Tuple: A tuple containing an empty string and the updated chatbot instance.
        """
        if rag_with_dropdown == "Upload docs to chat with:":
            prepare_vectordb_instance = PrepareVectorDB(data_directory=files_dir,
                                                        persist_directory=APP_CONFIG.custom_persist_directory,
                                                        embedding_model_engine=APP_CONFIG.embedding_model_engine,
                                                        chunk_size=APP_CONFIG.chunk_size,
                                                        chunk_overlap=APP_CONFIG.chunk_overlap)
            prepare_vectordb_instance.prepare_and_save_vectordb()
            chatbot.append(
                (" ", "Uploaded files are ready for querying."))
        else:
            chatbot.append(
                (" ", "If you want to upload your own PDF, please select 'rag_with' from the dropdown."))
        return "", chatbot
