
import openai
import os
from dotenv import load_dotenv
import yaml
from langchain.embeddings.openai import OpenAIEmbeddings
from pyprojroot import here # for creating top-level directories in project without changing setwd()
import shutil

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
    """

    def __init__(self) -> None:
        with open(here("frontend/configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        # llm configs
        self.llm_model = app_config["llm_config"]["model"]
        self.llm_system_role = app_config["llm_config"]["llm_system_role"]
        self.persist_directory = str(here(app_config["directories"]["persist_directory"]))  # converting to string for adding in chromadb backend: self._settings.require("persist_directory") + "/chroma.sqlite3"
        self.custom_persist_directory = str(here(app_config["directories"]["custom_persist_directory"]))
        self.embedding_model = OpenAIEmbeddings()

        # Retrieval configs
        self.data_directory = app_config["directories"]["data_directory"]
        self.k = app_config["retrieval_config"]["k"]
        self.embedding_model_engine = app_config["embedding_model_config"]["engine"]
        self.chunk_size = app_config["splitter_config"]["chunk_size"]
        self.chunk_overlap = app_config["splitter_config"]["chunk_overlap"]

        self.temperature = app_config["llm_config"]["temperature"]

        # Memory
        self.qa_pair_count = app_config["memory"]["qa_pair_count"]

        # Load OpenAI credentials
        #self.load_openai_cfg()

        # clean up the upload doc vectordb if it exists
        self.create_directory(self.persist_directory)
        self.remove_directory(self.custom_persist_directory)


    def create_directory(self, directory_path: str):
        """
        Create a directory if it does not exist.

        Parameters:
            directory_path (str): The path of the directory to be created.
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def remove_directory(self, directory_path: str):
        """
        Removes the specified directory.

        Parameters:
            directory_path (str): The path of the directory to be removed.

        Raises:
            OSError: If an error occurs during the directory removal process.

        Returns:
            None
        """
        if os.path.exists(directory_path):
            try:
                shutil.rmtree(directory_path)
                print(
                    f"The directory '{directory_path}' has been successfully removed.")
            except OSError as e:
                print(f"Error: {e}")
        else:
            print(f"The directory '{directory_path}' does not exist.")