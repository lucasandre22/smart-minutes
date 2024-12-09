import os
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import JSONLoader
import json

# Use the sentence transformer package with the all-MiniLM-L6-v2 embedding model
EMBEDDINGS = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
DATABASE = None
JSONL_FILE_NAME = "/mnt/d/Git/trabalho-metologias-ageis/documents/tickets.jsonl"
DATABASE_NAME = "backend/tickets_database"

def load_db_from_json_lines(file_path, db_name, json_lines=True):
    """Load or create a vector local json lines database by reading the file specified in file_path.

    Args:
        file_path (str): the file path.
        db_name (str): database name to be loaded or to be created.
        jq_schema (str): json field to read inside the json lines file.
        json_lines (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    if os.path.isdir(db_name):
        return FAISS.load_local(db_name, EMBEDDINGS, allow_dangerous_deserialization=True)
    else:
        loader = JSONLoader(
            file_path=file_path,
            text_content=False,
            jq_schema=".summary",
            json_lines=json_lines
        )
        data = loader.load()
        db = FAISS.from_documents(data, EMBEDDINGS)
        db.save_local(db_name)
        return db
    
def search_for_similar_tickets(text_to_search):
    global DATABASE
    if DATABASE is None:
        DATABASE = load_db_from_json_lines(JSONL_FILE_NAME, DATABASE_NAME)
    if text_to_search is not str:
        text_to_search = json.dumps(text_to_search)
    data = DATABASE.similarity_search(text_to_search, k=4)
    tickets = []
    for page in data:
        tickets.append(json.loads(page.page_content))
    return tickets

if __name__ == "__main__":
    DATABASE = load_db_from_json_lines(JSONL_FILE_NAME, DATABASE_NAME)
    text_to_search = "METHODS-5?"
    tickets = search_for_similar_tickets(text_to_search)