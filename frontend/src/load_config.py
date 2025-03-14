import openai
import os
import logging
from dotenv import load_dotenv
import yaml
from langchain_openai import OpenAIEmbeddings
from pyprojroot import here # for creating top-level directories in project without changing setwd()
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("config.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Config")

# Load environment variables
load_dotenv()


class LoadConfig:
    """
    A class for loading configuration settings and managing directories.

    This class loads various configuration settings from the 'app_config.yml' file,
    including LLM configurations, retrieval configurations, and memory configurations. 
    It also performs directory-related operations such as creating and removing directories.

    ...

    Attributes:
        llm_engine : str
            The language model engine specified in the configuration.
        llm_system_role : str
            The role of the language model system specified in the configuration.
        persist_directory : str
            The path to the persist directory where data is stored.
        custom_persist_directory : str
            The path to the custom persist directory.
        embedding_model : OpenAIEmbeddings
            An instance of the OpenAIEmbeddings class for language model embeddings.
        data_directory : str
            The path to the data directory.
        k : int
            The value of 'k' specified in the retrieval configuration.
        embedding_model_engine : str
            The engine specified in the embedding model configuration.
        chunk_size : int
            The chunk size specified in the splitter configuration.
        chunk_overlap : int
            The chunk overlap specified in the splitter configuration.
        temperature : float
            The temperature specified in the LLM configuration.
        qa_pair_count : int
            The number of question-answer pairs specified in the memory configuration.

    Methods:
        create_directory(directory_path):
            Create a directory if it does not exist.
        remove_directory(directory_path):
            Removes the specified directory.
        validate_config():
            Validates that all required configuration settings are present and valid.
        validate_api_keys():
            Validates that required API keys are set in environment variables.
    """

    def __init__(self) -> None:
        """
        Initialize the LoadConfig class by loading configuration settings from app_config.yml.
        
        Raises:
            FileNotFoundError: If the configuration file cannot be found.
            yaml.YAMLError: If the configuration file is not valid YAML.
            KeyError: If a required configuration key is missing.
        """
        try:
            config_path = here("configs/app_config.yml")
            logger.info(f"Loading configuration from {config_path}")
            
            with open(config_path) as cfg:
                app_config = yaml.load(cfg, Loader=yaml.FullLoader)
            
            # Load LLM configs
            self._load_llm_configs(app_config)
            
            # Load directory configs
            self._load_directory_configs(app_config)
            
            # Load retrieval configs
            self._load_retrieval_configs(app_config)
            
            # Load memory configs
            self._load_memory_configs(app_config)
            
            # Validate the loaded configuration
            self.validate_config()
            
            # Validate API keys
            self.validate_api_keys()
            
            # Initialize directories
            self._initialize_directories()
            
            logger.info("Configuration loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {e}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing required configuration key: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            raise

    def _load_llm_configs(self, app_config):
        """Load language model configuration settings."""
        try:
            llm_config = app_config["llm_config"]
            self.gpt_model = llm_config["gpt_model"]
            self.llama3_70bmodel = llm_config["llama3_70bmodel"]
            self.llm_system_role = llm_config["llm_system_role"]
            self.temperature = llm_config["temperature"]
            logger.debug(f"Loaded LLM configs: {self.gpt_model}, {self.llama3_70bmodel}")
        except KeyError as e:
            logger.error(f"Missing LLM configuration key: {e}")
            raise

    def _load_directory_configs(self, app_config):
        """Load directory configuration settings."""
        try:
            directories = app_config["directories"]
            self.persist_directory = str(here(directories["persist_directory"]))
            self.custom_persist_directory = str(here(directories["custom_persist_directory"]))
            self.data_directory = directories["data_directory"]
            logger.debug(f"Loaded directory configs: {self.persist_directory}, {self.custom_persist_directory}")
        except KeyError as e:
            logger.error(f"Missing directory configuration key: {e}")
            raise
        
        # Initialize embedding model
        try:
            self.embedding_model = OpenAIEmbeddings()
            logger.debug("OpenAI embeddings model initialized")
        except Exception as e:
            logger.error(f"Error initializing OpenAI embeddings: {e}")
            raise

    def _load_retrieval_configs(self, app_config):
        """Load retrieval configuration settings."""
        try:
            self.k = app_config["retrieval_config"]["k"]
            self.num_of_final_doc = app_config["retrieval_config"]["num_of_final_doc"]
            self.embedding_model_engine = app_config["embedding_model_config"]["engine"]
            self.chunk_size = app_config["splitter_config"]["chunk_size"]
            self.chunk_overlap = app_config["splitter_config"]["chunk_overlap"]
            logger.debug(f"Loaded retrieval configs: k={self.k}, chunk_size={self.chunk_size}")
        except KeyError as e:
            logger.error(f"Missing retrieval configuration key: {e}")
            raise

    def _load_memory_configs(self, app_config):
        """Load memory configuration settings."""
        try:
            self.qa_pair_count = app_config["memory"]["qa_pair_count"]
            logger.debug(f"Loaded memory configs: qa_pair_count={self.qa_pair_count}")
        except KeyError as e:
            logger.error(f"Missing memory configuration key: {e}")
            raise

    def _initialize_directories(self):
        """Initialize required directories."""
        try:
            # Create persist directory if it doesn't exist
            self.create_directory(self.persist_directory)
            logger.info(f"Created/verified persist directory: {self.persist_directory}")
            
            # Remove custom persist directory if it exists (clean start)
            self.remove_directory(self.custom_persist_directory)
            logger.info(f"Removed custom persist directory (if existed): {self.custom_persist_directory}")
        except Exception as e:
            logger.error(f"Error initializing directories: {e}")
            raise

    def create_directory(self, directory_path: str):
        """
        Create a directory if it does not exist.

        Parameters:
            directory_path (str): The path of the directory to be created.
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                logger.info(f"Created directory: {directory_path}")
            else:
                logger.debug(f"Directory already exists: {directory_path}")
        except Exception as e:
            logger.error(f"Error creating directory {directory_path}: {e}")
            raise

    def remove_directory(self, directory_path: str):
        """
        Removes the specified directory.

        Parameters:
            directory_path (str): The path of the directory to be removed.

        Raises:
            OSError: If an error occurs during the directory removal process.
        """
        try:
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)
                logger.info(f"Removed directory: {directory_path}")
            else:
                logger.debug(f"Directory does not exist: {directory_path}")
        except OSError as e:
            logger.error(f"Error removing directory {directory_path}: {e}")
            raise

    def validate_config(self):
        """
        Validates that all required configuration settings are present and valid.
        
        Raises:
            ValueError: If any configuration setting is invalid.
        """
        # Validate numeric values
        if not isinstance(self.k, int) or self.k <= 0:
            error_msg = f"Invalid k value: {self.k}. Must be a positive integer."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not isinstance(self.chunk_size, int) or self.chunk_size <= 0:
            error_msg = f"Invalid chunk_size: {self.chunk_size}. Must be a positive integer."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not isinstance(self.chunk_overlap, int) or self.chunk_overlap < 0:
            error_msg = f"Invalid chunk_overlap: {self.chunk_overlap}. Must be a non-negative integer."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not isinstance(self.temperature, (int, float)) or self.temperature < 0 or self.temperature > 1:
            error_msg = f"Invalid temperature: {self.temperature}. Must be between 0 and 1."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not isinstance(self.qa_pair_count, int) or self.qa_pair_count <= 0:
            error_msg = f"Invalid qa_pair_count: {self.qa_pair_count}. Must be a positive integer."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Validate string values
        if not self.llm_system_role or not isinstance(self.llm_system_role, str):
            error_msg = "Invalid or missing llm_system_role."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not self.embedding_model_engine or not isinstance(self.embedding_model_engine, str):
            error_msg = "Invalid or missing embedding_model_engine."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("Configuration validation successful")

    def validate_api_keys(self):
        """
        Validates that required API keys are set in environment variables.
        
        Raises:
            ValueError: If any required API key is missing.
        """
        openai_api_key = os.getenv("OPENAI_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not openai_api_key:
            warning_msg = "OPENAI_API_KEY environment variable is not set. OpenAI models will not work."
            logger.warning(warning_msg)
            
        if not groq_api_key:
            warning_msg = "GROQ_API_KEY environment variable is not set. Groq models will not work."
            logger.warning(warning_msg)
            
        if not openai_api_key and not groq_api_key:
            error_msg = "No API keys found. At least one of OPENAI_API_KEY or GROQ_API_KEY must be set."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("API key validation completed")