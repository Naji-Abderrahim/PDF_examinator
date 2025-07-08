from book_prep import AgentMaterial
from agent import AgentDocument
from pprint import pprint
import dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import TokenTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

if __name__ == '__main__':
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    template = """
    You are a helpful quiz master. Using the following text from the book "{book_title}", chapter "{chapter_name}", create 3 quiz questions to test understanding, with each question has its own answer, with the actual text, and metadata that has been used.

    Text:
    {text_chunk}

    Please format your questions clearly.
    """

    prompt = PromptTemplate(
        input_variables=["book_title", "chapter_name", "text_chunk"],
        template=template
    )

    quiz_chain = LLMChain(llm=llm, prompt=prompt)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    g_sp = TokenTextSplitter(
        chunk_size=256,          # max tokens per chunk
        chunk_overlap=32         # overlap between chunks
    )
# dotenv.load_dotenv('.env')

    book = AgentMaterial('./ref/thinkpython.pdf')
    book.clean_text_book()
    exit()

    docs = AgentDocument(book.vectors)
    chunks = g_sp.split_documents(docs.document)

    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_documents(docs.document, embeddings)

    vector_store.save_local("my_faiss_index")

    vector_store = FAISS.load_local("my_faiss_index", embeddings, allow_dangerous_deserialization=True)

    text_chunk = vector_store.similarity_search('Chapter 1')
    chapter_name = text_chunk[0].metadata['chapter_name']
    book_title = text_chunk[0].metadata['book_title']

    result = quiz_chain.run({
        "book_title": book_title,
        "chapter_name": chapter_name,
        "text_chunk": text_chunk
    })

    print(result)
