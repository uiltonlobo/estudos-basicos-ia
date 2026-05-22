import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# 1. Setup dos clientes
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./meu_chroma_db")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)

# Criando a coleção de políticas internas
collection = chroma_client.get_or_create_collection("politicas_internas", embedding_function=openai_ef)

# 2. Simulando o provisionamento/população do banco (Dados privados da empresa)
documentos_corporativos = [
    "Política de Home Office: Desenvolvedores seniores podem trabalhar 100% remoto. O reembolso de internet é de até R$ 150 mensais.",
    "Política de Benefícios: O plano de saúde corporativo cobre dependentes diretos (cônjuge e filhos) com coparticipação de 20%.",
    "Segurança da Informação: É estritamente proibido subir chaves de API privadas em repositórios públicos do GitHub."
]
collection.upsert(
    documents=documentos_corporativos,
    ids=["doc_ho_01", "doc_ben_01", "doc_seg_01"]
)

# 3. A pergunta do usuário
pergunta_usuario = "Sou dev sênior, posso trabalhar de casa? Tem algum auxílio para custos?"

# 4. Etapa de Recuperação (Retrieval)
busca_vetorial = collection.query(query_texts=[pergunta_usuario], n_results=1)
contexto_recuperado = busca_vetorial['documents'][0][0]

# 5. Etapa de Geração (Augmented Generation)
prompt_sistema = (
    "Você é um assistente virtual do departamento de Recursos Humanos.\n"
    "Responda à pergunta do usuário utilizando ESTRITAMENTE o contexto fornecido abaixo. "
    "Se a resposta não puder ser encontrada no contexto, diga honestamente 'Não possuo essa informação em minha base'.\n\n"
    f"CONTEXTO RECUPERADO:\n{contexto_recuperado}"
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": pergunta_usuario}
    ],
    temperature=0.0 # Queremos precisão factual máxima
)

print(f"Pergunta: {pergunta_usuario}\n")
print(f"Resposta Gerada:\n{response.choices[0].message.content}")