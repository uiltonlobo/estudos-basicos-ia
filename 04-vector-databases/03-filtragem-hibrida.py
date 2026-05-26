from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Conectamos ao banco simulado que já possui os dados da iteração anterior
db_client = QdrantClient(":memory:")
NOME_COLECAO = "documentacao_api"

# (Apenas re-criando o cenário da iteração passada de forma rápida para o script rodar isolado)
from qdrant_client.models import VectorParams, Distance, PointStruct
db_client.create_collection(NOME_COLECAO, vectors_config=VectorParams(size=3, distance=Distance.COSINE))
db_client.upsert(NOME_COLECAO, points=[
    PointStruct(id=1, vector=[0.12, 0.78, -0.05], payload={"texto_original": "O endpoint /v1/auth gera tokens JWT.", "categoria_modulo": "Segurança", "ambiente": "producao"}),
    PointStruct(id=2, vector=[-0.45, 0.12, 0.88], payload={"texto_original": "Para listar produtos use GET /v1/products.", "categoria_modulo": "Catálogo", "ambiente": "producao"}),
    PointStruct(id=3, vector=[0.10, 0.75, -0.02], payload={"texto_original": "Bypass de login para testes locais de homologação.", "categoria_modulo": "Segurança", "ambiente": "staging"})
])

# --- EXECUÇÃO DA BUSCA HÍBRIDA (PRÉ-FILTRAGEM) ---

# 1. Vetor gerado a partir da pergunta do usuário: "Como autenticar na API?"
vetor_query_usuario = [0.11, 0.80, -0.04]

print("[Agente] Executando busca semântica com cláusulas rígidas de pré-filtragem...")

# 2. Executa a busca aplicando o filtro na raiz do grafo HNSW
resposta = db_client.query_points(
    collection_name=NOME_COLECAO,
    query=vetor_query_usuario,
    limit=2, # Traga apenas as 2 melhores correspondências
    
    # CONTEXTO DE ENGENHARIA: Aplicando a Pré-Filtragem (Pre-filtering)
    query_filter=Filter(
        must=[
            FieldCondition(
                key="categoria_modulo",
                match=MatchValue(value="Segurança") # Garante que só trará dados de segurança
            ),
            FieldCondition(
                key="ambiente",
                match=MatchValue(value="producao") # Segurança máxima: impede vazamento de dados de staging/homologação
            )
        ]
    )
)

resultados = resposta.points

# 3. Print dos resultados validados
print("\n=======================================================")
print(f"Resultados encontrados que passaram no filtro: {len(resultados)}")
print("=======================================================\n")

for item in resultados:
    print(f"Score de Similaridade: {item.score:.4f}")
    print(f"Módulo: {item.payload['categoria_modulo']} | Ambiente: {item.payload['ambiente']}")
    print(f"Texto Extraído: {item.payload['texto_original']}")
    print("-" * 55)