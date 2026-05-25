import tiktoken

def recursive_token_chunker(text: str, model_name: str = "gpt-4o", chunk_size: int = 100, chunk_overlap: int = 20):
    """
    Fatia um texto baseado em contagem real de TOKENS (não caracteres),
    garantindo compatibilidade exata com as janelas de contexto dos modelos.
    """
    # 1. Inicializa o tokenizador do modelo específico
    tokenizer = tiktoken.encoding_for_model(model_name)
    
    # 2. Transforma o texto bruto em uma lista de IDs de tokens (inteiros)
    tokens = tokenizer.encode(text)
    total_tokens = len(tokens)
    
    chunks = []
    start = 0
    
    # 3. Sliding Window (Janela deslizante) aplicando o Overlap
    while start < total_tokens:
        end = min(start + chunk_size, total_tokens)
        chunk_tokens = tokens[start:end]
        
        # Decodifica os tokens de volta para string legível
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append({
            "text": chunk_text,
            "token_count": len(chunk_tokens),
            "bounds": (start, end)
        })
        
        # Move o ponteiro inicial subtraindo a sobreposição para manter o contexto conectado
        start += (chunk_size - chunk_overlap)
        
        # Break de segurança para evitar loops infinitos caso o overlap seja maior que o chunk
        if start >= total_tokens or chunk_size <= chunk_overlap:
            break
            
    return chunks

# --- SIMULAÇÃO COM DOCUMENTAÇÃO TÉCNICA ---
documento_infra = """
ARQUITETURA DE REDE CORPORATIVA:
O cluster principal Kubernetes roda na subnet privada 10.0.1.0/24 dentro da VPC de Produção.
Todos os pods de microsserviços utilizam instâncias EC2 com criptografia EBS nativa habilitada.
A comunicação externa é estritamente realizada via AWS Internet Gateway blindado por regras de WAF.
LOGS E AUDITORIA:
Qualquer tentativa de acesso não autorizado na porta 22 (SSH) dispara um alarme no AWS CloudWatch.
O time de SecOps recebe um payload via webhook no Slack em menos de 15 segundos para triagem automática.
"""

# Executa o chunking limitando a blocos pequenos de 40 tokens para fins didáticos
chunks_processados = recursive_token_chunker(documento_infra, chunk_size=40, chunk_overlap=10)

print(f"Texto original fatiado em {len(chunks_processados)} blocos coerentes:\n")
for idx, chunk in enumerate(chunks_processados):
    print(f"--- CHUNK {idx+1} ({chunk['token_count']} tokens) | IDs: {chunk['bounds']} ---")
    print(chunk['text'].strip())