import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- FERRAMENTAS MOCKADAS DE INFRAESTRUTURA ---
def checar_status_servidor(hostname: str) -> dict:
    print(f"   [API Executada] checar_status_servidor para '{hostname}'")
    if hostname == "prod-db-01":
        return {"status": "DOWN", "error": "Out of Memory (OOM)"}
    return {"status": "UP", "error": None}

def reiniciar_instancia_infra(hostname: str) -> dict:
    print(f"   [API Executada] reiniciar_instancia_infra para '{hostname}'")
    return {"status": "SUCCESS", "message": f"Instância {hostname} reiniciada com sucesso."}

# Esquema de ferramentas que a IA vai ler
spec_ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "checar_status_servidor",
            "description": "Verifica a saúde e status atual de um servidor na nuvem.",
            "parameters": {
                "type": "object",
                "properties": {"hostname": {"type": "string"}},
                "required": ["hostname"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reiniciar_instancia_infra",
            "description": "Força o reboot físico/lógico de um servidor instável.",
            "parameters": {
                "type": "object",
                "properties": {"hostname": {"type": "string"}},
                "required": ["hostname"],
                "additionalProperties": False
            }
        }
    }
]

# --- O MOTOR DE LOOP REACT (ORQUESTRADOR AMBIENTAL) ---
def rodar_agente_react(comando_usuario: str):
    print(f"[Agente] Iniciando Loop ReAct para o comando: '{comando_usuario}'")
    
    # Inicializa o histórico de estado que o agente acumulará a cada iteração
    historico_mensagens = [
        {
            "role": "system", 
            "content": "Você é um orquestrador de DevOps. Pense passo a passo (Thought) antes de tomar qualquer ação."
        },
        {"role": "user", "content": comando_usuario}
    ]
    
    MAX_ITERATION = 4 # Barreira mecânica de segurança contra loops infinitos
    
    for iteracao in range(1, MAX_ITERATION + 1):
        print(f"\n--- 🔄 ITERAÇÃO REACT #{iteracao} ---")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=historico_mensagens,
            tools=spec_ferramentas,
            temperature=0.0
        )
        
        mensagem_ia = response.choices[0].message
        historico_mensagens.append(mensagem_ia) # Persiste a decisão da IA no histórico
        
        # Condição de Parada 1: A IA não quis chamar ferramentas, ela decidiu dar a resposta final
        if not mensagem_ia.tool_calls:
            print("[Agente] Objetivo atingido. Gerando resposta final para o usuário.")
            return mensagem_ia.content
            
        # Tratamento das Ações (Function Calling)
        for chamada in mensagem_ia.tool_calls:
            nome_func = chamada.function.name
            args = json.loads(chamada.function.arguments)
            
            print(f"[Thought/Action]: Decidi invocar '{nome_func}' com os parâmetros {args}")
            
            # Roteamento e execução das APIs locais
            if nome_func == "checar_status_servidor":
                observacao_resultado = checar_status_servidor(hostname=args["hostname"])
            elif nome_func == "reiniciar_instancia_infra":
                observacao_resultado = reiniciar_instancia_infra(hostname=args["hostname"])
            else:
                observacao_resultado = {"error": "Função desconhecida."}
                
            print(f"[Observation]: Resultado obtido da API: {observacao_resultado}")
            
            # Alimenta o histórico com o resultado da ação para a próxima iteração
            historico_mensagens.append({
                "role": "tool",
                "tool_call_id": chamada.id,
                "name": nome_func,
                "content": json.dumps(observacao_resultado)
            })
            
    print("[Erro Infra] O agente estourou o limite máximo de iterações de segurança.")
    return "Não consegui concluir a tarefa devido a um limite de passos no sistema."

# --- DISPARANDO O AGENTE ---
comando_devops = "Verifique o servidor 'prod-db-01'. Se ele estiver fora do ar, aplique o reboot imediatamente."
resposta_sistema = rodar_agente_react(comando_devops)

print(f"\n=======================================================")
print(f"📩 OUTPUT FINAL EXIBIDO NO TERMINAL:\n{resposta_sistema}")
print("=======================================================")