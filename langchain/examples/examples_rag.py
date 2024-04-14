# LangChain is a framework and toolkit for interacting with LLMs programmatically

from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import SQLiteVSS
from langchain_community.document_loaders import TextLoader

# Load the document using a LangChain text loader
loader = TextLoader("D:\\Git\\tcc\\langchain\\examples\\state_of_the_union.txt", encoding="utf8")
documents = loader.load()

# Split the document into chunks
text_splitter = CharacterTextSplitter (chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
texts = [doc.page_content for doc in docs]

# Use the sentence transformer package with the all-MiniLM-L6-v2 embedding model
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Load the text embeddings in SQLiteVSS in a table named state_union
db = SQLiteVSS.from_texts(
    texts = texts,
    embedding = embedding_function,
    table = "state_union",
    db_file = "/tmp/vss.db"
)

# First, we will do a simple retrieval using similarity search
# Query
question = "What did the president say about Nancy Pelosi?"
data = db.similarity_search(question)

# print results
print(data[0].page_content)