import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def expandir_query_usuario(pergunta_original: str) -> list:
    """
    Usa um LLM para quebrar uma pergunta vaga em múltiplas queries técnicas correlacionadas.
    Isso otimiza a busca semântica cobrindo diferentes sinônimos textuais.
    """
    print(f"[Avançado] 1. Recebendo query original: '{pergunta_original}'")
    
    system_instruction = """
ROLE: Você é um otimizador de consultas para motores de busca vetorial corporativos.
OBJECTIVE: Sua tarefa é receber uma pergunta de um funcionário e gerar exatamente 3 variações dessa pergunta.

CONSTRAINTS:
- Use sinônimos técnicos e termos alternativos comuns no ambiente corporativo (ex: mudar 'grana' para 'reembolso', 'PLR' ou 'salário').
- Foque em capturar a real intenção de busca do usuário sob diferentes perspectivas de escrita.
- Retorne estritamente um array JSON de strings, sem formatação markdown ou explicações.

OUTPUT FORMAT:
["variacao 1", "variacao 2", "variacao 3"]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Gere variações para: {pergunta_original}"}
        ],
        temperature=0.2 # Baixa temperatura para manter o foco técnico
    )
    
    # Converte o JSON de retorno para Python e normaliza para lista.
    # Quando o modelo responde como objeto JSON, transformamos seus valores em lista.
    resposta_parseada = json.loads(response.choices[0].message.content)
    queries_expandidas = list(resposta_parseada.values()) if isinstance(resposta_parseada, dict) else resposta_parseada
    
    # Garantimos que a query original também faça parte da busca
    if isinstance(queries_expandidas, list):
        return [pergunta_original] + queries_expandidas
    else:
        # Fallback de segurança caso o modelo falhe no formato do array
        return [pergunta_original]

# --- SIMULAÇÃO DO PIPELINE DE ENTRADA ---
pergunta_vaga = "Como eu faço pra pegar a grana da consulta de volta?"

lista_de_buscas = expandir_query_usuario(pergunta_vaga)

print("\n=======================================================")
print("🚀 VETOR DE ENTRADA EXPANDIDO PARA O BANCO VETORIAL:")
print("=======================================================\n")
for idx, query in enumerate(lista_de_buscas):
    print(f"Query #{idx} (Enviada para Embedding): '{query}'")
print("\n=======================================================")