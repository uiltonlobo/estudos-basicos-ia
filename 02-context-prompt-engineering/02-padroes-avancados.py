import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SYSTEM PROMPT: Combinando Few-Shot com Chain-of-Thought
system_instruction = """
Você é um motor de subscrição automatizado para seguros de responsabilidade civil tecnológica (Tech E&O).
Seu objetivo é analisar a stack de desenvolvimento enviada pelo usuário e calcular o 'fator_risco' (de 1.0 a 5.0) e o 'status_aprovacao'.

Siga a lógica de análise passo a passo (Chain-of-Thought):
1. Avalie as linguagens e categorize quanto à segurança de memória e concorrência.
2. Identifique se há dependências críticas ou legadas.
3. Calcule a média de risco e determine a aprovação.

EXEMPLO DE ENTRADA E SAÍDA (Few-Shot):

User Input: 'Stack: C++, PHP antigo sem framework, hospedado em servidor local IIS.'

Output Esperado:
{
    "analise_passo_a_passo": "1. C++ possui alto risco de gerenciamento de memória (buffer overflow). PHP legado sem framework indica superfície de ataque alta por falta de sanitização nativa. Servidor local IIS fora de ambiente cloud indica provável falta de patches automáticos. 2. Dependências altamente críticas encontradas (PHP antigo). 3. Score ponderado alto devido à vulnerabilidade estrutural.",
    "fator_risco": 4.8,
    "status_aprovacao": "REJEITADO"
}

Retorne SEMPRE um JSON válido.
"""

# Input dinâmico que o sistema vai avaliar
### input_usuario = "Stack: C# (.NET 8), Go (serviços de alta concorrência), PostgreSQL gerenciado na AWS RDS, CI/CD ativo no GitHub Actions."
### input_usuario = "Stack: Java (camada de regras de negócio), Python (serviços com agentes de IA), PostgreSQL gerenciado na AWS RDS, CI/CD ativo no Azure DevOps."
### input_usuario = "Stack: Clojure e Ruby (camada de regras de negócio), Python (serviços com agentes de IA), Oracle gerenciado na AWS RDS, CI/CD com Jenkins."
input_usuario = "Stack: C (CGI), Cobol, Oracle on Premises, Deploy com FileZilla."

response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},    # Obs.: Força o modelo a retornar um JSON nativo, evitando erros de parsing
    messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": input_usuario}
    ],
    temperature=0.1
)

output = json.loads(response.choices[0].message.content)
print(json.dumps(output, indent=4, ensure_ascii=False))