import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

db_client = QdrantClient(":memory:")
NOME_COLECAO = "documentacao_api"

db_client.create_collection(
    collection_name=NOME_COLECAO,
    vectors_config=VectorParams(size=3, distance=Distance.COSINE)
)

# 1. Função auxiliar para gerar um UUID estável a partir de uma string (Garante Idempotência)
def gerar_id_estavel(conteudo_texto: str) -> str:
    # Gera um hash MD5 padrão de 128 bits a partir do texto
    hash_objeto = hashlib.md5(conteudo_texto.encode('utf-8'))
    hex_digest = hash_objeto.hexdigest()
    
    # Formata no padrão UUIDv4 de hífens (8-4-4-4-12) exigido por bancos vetoriais
    return f"{hex_digest[:8]}-{hex_digest[8:12]}-{hex_digest[12:16]}-{hex_digest[16:20]}-{hex_digest[20:]}"

# 2. Dados brutos simulados vindo do seu pipeline de ingestão
chunks_para_salvar = [
    {"texto": "O endpoint /v1/auth gera tokens JWT com expiração de 15 minutos.", "modulo": "Segurança"},
    {"texto": "Para listar os produtos cadastrados, use o método GET na rota /v1/products.", "modulo": "Catálogo"}
]

# 3. Preparando os "Points" para inserção em lote (Upsert)
pontos_ingestao = []
for idx, item in enumerate(chunks_para_salvar):
    # Geramos o ID baseado no próprio texto do chunk
    id_idempotente = gerar_id_estavel(item["texto"])
    
    # Vetores de 3 dimensões simulados correspondentes aos textos
    vetor_simulado = [0.12, 0.78, -0.05] if idx == 0 else [-0.45, 0.12, 0.88]
    
    pontos_ingestao.append(
        PointStruct(
            id=id_idempotente,
            vector=vetor_simulado,
            # O Payload carrega os metadados estruturados que o RAG precisará ler
            payload={
                "texto_original": item["texto"],
                "categoria_modulo": item["modulo"],
                "ambiente": "producao"
            }
        )
    )

# 4. Executa a operação de UPSERT (Se o ID já existir, atualiza; se não, insere)
db_client.upsert(
    collection_name=NOME_COLECAO,
    wait=True, # Bloqueia a execução até que o índice seja sincronizado
    points=pontos_ingestao
)

print(f"[Upsert] {len(pontos_ingestao)} pontos processados de forma segura e idempotente.")

# Teste de Idempotência: Se contarmos os itens na coleção, deve haver exatamente 2, mesmo rodando o código de novo
info = db_client.get_collection(collection_name=NOME_COLECAO)
print(f"[Confirmação] Pontos totais reais no banco: {info.points_count}")