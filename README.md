# Ingestão e Busca Semântica com LangChain e Postgres

Sistema de busca semântica que permite fazer perguntas sobre o conteúdo de um arquivo PDF usando LangChain, Gemini e PostgreSQL com pgVector.

## ?? Requisitos

- Python 3.10+
- Docker e Docker Compose
- Chave de API do Google Gemini

## ?? Instalação e Configuração

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd langchain-postgres-semantic-search
```

### 2. Configure o ambiente virtual Python

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure os seguintes valores:

```env
# Gemini API Key (obrigatório)
API_KEY=sua_chave_api_aqui

# Embedding Model (Gemini)
EMBEDDING_MODEL_NAME=models/embedding-001

# LLM Model (Gemini)
LLM_MODEL_NAME=gemini-1.5-flash

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres@123
POSTGRES_DB=postgres
POSTGRES_PORT=5430

# pgAdmin Configuration
PGADMIN_EMAIL=admin@email.com
PGADMIN_PASSWORD=admin@123
PGADMIN_PORT=8080

# Database Connection (construída a partir das variáveis acima)
DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}
```

> **Nota:** Para obter uma chave de API do Gemini, acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
> 
> **Importante:** Você pode alterar as senhas e configurações do PostgreSQL e pgAdmin conforme necessário. Certifique-se de que a `DATABASE_URL` corresponda às credenciais configuradas.

### 5. Inicie o banco de dados PostgreSQL

```bash
docker-compose up -d
```

Aguarde alguns segundos para o banco de dados inicializar completamente. Você pode verificar o status com:

```bash
docker-compose ps
```

### 6. Adicione seu arquivo PDF

Coloque o arquivo PDF que deseja processar na raiz do projeto com o nome `document.pdf`.

## ?? Como Usar

### Ingestão do PDF

Execute o script de ingestão para processar o PDF e armazenar os embeddings no banco de dados:

```bash
python src/ingest.py
```

Este script irá:
1. Carregar o arquivo `document.pdf`
2. Dividir o conteúdo em chunks de 1000 caracteres com overlap de 150
3. Gerar embeddings usando o modelo Gemini
4. Armazenar os vetores no PostgreSQL com pgVector

### Chat Interativo

Após a ingestão, inicie o chat para fazer perguntas sobre o conteúdo do PDF:

```bash
python src/chat.py
```

Exemplo de uso:

```
================================================================================
CHAT - Busca Semântica com LangChain e PostgreSQL
================================================================================

Digite 'sair' para encerrar o chat.

Faça sua pergunta:
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

--------------------------------------------------------------------------------

Faça sua pergunta:
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

--------------------------------------------------------------------------------

Faça sua pergunta:
PERGUNTA: sair

Encerrando chat. Até logo!
```

### Busca Simples (Opcional)

Para testar a busca semântica sem o chat completo:

```bash
python src/search.py
```

## ??? Estrutura do Projeto

```
??? docker-compose.yml          # Configuração do PostgreSQL e pgAdmin
??? requirements.txt            # Dependências Python
??? .env.example                # Template das variáveis de ambiente
??? .env                        # Variáveis de ambiente (criar a partir do .env.example)
??? document.pdf                # PDF para ingestão (adicionar manualmente)
??? Postgres/
?   ??? Dockerfile              # Dockerfile do PostgreSQL com pgVector
??? src/
?   ??? ingest.py               # Script de ingestão do PDF
?   ??? search.py               # Script de busca semântica
?   ??? chat.py                 # CLI para interação com usuário
??? README.md                   # Este arquivo
```

## ?? Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **LangChain**: Framework para aplicações com LLMs
- **Google Gemini**: Modelo de linguagem e embeddings
- **PostgreSQL + pgVector**: Banco de dados vetorial
- **Docker**: Containerização do banco de dados

## ??? Gerenciamento do Banco de Dados

### Acesso ao pgAdmin

O projeto inclui pgAdmin para gerenciamento visual do banco de dados:

- URL: http://localhost:8080 (ou a porta configurada em `PGADMIN_PORT`)
- Email: Conforme configurado em `PGADMIN_EMAIL` (padrão: admin@email.com)
- Senha: Conforme configurado em `PGADMIN_PASSWORD` (padrão: admin@123)

### Parar os serviços

```bash
docker-compose down
```

### Remover dados do banco (reset completo)

```bash
docker-compose down -v
rm -rf postgres/pgdata postgres/pgadmin
```

## ?? Solução de Problemas

### Erro de conexão com o banco de dados

Certifique-se de que os containers estão rodando:

```bash
docker-compose ps
```

### Erro de importação de módulos Python

Verifique se o ambiente virtual está ativado e as dependências instaladas:

```bash
pip install -r requirements.txt
```

### API Key inválida

Verifique se a chave de API do Gemini está corretamente configurada no arquivo `.env`

## ?? Notas

- O sistema responde **apenas** com base no conteúdo do PDF processado
- Perguntas fora do contexto retornam: "Não tenho informações necessárias para responder sua pergunta."
- Os chunks são armazenados com overlap para manter o contexto entre pedaços do texto
- A busca retorna os 10 resultados mais relevantes (k=10) para cada pergunta

## ?? Licença

Este projeto está sob a licença especificada no arquivo LICENSE.
