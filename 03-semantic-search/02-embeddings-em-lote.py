import os
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_embeddings_em_lote(chunks: list, batch_size: int = 32, dimensoes: int = 512) -> list:
    """
    Processa uma lista de strings em lotes (batching) e extrai embeddings 
    com dimensionalidade reduzida de forma nativa.
    """
    todos_os_vetores = []
    
    # 1. Divide a lista de chunks em pedaços de tamanho 'batch_size'
    for i in range(0, len(chunks), batch_size):
        lote_atual = chunks[i:i + batch_size]
        print(f"[ETL] Processando lote de {i} até {i + len(lote_atual)}...")
        
        try:
            # 2. Chamada única de rede para o lote inteiro
            response = client.embeddings.create(
                model="text-embedding-3-large", # Suporta Matryoshka Embeddings
                input=lote_atual,
                dimensions=dimensoes # Reduz o tamanho do vetor na própria API
            )
            
            # 3. Extrai os vetores da resposta na ordem exata de envio
            for objeto_embedding in response.data:
                todos_os_vetores.append(objeto_embedding.embedding)
                
        except Exception as e:
            print(f"[ERRO] Falha ao processar lote: {str(e)}")
            # Em produção, implemente aqui uma estratégia de Backoff Exponencial (Retry)
            raise e
            
    return todos_os_vetores

# --- SIMULAÇÃO EM LARGA ESCALA ---
# Imagine dezenas de chunks extraídos de um manual técnico
lista_de_chunks_extraidos = [
    "Configuração do banco de dados relacional PostgreSQL na AWS.",
    "Políticas de acesso e controle IAM para desenvolvedores juniores.",
    "Estratégia de cache de sessões usando Redis em cluster distribuído.",
    "Scripts de deploy automatizado via Terraform e Ansible no ambiente de staging.",
    "Monitoramento de latência e métricas de APM com Datadog e Prometheus.",
    "Configurações de segurança de rede utilizando Security Groups e instâncias de NAT Gateway."
]

# Executa o pipeline solicitando vetores otimizados de 512 floats (em vez de 3072)
vetores_finais = gerar_embeddings_em_lote(lista_de_chunks_extraidos, batch_size=3, dimensoes=512)

# Validação do formato de engenharia
print("\n=======================================================")
print(f"Total de vetores gerados: {len(vetores_finais)}")
print(f"Dimensões do primeiro vetor: {len(vetores_finais[0])} dimensões (Floats)")
print(f"Amostra dos 5 primeiros valores do vetor: {vetores_finais[0][:5]}")
print("=======================================================")