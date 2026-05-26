import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# 1. Inicialização dos Clientes Globais de Infraestrutura
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
vector_db = QdrantClient(":memory:")

NOME_COLECAO = "politicas_rh_empresa"
MODELO_EMBEDDING = "text-embedding-3-small"
DIMENSOES = 512

# 2. Setup do Banco Vetorial e Ingestão de Dados (Simulando nossa base de conhecimento de RH)
vector_db.create_collection(
    collection_name=NOME_COLECAO,
    vectors_config=VectorParams(size=DIMENSOES, distance=Distance.COSINE)
)

documentos_privados_rh = [
    "A política de home office permite até 3 dias de trabalho remoto por semana, necessitando aprovação do gestor direto até sexta-feira anterior.",
    "O plano de saúde corporativo Bradesco Top Premium dá direito a reembolso de consultas médicas particulares em até R$ 150,00 por recibo enviado.",
    "O bônus anual de performance (PLR) é pago sempre no segundo dia útil do mês de Março, baseado nas metas batidas no ano fiscal anterior."
]

# Helper para gerar embeddings rapidamente
def obter_embedding(texto: str) -> list:
    resp = openai_client.embeddings.create(model=MODELO_EMBEDDING, input=[texto], dimensions=DIMENSOES)
    return resp.data[0].embedding

# Ingestão inicial dos dados no banco vetorial
pontos = [
    PointStruct(id=idx, vector=obter_embedding(txt), payload={"texto": txt})
    for idx, txt in enumerate(documentos_privados_rh)
]
vector_db.upsert(collection_name=NOME_COLECAO, points=pontos)
print("[Infra] Banco Vetorial populado com dados privados de RH!\n")


# =====================================================================
# 3. O PIPELINE RAG (O Core do seu Serviço de IA)
# =====================================================================
def executar_pipeline_rag(pergunta_usuario: str) -> str:
    print(f"[RAG] 1. Interceptando a pergunta: '{pergunta_usuario}'")
    
    # Passo A: Vetorizar a pergunta do usuário em tempo real
    vetor_query = obter_embedding(pergunta_usuario)
    
    # Passo B: Recuperar (Retrieve) os 2 chunks mais parecidos do banco vetorial
    resposta = vector_db.query_points(
        collection_name=NOME_COLECAO,
        query=vetor_query,
        limit=2
    )

    resultados_banco = resposta.points
    
    # Extrai o texto dos payloads recuperados
    contextos_recuperados = [match.payload["texto"] for match in resultados_banco]
    print(f"[RAG] 2. Chunks recuperados do banco vetorial: {len(contextos_recuperados)} trechos encontrados.")
    
    # Passo C: Aumentar (Augment) o Prompt injetando os contextos recuperados como dependência
    contexto_formatado = "\n".join([f"- {txt}" for txt in contextos_recuperados])
    
    system_prompt = f"""
ROLE: Você é um assistente virtual de RH corporativo rigoroso e preciso.
OBJECTIVE: Responda à pergunta do usuário utilizando estritamente as informações fornecidas no bloco CONTEXTO abaixo.

CONTEXTO RECUPERADO DO BANCO DE DADOS:
{contexto_formatado}

CONSTRAINTS (Restrições Rígidas):
- Se a resposta não puder ser encontrada explicitamente no CONTEXTO acima, responda exatamente: 'Desculpe, mas não possuo essa informação na minha base de conhecimento de RH.'
- Não invente dados, datas, valores ou regras que não estejam escritos textualmente no contexto.
"""

    # Passo D: Gerar (Generate) a resposta final usando o modelo de chat
    print("[RAG] 3. Enviando contexto enriquecido para a OpenAI...")
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pergunta_usuario}
        ],
        temperature=0.0 # Determinismo máximo para evitar desvios das regras de RH
    )
    
    return response.choices[0].message.content

# --- TESTANDO O PIPELINE COM DUAS PERGUNTAS ---

# Cenário 1: Pergunta com dado existente no banco
pergunta_valida = "Quantos dias posso trabalhar de casa e qual o prazo para o gestor aprovar?"
resposta_1 = executar_pipeline_rag(pergunta_valida)
print(f"\n[Assistente]: {resposta_1}\n")
print("-" * 60 + "\n")

# Cenário 2: Pergunta sobre algo que NÃO existe no banco (Testando a barreira contra alucinação)
pergunta_invalida = "A empresa paga auxílio creche para quem tem filhos pequenos?"
resposta_2 = executar_pipeline_rag(pergunta_invalida)
print(f"\n[Assistente]: {resposta_2}\n")