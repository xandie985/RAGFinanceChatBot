from src.prepare_openAIEmbeddings_vectordb import PrepareVectorDB
from typing import List, Tuple, Optional, Any
import logging
import os
from src.load_config import LoadConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("upload.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("UploadFile")

APP_CONFIG = LoadConfig()


class UploadFile:
    """
    Utility class for handling file uploads and processing.

    This class provides static methods for checking directories and processing uploaded files
    to prepare a VectorDB for retrieval augmented generation (RAG).
    
    Methods:
        process_uploaded_files: Processes uploaded files and creates a vector database.
        validate_files: Validates that uploaded files exist and are in supported formats.
    """

    @staticmethod
    def process_uploaded_files(files_dir: List[str], chatbot: List, 
                              rag_with_dropdown: str, 
                              model_choice: Optional[str] = None) -> Tuple[str, List]:
        """
        Prepares and saves a VectorDB from uploaded files.

        Parameters:
            files_dir (List[str]): List of paths to the uploaded files.
            chatbot (List): An instance of the chatbot for communication.
            rag_with_dropdown (str): Indicates whether to perform RAG on new documents.
            model_choice (Optional[str]): The selected model for the chatbot.
            
        Returns:
            Tuple[str, List]: A tuple containing an empty string and the updated chatbot instance.
            
        Raises:
            Exception: If there's an error during vector database preparation.
        """
        try:
            logger.info(f"Processing uploaded files. RAG option: {rag_with_dropdown}")
            
            # Validate the uploaded files
            if not UploadFile.validate_files(files_dir):
                error_msg = "No valid files were uploaded or files are in unsupported format."
                logger.warning(error_msg)
                chatbot.append((" ", f"Error: {error_msg}"))
                return "", chatbot
            
            if rag_with_dropdown == "Upload docs to chat with:":
                logger.info(f"Creating vector database from {len(files_dir)} files")
                
                try:
                    prepare_vectordb_instance = PrepareVectorDB(
                        data_directory=files_dir,
                        persist_directory=APP_CONFIG.custom_persist_directory,
                        embedding_model_engine=APP_CONFIG.embedding_model_engine,
                        chunk_size=APP_CONFIG.chunk_size,
                        chunk_overlap=APP_CONFIG.chunk_overlap
                    )
                    
                    prepare_vectordb_instance.prepare_and_save_vectordb()
                    logger.info("Vector database created successfully")
                    
                    chatbot.append((" ", "✅ Uploaded files are ready for querying."))
                except Exception as e:
                    error_msg = f"Error creating vector database: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    chatbot.append((" ", f"❌ Error: {error_msg}"))
            else:
                logger.info("RAG option not selected, skipping vector database creation")
                chatbot.append(
                    (" ", "If you want to upload your own PDF, please select 'Upload docs to chat with:' from the dropdown."))
                
            return "", chatbot
            
        except Exception as e:
            error_msg = f"Unexpected error processing uploaded files: {str(e)}"
            logger.error(error_msg, exc_info=True)
            chatbot.append((" ", f"❌ Error: {error_msg}"))
            return "", chatbot

    @staticmethod
    def validate_files(files_dir: List[str]) -> bool:
        """
        Validates that the uploaded files exist and are in supported formats.
        
        Parameters:
            files_dir (List[str]): List of paths to the uploaded files.
            
        Returns:
            bool: True if files are valid, False otherwise.
        """
        if not files_dir or len(files_dir) == 0:
            logger.warning("No files were uploaded")
            return False
            
        supported_extensions = ['.pdf', '.txt', '.md', '.csv', '.json']
        valid_files = []
        
        for file_path in files_dir:
            if not os.path.exists(file_path):
                logger.warning(f"File does not exist: {file_path}")
                continue
                
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in supported_extensions:
                logger.warning(f"Unsupported file format: {ext} for file {file_path}")
                continue
                
            valid_files.append(file_path)
            
        if not valid_files:
            logger.warning("No valid files found among the uploaded files")
            return False
            
        logger.info(f"Validated {len(valid_files)} files out of {len(files_dir)} uploaded")
        return True
