# LangChain is a framework and toolkit for interacting with LLMs programmatically
import os
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader

# Load the document using a LangChain text loader
loader = TextLoader("D:\\Git\\tcc\\langchain\\examples\\state_of_the_union.txt", encoding="utf8")
documents = loader.load()

DB_NAME = "state"

# Split the document into chunks
text_splitter = CharacterTextSplitter (chunk_size=512, chunk_overlap=0)
#text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=200)
docs = text_splitter.split_documents(documents)
texts = [doc.page_content for doc in docs]

# Use the sentence transformer package with the all-MiniLM-L6-v2 embedding model
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Load the text embeddings in SQLiteVSS in a table named state_union
db = None
if os.path.isdir(DB_NAME):
    db = FAISS.from_texts(
        texts = texts,
        embedding = embedding_function
    )
    db.save_local(DB_NAME)
else:
    db = FAISS.load_local(DB_NAME, embedding_function)

# First, we will do a simple retrieval using similarity search
# Query
question = "What did the president say about the ukrainian people?"
data = db.similarity_search(question)
print("Length:", len(data))
print("Result:", data[0].page_content)
# print results
for doc in docs:
    print(str(doc.page_content[:300]))
    print("----------")