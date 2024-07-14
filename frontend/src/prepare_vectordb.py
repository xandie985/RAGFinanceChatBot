import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings


class PrepareVectorDB:
    """
    A class for preparing and saving a VectorDB using OpenAI embeddings.

    Involves process of loading documents, chunking them, and creating a VectorDB 
    with OpenAI embeddings. contains methods to prepare & save the vecotordb.

    Parameters:
        data_directory (str):  Directory or list of directories containing the documents.
        persist_directory (str): Directory to save the VectorDB.
        embedding_model_engine (str): The engine for OpenAI embeddings.
        chunk_size (int): The size of the chunks for document processing.
        chunk_overlap (int): The overlap between chunks.
    """

    def __init__(
            self,
            data_directory: str,
            persist_directory: str,
            embedding_model_engine: str,
            chunk_size: int,
            chunk_overlap: int) -> None:
        
        """
        Initializing the PrepareVectorDB instance.

        Parameters:
            data_directory (str):  Directory or list of directories containing the documents.
            persist_directory (str): Directory to save the VectorDB.
            embedding_model_engine (str): The engine for OpenAI embeddings.
            chunk_size (int): The size of the chunks for document processing.
            chunk_overlap (int): The overlap between chunks.
        """

        self.embedding_model_engine = embedding_model_engine
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        """choices: MarkdownHeaderTextSplitter,TokenTextSplitter, etc."""
        self.data_directory = data_directory
        self.persist_directory = persist_directory
        self.embedding = OpenAIEmbeddings()

    def __load_all_documents(self) -> List:
        """
        Load all documents from the specified directory or directories and 
        handles the documents obtained live during chat. 

        Returns:
            List: A list of loaded documents.
        """
        doc_counter = 0
        if isinstance(self.data_directory, list):
            print("Loading the uploaded documents...")
            docs = [doc for doc_dir in self.data_directory
                    for doc in PyPDFLoader(doc_dir).load()]
        else:
            print("Loading documents manually...")
            document_list = os.listdir(self.data_directory)
            docs = [doc for doc_name in document_list
                    for doc in PyPDFLoader(os.path.join(
                        self.data_directory, doc_name)).load()]
        doc_counter = len(docs)
        print(f"Number of loaded documents: {doc_counter}")
        print(f"Number of pages: {len(docs)}\n\n")

        return docs

    def __chunk_documents(self, docs: List) -> List:
        """
        Chunk the loaded documents using the specified text splitter.
        Parameters:
            docs (List): The list of loaded documents.
        Returns:
            List: A list of chunked documents.
        """
        print("Chunking documents...")
        chunked_documents = self.text_splitter.split_documents(docs)
        print("Number of chunks:", len(chunked_documents), "\n\n")
        return chunked_documents

    def prepare_and_save_vectordb(self):
        """
        Load, chunk, and create a VectorDB with OpenAI embeddings, and save it.

        Returns:
            Chroma: The created VectorDB.
        """
        docs = self.__load_all_documents()
        chunked_documents = self.__chunk_documents(docs)
        print("Preparing vectordb...")
        vectordb = Chroma.from_documents(
            documents=chunked_documents,
            embedding=self.embedding,
            persist_directory=self.persist_directory
        )
        print("Vectordb created and saved!")
        print("Number of vectors in vectordb:", vectordb._collection.count(), "\n\n")
        return vectordb
    