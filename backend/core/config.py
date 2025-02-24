import os

os.environ["OLLAMA_API_ADDRESS"] = "http://localhost:11434"

# Configuration regarding the documents
os.environ["DOCUMENTS_PATH"] = "databases/docs"
os.environ["DOCUMENT_DATABASE_PATH"] = "databases/document_vector_database"

# Configuration regarding the transcripts
os.environ["TRANSCRIPTS_PATH"] = os.path.join("databases", "transcripts")
os.environ["PROCESSED_FILES_PATH"] = os.path.join("databases", "processed_files")

# Frontend path
os.environ["FRONTEND_PATH"] = "../frontend"

MY_DOC_PATH = os.path.join("databases", "docs", "Regulamento do PPGCA.pdf")
DOCS_DATABASE_PATH = os.path.join("databases", "document_database")

# Create the directories needed for the application
os.makedirs(os.environ["DOCUMENTS_PATH"], exist_ok=True)
os.makedirs(os.environ["TRANSCRIPTS_PATH"], exist_ok=True)
os.makedirs(os.environ["PROCESSED_FILES_PATH"], exist_ok=True)
os.makedirs(os.environ["DOCUMENT_DATABASE_PATH"], exist_ok=True)

OLLAMA_MODELS_URL = "https://ollama.com/library"

class Config():
    
    def __init__(self, model="lucasalmeida/gemma-2-9b-it-sppo-iter3:Q4_K_M", temperature=0, top_p=0, debug_traces=False):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.debug_traces = debug_traces

CONFIG = Config()