import math

def dot_product(v1, v2):
    """Calcula o produto escalar entre dois vetores."""
    return sum(x * y for x, y in zip(v1, v2))

def magnitude(v):
    """Calcula a magnitude (comprimento) de um vetor."""
    return math.sqrt(sum(x ** 2 for x in v))

def cosine_similarity(v1, v2):
    """Calcula a similaridade de cosseno (De -1.0 a 1.0)."""
    m1 = magnitude(v1)
    m2 = magnitude(v2)
    if m1 == 0 or m2 == 0:
        return 0.0
    return dot_product(v1, v2) / (m1 * m2)

# --- SIMULAÇÃO DE VETORES DE PRODUÇÃO ---
# Para fins didáticos, simularemos vetores de apenas 3 dimensões (X, Y, Z)
# Em produção, esses vetores teriam centenas ou milhares de dimensões.

vetor_query = [0.12, 0.85, -0.05] # Vetor da pergunta: "Como resetar minha senha corporativa?"

# Chunks recuperados do banco vetorial
chunks_banco = [
    {"id": 101, "texto": "Para alterar sua credencial, vá no menu de configurações de segurança.", "vetor": [0.11, 0.82, -0.03]},
    {"id": 102, "texto": "A infraestrutura corporativa é composta por servidores Linux Ubuntu.", "vetor": [0.75, -0.12, 0.44]},
    {"id": 103, "texto": "Se esqueceu a senha, clique em 'esqueci minha senha' na tela de login.", "vetor": [0.09, 0.79, -0.09]}
]

# 1. FASE DE RECUPERAÇÃO: Calculando a similaridade linearmente (Varredura de Banco)
resultados_busca = []
for chunk in chunks_banco:
    score = cosine_similarity(vetor_query, chunk["vetor"])
    resultados_busca.append({
        "id": chunk["id"],
        "texto": chunk["texto"],
        "score_vetorial": score
    })

# Ordena pelo score vetorial do maior para o menor
resultados_busca.sort(key=lambda x: x["score_vetorial"], reverse=True)

print("--- [Fase 1]: Resultados do Banco Vetorial (Bi-Encoder) ---")
for r in resultados_busca:
    print(f"ID: {r['id']} | Score Vetorial: {r['score_vetorial']:.4f} | Texto: {r['texto']}")

# 2. FASE DE RE-RANKING (Simulação de Cross-Encoder de Produção)
# O Re-ranker analisa detalhes gramaticais profundos que o vetor puro deixou passar.
# Ele percebe que o ID 103 fala explicitamente sobre "esquecer a senha", mais próximo da query "resetar".
print("\n--- [Fase 2]: Aplicando Re-ranking Inteligente (Cross-Encoder) ---")

# Simulando o ajuste fino de notas do modelo de re-ranker
scores_rerank_proprietarios = {101: 0.62, 102: 0.01, 103: 0.95}

for r in resultados_busca:
    r["score_final"] = scores_rerank_proprietarios[r["id"]]

# Re-ordena a lista com base no novo critério cognitivo profundo
resultados_busca.sort(key=lambda x: x["score_final"], reverse=True)

for r in resultados_busca:
    print(f"ID: {r['id']} | Score Final: {r['score_final']:.4f} | Texto: {r['texto']}")