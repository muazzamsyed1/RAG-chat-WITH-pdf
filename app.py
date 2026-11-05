from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
## for ui design
import streamlit as st
### for v datbases
from langchain_community.vectorstores import InMemoryVectorStore
from time import sleep

##llm defining
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

## to store chat of user and ai
if "message" not in st.session_state:
    st.session_state.message = []

def document_process(file_path):
    ## document loading
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    ##splitting
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents(docs)

    ##embedding and vector stor
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    vector_db =InMemoryVectorStore.from_documents(documents=docs, embedding=embeddings)

    st.session_state.vector_db = vector_db
    st.session_state.document_uploaded = True



st.subheader("Document Q&A ChatBot - Ask Anything")
if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

### document upload
if not st.session_state.document_uploaded:
    file = st.file_uploader(label="Select your pdf file", type="pdf")
    if file:
        with open("uploaded_document.pdf", "wb") as f:
            f.write(file.getvalue())

        with st.spinner("processing...."):
            document_process("./uploaded_document.pdf")

        st.markdown("Document Processed Successfully...")
        sleep(2)
        st.rerun()

if st.session_state.document_uploaded and st.session_state.vector_db:
    query = st.chat_input("Ask Anything...")

    for oneMessage in st.session_state.message:
        role = oneMessage["role"]
        content = oneMessage["content"]

        st.chat_message(role).markdown(content)

    if query:

        st.session_state.message.append({"role":"user", "content":query})

        ##to see content on ui  
        st.chat_message("user").markdown(query) 
                
        documents = st.session_state.vector_db.similarity_search(query, k=2)
        context = ""

        for doc in documents:
            context += doc.page_content + "\n\n"

        prompt = f"""You are a helpful assistant for user question based on provided context. context: {context} and question is: {query} """
        result = llm.invoke(prompt)

        st.session_state.message.append({"role":"ai", "content":result.content})
        st.chat_message("assistant").markdown(result.content[0]["text"])

### chat ui