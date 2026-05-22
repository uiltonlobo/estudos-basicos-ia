import os
import json
from dotenv import load_dotenv
from openai import OpenAI
    
# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicialização padrão do client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Definindo o prompt do sistema (System Prompt / Role) e o contexto
system_instruction = (
    "Você é um microsserviço de backend especializado em análise de sentimento de logs de suporte. "
    "Sua saída deve ser estritamente em formato JSON válido, contendo as chaves: 'status', 'score' (-1 a 1) e 'justificativa_passo_a_passo'."
)

# Exemplos para o modelo (Few-Shot) + Indução de raciocínio (Chain-of-Thought)
user_payload = """
Analise o seguinte log de suporte:
'O sistema caiu novamente no meio da homologação. Já é a terceira vez esta semana. Preciso disso resolvido até as 14h ou perderemos o prazo com o cliente.'
"""

response = client.chat.completions.create(
    model="gpt-4o-mini", # Modelo rápido e ideal para tarefas estruturadas
    response_format={ "type": "json_object" }, # Garante JSON válido a nível de API
    messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_payload}
    ],
    temperature=0.1 # Baixa temperatura = maior determinismo (ideal para devs)
)

# Parse do output
resultado = json.loads(response.choices[0].message.content)
print(json.dumps(resultado, indent=4, ensure_ascii=False))