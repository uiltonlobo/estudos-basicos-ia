import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
# 1. FUNÇÃO REAL DO SEU BACKEND (O código determinístico)
def bloquear_usuario_no_banco(user_id: int, motivo: str) -> dict:
    """Simula uma query UPDATE no banco de dados SQL."""
    print(f"\n[BACKEND] Executando: UPDATE users SET status='BLOCKED' WHERE id={user_id};")
    return {
        "status": "success", 
        "message": f"Usuário {user_id} foi suspenso com sucesso por: '{motivo}'."
    }

# 2. DEFINIÇÃO DA FERRAMENTA (O Contrato que a IA vai ler)
ferramentas_sistema = [
    {
        "type": "function",
        "function": {
            "name": "bloquear_usuario_no_banco",
            "description": "Bloqueia e suspende o acesso de um usuário ao sistema devido a violações de termos ou segurança.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "O identificador numérico único do usuário no banco de dados."
                    },
                    "motivo": {
                        "type": "string",
                        "description": "A razão detalhada pela qual a conta está sendo bloqueada."
                    }
                },
                "required": ["user_id", "motivo"],
                "additionalProperties": False
            }
        }
    }
]

# 3. CHAMADA INICIAL: O usuário dá uma ordem imperativa
prompt_usuario = "O cliente ID 4829 está disparando ataques de spam. Suspenda a conta dele agora por abuso de API."

print("[Agente] Enviando comando e especificações de ferramentas para o LLM...")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt_usuario}],
    tools=ferramentas_sistema,
    tool_choice="auto" # O modelo decide de forma autônoma se usa ou não a ferramenta
)

mensagem_modelo = response.choices[0].message

# 4. TRATAMENTO DO RETORNO: A IA decidiu chamar a ferramenta?
if mensagem_modelo.tool_calls:
    chamada_ferramenta = messaging_modelo = mensagem_modelo.tool_calls[0]
    nome_funcao = chamada_ferramenta.function.name
    argumentos_ia = json.loads(chamada_ferramenta.function.arguments)
    
    print(f"\n[LLM Decisão]: Preciso chamar '{nome_funcao}' com os dados: {argumentos_ia}")
    
    # Roteamento dinâmico no seu código de backend
    if nome_funcao == "bloquear_usuario_no_banco":
        # Executamos o código Python real passando os dados que a IA extraiu
        resultado_execucao = bloquear_usuario_no_banco(
            user_id=argumentos_ia["user_id"],
            motivo=argumentos_ia["motivo"]
        )
        
        # 5. ENVIANDO O RESULTADO DE VOLTA PARA A IA
        print("[Agente] Devolvendo o resultado da API para consolidação do modelo...")
        resposta_final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt_usuario},
                mensagem_modelo, # Enviamos a mensagem de decisão do modelo (Obrigatório)
                {
                    "role": "tool",
                    "tool_call_id": chamada_ferramenta.id, # Vincula a resposta à chamada correta
                    "name": nome_funcao,
                    "content": json.dumps(resultado_execucao) # O resultado técnico da API
                }
            ]
        )
        
        print(f"\n[Assistente Resposta Final]:\n{resposta_final.choices[0].message.content}")
else:
    print(f"\n[Assistente Resposta Direta]:\n{mensagem_modelo.content}")