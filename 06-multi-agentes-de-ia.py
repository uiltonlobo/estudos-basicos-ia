import os
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- AGENTE 1: O Desenvolvedor ----
def agente_desenvolvedor(requisito: str) -> str:
    prompt_sistema = (
        "Você é um Engenheiro de Software Sênior especialista em Python. "
        "Escreva apenas o código limpo, sem explicações textuais antes ou depois. Use markdown."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Implemente o seguinte requisito: {requisito}"}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# ---- AGENTE 2: O Analista de QA (Quality Assurance) ----
def agente_qa(codigo_gerado: str) -> str:
    prompt_sistema = (
        "Você é um Engenheiro de QA especialista em testes unitários e segurança de código. "
        "Analise o código Python fornecido, aponte vulnerabilidades, bugs potenciais e sugira melhorias drásticas."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Avalie este código:\n\n{codigo_gerado}"}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

# ---- ORQUESTRADOR / PIPELINE COREOGRAFADO ----
if __name__ == "__main__":
    requisito_usuario = "Criar uma função que leia um arquivo de configuração e processe credenciais em string."

    print("=== PIPELINE DE AGENTES DE IA: DESENVOLVEDOR + QA ===\n")

    print(f"Requisito do Usuário:\n{requisito_usuario}\n")
    
    print("--- [PASSO 1]: Acionando Agente Desenvolvedor ---")
    codigo = agente_desenvolvedor(requisito_usuario)
    print(f"Output do Dev:\n{codigo}\n")
    
    print("--- [PASSO 2]: Passando Output para o Agente de QA ---")
    critica_qa = agente_qa(codigo)
    print(f"Relatório de Revisão do QA:\n{critica_qa}")