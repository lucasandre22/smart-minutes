from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import JSONLoader
from .local_rag_database import LocalRagDatabase
import json

class JsonlRagDatabase(LocalRagDatabase):
    def __init__(self, database_path, jsonl_file_path=""):
        LocalRagDatabase.__init__(self, database_path)
        self.jsonl_file_path = jsonl_file_path
    
    def update_db(self, data):
        json_data = ""
        with open(self.jsonl_file_path, 'r') as file:
            json_data = json.load(file)
            json_data["content"].append(data)
        with open(self.jsonl_file_path, "w") as jsonl_file:
            jsonl_file.write(json.dumps(json_data) + "\n")
        self._create_new_db(self.jsonl_file_path)

    def _create_new_db(self, file_path):
        loader = JSONLoader(
            file_path=file_path,
            text_content=True,
            jq_schema=".content[].summary",
            json_lines=False
        )
        data = loader.load()
        self.db = FAISS.from_documents(data, LocalRagDatabase._EMBEDDINGS)
        self.db.save_local(self.database_path)