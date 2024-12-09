import os
import os.path
from langchain_community.vectorstores import FAISS
from .local_rag_database import LocalRagDatabase
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from rag.document_loader import PdfDocumentLoader
from langchain_core.documents import Document
from core.config import *
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain_community.llms import Ollama
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever

#TODO inject PdfDocumentLoader, to support any kind of document loader here!!!
#TODO: https://python.langchain.com/docs/how_to/#retrievers
class DocumentRagDatabase(LocalRagDatabase):
    def __init__(self, database_path):
        LocalRagDatabase.__init__(self, database_path)
        
    def update_db(self, docs: list[Document]):
        if not self.db:
            self.db = FAISS.from_documents(docs, LocalRagDatabase._EMBEDDINGS)
        self.db.add_documents(docs)

    def save_local(self):
        self.db.save_local(self.database_path)

    def update_and_save_db(self, docs: list[Document]):
        self.db.add_documents(docs)
        self.db.save_local()

    def get_retriever(self):
        return self.db.as_retriever()

    def create_new_db(self, document_loader: PdfDocumentLoader):
        data = document_loader.docs
        self.db = FAISS.from_documents(data, LocalRagDatabase._EMBEDDINGS)
        print("Saving newly created DB...")
        self.db.save_local(self.database_path)

    def chain_filter(self, text_to_search):
        llm = Ollama(
            model="lucasalmeida/gemma-2-9b-it-sppo-iter3:Q4_K_M",
            verbose=True,
            temperature=0
        )
        _filter = LLMChainFilter.from_llm(llm)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=_filter, base_retriever=self.db.as_retriever()
        )
        return compression_retriever.invoke(text_to_search)

    #TODO: Implement a classifier for the retrieved documents
    def multi_query_retriever(self, text_to_search):
        llm = Ollama(
            model="lucasalmeida/gemma-2-9b-it-sppo-iter3:Q4_K_M",
            verbose=True,
            temperature=0
        )
        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=self.db.as_retriever(), llm=llm
        )
        return retriever_from_llm.invoke(text_to_search)


#Example to create a database
if __name__ == "__main__":
    #MY_DOC_PATH = os.path.join(os.getenv("DOCUMENTS_PATH"), "Regulamento do PPGCA.pdf")
    MY_DOC_PATH = os.getenv("DOCUMENTS_PATH")
    DOCS_DATABASE_PATH = os.getenv("DOCUMENT_DATABASE_PATH")
    mydatabase = DocumentRagDatabase(DOCS_DATABASE_PATH)
    #mydatabase.load_db()

    for file_name in os.listdir(MY_DOC_PATH):
        file_path = os.path.join(MY_DOC_PATH, file_name)
        if os.path.isfile(file_path):
            print("Processing file:", file_path)
            mypdf = PdfDocumentLoader(file_path, 1024, True)
            #TODO: include the summary of the document in a database?
            mydatabase.update_db(mypdf.docs)
    
    mydatabase.save_local()
    docs = mydatabase.search_for_similar_docs("de acordo com o paragrafo 4 da Resolução PPGCA 01/2018")
    print(docs[0])
    
#Example to create a database
# if __name__ == "__main__":
#     MY_DOC_PATH = os.path.join(os.getenv("DOCUMENT_DATABASE_PATH"), "Regulamento do PPGCA.pdf")
    
#     DOCS_DATABASE_PATH = os.path.join("databases", "document_database")
#     mypdf = PdfDocumentLoader(MY_DOC_PATH, 500, True)
#     mydatabase = DocumentRagDatabase(DOCS_DATABASE_PATH)
#     mydatabase.create_new_db(mypdf)
#     docs = mydatabase.search_for_similar_docs("de acordo com o paragrafo 4 da Resolução PPGCA 01/2018")
#     print(docs[0])