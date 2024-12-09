from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from abc import abstractmethod

class LocalRagDatabase():
    _EMBEDDINGS = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    def __init__(self, database_path):
        self.database_path = database_path
        self.db = None
        pass

    #Make routing here
    def load_db(self):
        if self.db == None:
            self.db = FAISS.load_local(self.database_path, LocalRagDatabase._EMBEDDINGS, allow_dangerous_deserialization=True)
        return self.db

    def search_for_similar_docs(self, text_to_search, number_of_docs_to_retrieve=4):
        return self.load_db().similarity_search(text_to_search, number_of_docs_to_retrieve)

    @abstractmethod
    def create_new_db(self):
        pass