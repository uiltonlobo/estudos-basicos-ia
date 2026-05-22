import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# 1. Inicializa o cliente ChromaDB (aqui em modo persistente local, simulando um banco)
# Em produção, seria: client = chromadb.HttpClient(host='localhost', port=8000)
chroma_client = chromadb.PersistentClient(path="./meu_chroma_db")

# 2. Configura a função de embedding padrão usando a API Key do ambiente
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# 3. Cria ou obtém uma Coleção (equivalente a uma Tabela no SQL ou Collection no MongoDB)
collection = chroma_client.get_or_create_collection(
    name="logs_sistema", 
    embedding_function=openai_ef,
    metadata={"hnsw:space": "cosine"} # Define explicitamente a métrica de distância
)

# 4. Inserindo dados (O ChromaDB lida com a geração dos embeddings internamente via 'openai_ef')
collection.upsert(
    documents=[
        "Erro de Timeout na API de Pagamentos Stripe.",
        "Refatoração de código pendente na controller de usuários.",
        "Alerta de segurança: Múltiplas tentativas de login inválidas."
    ],
    metadatas=[
        {"modulo": "financeiro", "severidade": "critico"},
        {"modulo": "auth", "severidade": "baixo"},
        {"modulo": "seguranca", "severidade": "alto"}
    ],
    ids=["id_log_001", "id_log_002", "id_log_003"]
)

# 5. Executando a Busca Semântica com Filtragem de Metadados (Metadata Filtering)
query_texto = "Houve falha ao processar a cobrança do cliente"

resultados = collection.query(
    query_texts=[query_texto],
    n_results=1, # Traz apenas o top 1 mais próximo
    where={"severidade": "critico"} # Filtro híbrido clássico (Vetorial + Atributo Relacional)
)

# Exibindo o resultado
for doc, meta, dist in zip(resultados['documents'][0], resultados['metadatas'][0], resultados['distances'][0]):
    print(f"Resultado Encontrado: '{doc}'")
    print(f"Metadados: {meta}")
    print(f"Distância/Mapeamento: {dist:.4f} (Menor distância = mais próximo)")