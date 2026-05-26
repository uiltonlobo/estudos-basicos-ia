# Instale o SDK oficial: pip install qdrant-client
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff, PointStruct

# 1. Inicializa o cliente Qdrant (Em modo In-Memory para desenvolvimento rápido)
# Em produção, você passaria o host/porta: QdrantClient(url="http://localhost:6333")
db_client = QdrantClient(":memory:")

NOME_COLECAO = "infraestrutura_telecom"

# 2. Criando uma Coleção (Equivalente a uma Tabela no SQL ou Coleção no MongoDB)
db_client.create_collection(
    collection_name=NOME_COLECAO,
    # Configura os parâmetros globais dos vetores que este banco vai aceitar
    vectors_config=VectorParams(
        size=3,  # Simulando vetores pequenos de 3 dimensões para visualização
        distance=Distance.COSINE # Configura a métrica de distância na raiz do banco
    ),
    # Customização Avançada do Índice HNSW para Engenharia de Produção
    hnsw_config=HnswConfigDiff(
        m=16,          # Número máximo de conexões de borda para cada nó no grafo
        ef_construct=100, # Controla o trade-off entre tempo de indexação e acurácia
        full_scan_threshold=10000 # Faz busca linear se a coleção for menor que isso
    )
)

print(f"[Banco] Coleção '{NOME_COLECAO}' criada com índice HNSW customizado!")

# Este código comentado como realizar a inserção de pontos e verificar o status da coleção, 
# garantindo que o índice HNSW esteja ativo e otimizado para consultas de alta performance.
# Basta descomentá-lo e executá-lo para ver o processo completo em ação.
"""
# 2.1. Inserindo pontos na coleção para gerar contagem > 0
db_client.upsert(
    collection_name=NOME_COLECAO,
    points=[
        PointStruct(id=1, vector=[0.12, 0.80, 0.44], payload={"sistema": "billing"}),
        PointStruct(id=2, vector=[0.66, 0.10, 0.71], payload={"sistema": "crm"}),
        PointStruct(id=3, vector=[0.30, 0.55, 0.91], payload={"sistema": "rede"}),
    ],
    wait=True,
)

print("[Banco] 3 pontos inseridos na coleção.")
"""

# 3. Verificando o Schema e Status da Coleção
info_colecao = db_client.get_collection(collection_name=NOME_COLECAO)
# print(f"[Status] Vetores ativos na coleção: {info_colecao.vectors_count}")    <-- Método antigo, agora obsoleto
print(f"[Status] Quantidade de pontos armazenados: {info_colecao.points_count}")
print(f"[Status] Quantidade de vetores já indexados na coleção: {info_colecao.indexed_vectors_count}")
print(f"[Status] Método de Distância: {info_colecao.config.params.vectors.distance}")