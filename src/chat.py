import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGVector

# Carrega vari�veis de ambiente
load_dotenv()

API_KEY = os.getenv("API_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = "pdf_embeddings"


def get_context_from_db(query: str, k: int = 10) -> str:
    """
    Busca os documentos mais relevantes no banco de dados.
    
    Args:
        query: A pergunta do usu�rio
        k: N�mero de resultados a buscar (padr�o: 10)
    
    Returns:
        String com o contexto concatenado
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
    
    # Busca documentos similares
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    # Concatena os resultados
    context_parts = []
    for doc, score in results:
        context_parts.append(doc.page_content)
    
    return "\n\n".join(context_parts)


def build_prompt(context: str, question: str) -> str:
    """
    Constr�i o prompt para a LLM com base no contexto e na pergunta.
    
    Args:
        context: Contexto recuperado do banco de dados
        question: Pergunta do usu�rio
    
    Returns:
        Prompt formatado
    """
    prompt = f"""CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informa��o n�o estiver explicitamente no CONTEXTO, responda:
  "N�o tenho informa��es necess�rias para responder sua pergunta."
- NUNCA invente ou use conhecimento externo.
- NUNCA produza opini�es ou interpreta��es al�m do que est� escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual � a capital da Fran�a?"
Resposta: "N�o tenho informa��es necess�rias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "N�o tenho informa��es necess�rias para responder sua pergunta."

Pergunta: "Voc� acha isso bom ou ruim?"
Resposta: "N�o tenho informa��es necess�rias para responder sua pergunta."

PERGUNTA DO USU�RIO:
{question}

RESPONDA A "PERGUNTA DO USU�RIO"
"""
    return prompt


def ask_llm(prompt: str) -> str:
    """
    Envia o prompt para a LLM e retorna a resposta.
    
    Args:
        prompt: Prompt formatado
    
    Returns:
        Resposta da LLM
    """
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=API_KEY,
        temperature=0,
    )
    
    response = llm.invoke(prompt)
    return response.content


def chat():
    """
    Interface CLI para intera��o com o usu�rio.
    """
    print("=" * 80)
    print("CHAT - Busca Sem�ntica com LangChain e PostgreSQL")
    print("=" * 80)
    print("\nDigite 'sair' para encerrar o chat.\n")
    
    while True:
        # Solicita pergunta do usu�rio
        print("Fa�a sua pergunta:")
        question = input("PERGUNTA: ").strip()
        
        # Verifica se o usu�rio quer sair
        if question.lower() in ['sair', 'exit', 'quit']:
            print("\nEncerrando chat. At� logo!")
            break
        
        # Ignora perguntas vazias
        if not question:
            print("Por favor, digite uma pergunta v�lida.\n")
            continue
        
        try:
            # Busca contexto no banco de dados
            context = get_context_from_db(question, k=10)
            
            # Verifica se encontrou contexto
            if not context:
                print("RESPOSTA: N�o tenho informa��es necess�rias para responder sua pergunta.\n")
                print("-" * 80)
                continue
            
            # Constr�i o prompt
            prompt = build_prompt(context, question)
            
            # Obt�m resposta da LLM
            answer = ask_llm(prompt)
            
            # Exibe a resposta
            print(f"RESPOSTA: {answer}\n")
            print("-" * 80)
            print()
            
        except Exception as e:
            print(f"Erro ao processar pergunta: {str(e)}\n")
            print("-" * 80)
            print()


if __name__ == "__main__":
    # Verifica se as vari�veis de ambiente est�o configuradas
    if not API_KEY:
        print("Erro: API_KEY n�o configurada no arquivo .env")
        exit(1)
    
    if not EMBEDDING_MODEL_NAME:
        print("Erro: EMBEDDING_MODEL_NAME n�o configurada no arquivo .env")
        exit(1)
    
    if not LLM_MODEL_NAME:
        print("Erro: LLM_MODEL_NAME n�o configurada no arquivo .env")
        exit(1)
    
    if not DATABASE_URL:
        print("Erro: DATABASE_URL n�o configurada no arquivo .env")
        exit(1)
    
    # Inicia o chat
    chat()
