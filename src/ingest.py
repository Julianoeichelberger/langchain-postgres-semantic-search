import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

# Carrega variáveis de ambiente
load_dotenv()

API_KEY = os.getenv("API_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = "pdf_embeddings"


def ingest_pdf(pdf_path: str):
    """
    Lê um arquivo PDF, divide em chunks, gera embeddings e armazena no PostgreSQL.
    
    Args:
        pdf_path: Caminho para o arquivo PDF a ser processado
    """
    print(f"Carregando PDF: {pdf_path}")
    
    # Carrega o PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    print(f"PDF carregado com {len(documents)} página(s)")
    
    # Divide o texto em chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Documento dividido em {len(chunks)} chunks")
    
    # Configura embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=API_KEY
    )
    
    print("Gerando embeddings e armazenando no banco de dados...")
    
    # Cria/atualiza o vector store
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )
    
    # Adiciona os documentos
    vectorstore.add_documents(chunks)
    
    print(f"? Ingestão concluída! {len(chunks)} chunks foram armazenados no banco de dados.")


if __name__ == "__main__":
    # Verifica se o arquivo PDF existe
    pdf_file = "document.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"Erro: Arquivo '{pdf_file}' não encontrado!")
        print("Por favor, coloque um arquivo PDF chamado 'document.pdf' na raiz do projeto.")
        exit(1)
    
    # Verifica se as variáveis de ambiente estão configuradas
    if not API_KEY:
        print("Erro: API_KEY não configurada no arquivo .env")
        exit(1)
    
    if not EMBEDDING_MODEL_NAME:
        print("Erro: EMBEDDING_MODEL_NAME não configurada no arquivo .env")
        exit(1)
    
    if not DATABASE_URL:
        print("Erro: DATABASE_URL não configurada no arquivo .env")
        exit(1)
    
    # Executa a ingestão
    ingest_pdf(pdf_file)
