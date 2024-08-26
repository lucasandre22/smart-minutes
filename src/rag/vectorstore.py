import os
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import JSONLoader

# Use the sentence transformer package with the all-MiniLM-L6-v2 embedding model
EMBEDDINGS = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def load_db_from_text_document(file_path, db_name, chunk_size=256, chunk_overlap=0):
    """Load or create a vector local text database by reading the content from the specified document in file_path.

    Args:
        file_path (str): the file path.
        db_name (str): database name to be loaded or to be created.
        chunk_size (int, optional): _description_. Defaults to 512.
        chunk_overlap (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    if os.path.isdir(db_name):
        return FAISS.load_local(db_name, EMBEDDINGS, allow_dangerous_deserialization=True)
    else:
        raw_documents = TextLoader(file_path, encoding="utf8").load()
        # Split the document into chunks
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        documents_splitted = text_splitter.split_documents(raw_documents)
        texts = [doc.page_content for doc in documents_splitted]
        db = FAISS.from_texts(
            texts = texts,
            embedding = EMBEDDINGS
        )
        db.save_local(db_name)
        return db
    
def load_db_from_text_document_chroma(file_path, db_name, chunk_size=128, chunk_overlap=0):
    """Load or create a vector local text database by reading the content from the specified document in file_path.

    Args:
        file_path (str): the file path.
        db_name (str): database name to be loaded or to be created.
        chunk_size (int, optional): _description_. Defaults to 512.
        chunk_overlap (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    if os.path.isdir(db_name):
        return FAISS.load_local(db_name, EMBEDDINGS, allow_dangerous_deserialization=True)
    else:
        raw_documents = TextLoader(file_path, encoding="utf8").load()
        # Split the document into chunks
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        documents = text_splitter.split_documents(raw_documents)
        db = Chroma.from_documents(documents, EMBEDDINGS)
        db.save_local(db_name)
        return db

def load_db_from_json_lines(file_path, db_name='podcast', jq_schema=".content", json_lines=True):
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
            jq_schema=jq_schema,
            text_content=False,
            json_lines=json_lines
        )
        data = loader.load()
        db = FAISS.from_documents(data, EMBEDDINGS)
        db.save_local(db_name)
        return db

def test_text():
    db = load_db_from_text_document("D:\\Git\\tcc\\langchain\\examples\\state_of_the_union.txt", db_name='state')
    # Simple retrieval using similarity search
    question = "What did the president say about the ukrainian people?"
    data = db.similarity_search(question)
    print("Length:", len(data))
    print("Result:", data[0].page_content)
    # Print results
    for doc in data:
        print(str(doc.page_content[:300]))
        print("----------")
        
def test_jsonl():
    db = load_db_from_json_lines("/mnt/d/Git/tcc/documents/Emilias_podcast_99_ Anne_Lesinhovski_small.jsonl",
                                 db_name='podcast',
                                 jq_schema=".content")

    question = "O que é Emilias Podcast?"
    data = db.similarity_search(question)
    for i in data:
        print("Result:", i.page_content)

if __name__ == "__main__":
    #db = load_db_from_text_document("D:\\Git\\tcc\\langchain\\examples\\state_of_the_union.txt", db_name='state')
    db = load_db_from_text_document("D:\\Git\\tcc\\documents\\Emilias_podcast_99_ Anne_Lesinhovski_medium.txt", db_name='podcast_db', chunk_size=256)
    question = "O que é Emilias Podcast?"
    data = db.similarity_search(question)
    print("Result:", data[0].page_content)