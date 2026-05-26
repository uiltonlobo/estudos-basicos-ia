import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
def avaliar_groundedness(contexto_recuperado: str, resposta_gerada: str) -> dict:
    """
    Atua como um juiz (LLM-as-a-Judge) para verificar se a resposta gerada
    está estritamente ancorada no contexto fornecido, identificando alucinações.
    """
    
    judge_prompt = """
ROLE: Você é um auditor de sistemas de IA encarregado de controle de qualidade e prevenção de alucinações.

OBJECTIVE: Avaliar se a 'RESPOSTA GERADA' está 100% contida e suportada pelo 'CONTEXTO FORNECIDO'.

CRITÉRIOS DE NOTA (Score de 1 a 5):
5 - Perfeito: Cada afirmação na resposta está diretamente escrita no contexto.
3 - Parcial: A resposta é verdadeira em parte, mas assume ou extrapola pequenos detalhes não ditos.
1 - Alucinação Grave: A resposta contém dados, valores, regras ou afirmações que NÃO existem no contexto.

OUTPUT FORMAT:
Retorne estritamente um objeto JSON com o seguinte schema:
{
    "score": int,
    "justificativa_tecnica": "string explicando a quebra de fidelidade se houver"
}
"""

    payload_avaliacao = f"""
CONTEXTO FORNECIDO:
"{contexto_recuperado}"

RESPOSTA GERADA:
"{resposta_gerada}"
"""

    response = client.chat.completions.create(
        model="gpt-4o", # Modelos mais fortes são exigidos para atuar como juízes
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": judge_prompt},
            {"role": "user", "content": payload_avaliacao}
        ],
        temperature=0.0 # Juízes precisam ser totalmente deterministas
    )
    
    return json.loads(response.choices[0].message.content)

# --- SIMULAÇÃO DE UMA FALHA/ALUCINAÇÃO EM PRODUÇÃO ---

contexto_real_banco = "O plano de saúde cobre cirurgias refrativas apenas para pacientes com mais de 7 graus de miopia."
resposta_alucinada_da_ia = "Sim, o plano cobre a sua cirurgia refrativa. O agendamento pode ser feito direto pelo WhatsApp da Central de Benefícios pelo número 0800-123-456."

# Execução da auditoria automática
resultado_auditoria = avaliar_groundedness(contexto_real_banco, resposta_alucinada_da_ia)

print("=======================================================")
print("📊 RELATÓRIO DE AUDITORIA AUTOMÁTICA DE RAG (CI/CD):")
print("=======================================================\n")
print(f"SCORE DE FIDELIDADE: {resultado_auditoria['score']}/5")
print(f"ANÁLISE DO JUIZ: {resultado_auditoria['justificativa_tecnica']}")
print("\n=======================================================")