import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. Ferramenta analítica definida no seu sistema tradicional (Simulação de um Microserviço)
def obter_faturamento_cliente(id_cliente: str) -> str:
    # Em produção, consultaria o banco relacional
    if id_cliente == "CLI-99":
        return json.dumps({"cliente": "CLI-99", "status": "Inadimplente", "valor_devido": 25000.00})
    return json.dumps({"cliente": id_cliente, "status": "Regular", "valor_devido": 0.0})

# 2. Schema de definição da ferramenta (Fornecido ao LLM para ele mapear os parâmetros)
tools_definitions = [
    {
        "type": "function",
        "function": {
            "name": "obter_faturamento_cliente",
            "description": "Consulta o faturamento e o status financeiro de um cliente específico no banco.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_cliente": {"type": "string", "description": "O ID identificador do cliente, ex: CLI-99"}
                },
                "required": ["id_cliente"]
            }
        }
    }
]

# 3. Execução do Loop
prompt_usuario = "O cliente CLI-99 solicitou liberação de crédito. Podemos autorizar?"

# Primeira chamada ao LLM (Enviando a intenção e as ferramentas disponíveis)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt_usuario}],
    tools=tools_definitions,
    tool_choice="auto" # O LLM decide se precisa usar ou não
)

message = response.choices[0].message

# Verificação de Controle de Fluxo: O modelo decidiu chamar a ferramenta?
if message.tool_calls:
    print(f"[Pensamento do Agente]: Preciso checar as ferramentas de faturamento.")
    tool_call = message.tool_calls[0]
    nome_funcao = tool_call.function.name
    argumentos = json.loads(tool_call.function.arguments)
    
    print(f"[Ação do Agente]: Invocando a função nativa '{nome_funcao}' com parâmetros {argumentos}")
    
    # Roteamento dinâmico da execução da função no backend
    if nome_funcao == "obter_faturamento_cliente":
        resultado_ferramenta = obter_faturamento_cliente(id_cliente=argumentos.get("id_cliente"))
        
    print(f"[Observação do Sistema]: Retorno da Ferramenta -> {resultado_ferramenta}")
    
    # Segunda chamada ao LLM (Enviando o resultado da execução técnica para consolidação)
    resposta_final = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt_usuario},
            message, # Inclui a mensagem anterior do assistente com o tool_call
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": nome_funcao,
                "content": resultado_ferramenta
            }
        ]
    )
    
    print(f"\n[Resposta Final Consolidada para o Usuário]:\n{resposta_final.choices[0].message.content}")