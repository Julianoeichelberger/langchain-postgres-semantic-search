import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

# Carrega variáveis de ambiente
load_dotenv()

API_KEY = os.getenv("API_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = "pdf_embeddings"


def search(query: str, k: int = 10):
    """
    Realiza uma busca semântica no banco de dados vetorial.
    
    Args:
        query: A pergunta/consulta do usuário
        k: Número de resultados a retornar (padrão: 10)
    
    Returns:
        Lista de tuplas (documento, score) com os resultados mais relevantes
    """
    # Configura embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=API_KEY
    )
    
    # Conecta ao vector store
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )
    
    # Busca documentos similares com score
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    return results


if __name__ == "__main__":
    # Teste simples
    test_query = "Qual o faturamento da empresa?"
    
    print(f"Buscando por: '{test_query}'\n")
    
    results = search(test_query)
    
    print(f"Encontrados {len(results)} resultados:\n")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"Resultado {i} (Score: {score:.4f}):")
        print(f"Conteúdo: {doc.page_content[:200]}...")
        print(f"Metadata: {doc.metadata}")
        print("-" * 80)
