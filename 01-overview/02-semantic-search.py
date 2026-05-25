import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str, model="text-embedding-3-small"):
    # Garante a remoção de quebras de linha para evitar ruído no modelo
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def cosine_similarity(v1, v2):
    # Cálculo manual da similaridade de cosseno usando álgebra linear básica
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Nosso "banco de dados" conceitual de logs do sistema
base_conhecimento = [
    "Erro crítico: Conexão com o banco de dados SQL expirou.",
    "A interface do usuário quebrou ao clicar no botão de salvar.",
    "Nova atualização de segurança aplicada no servidor de produção."
]

# Gerando os embeddings da base
embeddings_base = [get_embedding(texto) for texto in base_conhecimento]

# Input de busca do usuário (com palavras totalmente diferentes da base)
query = "O sistema falhou ao tentar conectar no banco"
embedding_query = get_embedding(query)

# Calculando a similaridade com cada item da base
print(f"Query: '{query}'\n")
for texto, emb_base in zip(base_conhecimento, embeddings_base):
    sim = cosine_similarity(embedding_query, emb_base)
    print(f"-> Similaridade: {sim:.4f} | Texto: '{texto}'")