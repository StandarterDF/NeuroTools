from chromadb.utils import embedding_functions
import chromadb
import random
import Config

class ProjectDatabase:
    def __init__(self):
        self.CreateEmbedding = embedding_functions.OpenAIEmbeddingFunction(
            api_base=Config.OpenAI_API_BaseURL,
            api_key=Config.OpenAI_API_Key,
            model_name=Config.OpenAI_API_Embedding
        )
        self.DB = chromadb.Client()
    def ChromaUpdate(self, Topic, Text):
        Collection = self.DB.get_or_create_collection(Topic, embedding_function=self.CreateEmbedding)
        Collection.add(
            documents = [Text] if type(Text) == str else Text, 
            ids=[f"id_{random.randint(1000000, 9999999)}" if type(Text) == str else f"id_{random.randint(1000000, 9999999)}" for _ in range(len(Text))]
        )
    def ChromaSearch(self, Topic, Text):
        Collection = self.DB.get_or_create_collection(Topic, embedding_function=self.CreateEmbedding)
        return Collection.query(query_texts=[Text], n_results=1)['documents']