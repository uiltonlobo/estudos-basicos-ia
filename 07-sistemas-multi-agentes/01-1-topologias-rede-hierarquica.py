import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================================
# APEST - DEFINIÇÃO DOS AGENTES ESPECIALISTAS ATÔMICOS
# =====================================================================
def agente_banco_dados(ticket_usuario: str) -> str:
    print("   [DB-Agent] Processando requisição de dados...")
    prompt = f"Gere uma query SQL ou instrução técnica para resolver este problema: {ticket_usuario}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um DBA especialista em PostgreSQL. Escreva apenas código SQL ou instruções de banco, sem rodeios."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def agente_seguranca_iam(ticket_usuario: str) -> str:
    print("   [Security-Agent] Analisando regras de privilégios e acessos...")
    prompt = f"Avalie o impacto de segurança ou gere comandos AWS IAM para: {ticket_usuario}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um Engenheiro de SecOps especialista em AWS IAM e segurança de perímetros. Seja focado em governança."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# =====================================================================
# O ORQUESTRADOR CENTRAL (SUPERVISOR / ROUTER)
# =====================================================================
def supervisor_multi_agente(chamado_bruto: str):
    print(f"[Supervisor] Triando chamado do usuário: '{chamado_bruto}'")
    
    # Prompt do roteador para decidir o destino
    router_prompt = """
    Você é o Roteador/Supervisor Central de uma equipe de engenheiros de IA.
    Sua tarefa é analisar o ticket do usuário e decidir qual especialista deve tratar o problema.
    
    Especialistas disponíveis:
    - 'DBA': Se o problema envolver queries, tabelas, lentidão em banco ou dados.
    - 'SECURITY': Se o problema envolver permissões de acesso, chaves criptográficas ou bloqueios IAM.
    
    Retorne estritamente um JSON com a chave 'proximo_passo' contendo apenas o nome do especialista ('DBA' ou 'SECURITY').
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": router_prompt},
            {"role": "user", "content": chamado_bruto}
        ],
        temperature=0.0
    )
    
    decisao = json.loads(response.choices[0].message.content)
    proximo = decisao.get("proximo_passo")
    
    # Roteamento físico da tarefa baseado na inteligência do supervisor
    if proximo == "DBA":
        print("[Supervisor] ➔ Delegando tarefa para o Agente de Banco de Dados.")
        resultado_final = agente_banco_dados(chamado_bruto)
    elif proximo == "SECURITY":
        print("[Supervisor] ➔ Delegando tarefa para o Agente de Segurança.")
        resultado_final = agente_seguranca_iam(chamado_bruto)
    else:
        resultado_final = "Não consegui identificar um especialista adequado."
        
    return proximo, resultado_final

# --- EXECUÇÃO EM DOIS CENÁRIOS DISTINTOS ---

print("--- 🎫 CENÁRIO 1: Problema na Infra de Dados ---")
ticket_1 = "O microsserviço de vendas está dando timeout ao tentar buscar o relatório consolidado de clientes."
especialista, resposta_1 = supervisor_multi_agente(ticket_1)
print(f"\n[Resposta do Especialista ({especialista})]:\n{resposta_1}\n")

print("-" * 60 + "\n")

print("--- 🎫 CENÁRIO 2: Problema de Acesso ---")
ticket_2 = "O desenvolvedor novo precisa de acesso de leitura (Read-Only) no bucket S3 de logs da nuvem."
especialista, resposta_2 = supervisor_multi_agente(ticket_2)
print(f"\n[Resposta do Especialista ({especialista})]:\n{resposta_2}")