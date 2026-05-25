import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
# CONTEXT ENGINEERING: Estruturando o ambiente de execução da IA
system_instruction = """
ROLE: Você é um parser de segurança de backend especializado em análise forense de logs de infraestrutura AWS.

OBJECTIVE: Extrair dados de strings brutas de log e convertê-los em um objeto JSON estruturado para indexação.

CONSTRAINTS (Restrições Rígidas):
- Identifique apenas IPs públicos. Ignore IPs de rede interna (ex: 10.x.x.x ou 192.168.x.x).
- Se o log não contiver uma falha clara, defina o campo 'severity' como 'INFO'.
- Não adicione textos explicativos, saudações ou markdown (como ```json) no output. A saída deve ser APENAS o JSON puro.

OUTPUT FORMAT:
Retorne estritamente o seguinte schema JSON:
{
    "timestamp": "ISO8601 string ou null",
    "source_ip": "string ou null",
    "event_type": "AUTH_FAIL | DATABASE_TIMEOUT | UNKNOWN",
    "severity": "CRITICAL | WARN | INFO",
    "system_msg": "Resumo limpo do erro em uma frase curta"
}
"""

# Payload dinâmico que viria de um arquivo de log (User Input)
log_bruto_usuario = "syslog: [2026-05-24T14:32:01Z] 10.0.1.55 - inbound_auth - connection rejected from blocked public IP 185.220.101.4 por tentativas excessivas."

# Execução do pipeline
response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"}, # Força o modo JSON nativo na API
    messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": log_bruto_usuario}
    ],
    temperature=0.0 # Determinismo máximo: queremos um parser, não um poeta
)

# Validação do output no backend do seu software
output_final = json.loads(response.choices[0].message.content)
print(json.dumps(output_final, indent=4, ensure_ascii=False))