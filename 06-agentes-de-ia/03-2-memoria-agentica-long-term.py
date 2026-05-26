import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================================
# 1. INFRAESTRUTURA DE PERSISTÊNCIA (Simulando o Banco de Dados da Empresa)
# =====================================================================
class MockDatabase:
    def __init__(self):
        # Tabela fictícia no SQL: 'user_long_term_memories'
        self.tabela_memorias = {}

    def salvar_fato_usuario(self, user_id: int, chave: str, fato: str):
        if user_id not in self.tabela_memorias:
            self.tabela_memorias[user_id] = {}
        self.tabela_memorias[user_id][chave] = fato
        print(f"   [DB WRITE] Gravado para Usuário {user_id} -> {chave.upper()}: '{fato}'")

    def recuperar_fatos_usuario(self, user_id: int) -> dict:
        return self.tabela_memorias.get(user_id, {})

# Inicializa o banco de dados global da aplicação
banco_de_dados = MockDatabase()


# =====================================================================
# 2. DEFINIÇÃO DA FERRAMENTA DE MEMÓRIA (Function Calling)
# =====================================================================
ferramenta_memoria = [
    {
        "type": "function",
        "function": {
            "name": "gravar_fato_importante_no_perfil",
            "description": "Salva uma preferência, configuração ou fato imutável sobre o usuário no banco de dados de longo prazo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chave_config": {
                        "type": "string",
                        "description": "A categoria do fato. Exemplos: 'linguagem_preferida', 'sistema_operacional', 'fuso_horario'."
                    },
                    "descricao_fato": {
                        "type": "string",
                        "description": "O fato extraído textualmente da fala do usuário de forma concisa."
                    }
                },
                "required": ["chave_config", "descricao_fato"],
                "additionalProperties": False
            }
        }
    }
]


# =====================================================================
# 3. ORQUESTRADOR DO AGENTE COM LONG-TERM MEMORY
# =====================================================================
def rodar_agente_com_historico(user_id: int, mensagem_atual: str):
    # PASSO A: BOOTSTRAP - Recupera tudo o que o banco de dados sabe sobre esse usuário do passado
    fatos_passados = banco_de_dados.recuperar_fatos_usuario(user_id)
    
    # Injeta os fatos recuperados do disco diretamente no System Prompt
    system_instruction = (
        "Você é um assistente de programação sênior.\n"
        f"PERFIL DO USUÁRIO RECUPERADO DO BANCO DE DISCO: {json.dumps(fatos_passados)}\n\n"
        "INSTRUÇÃO: Responda de acordo com as preferências históricas do usuário. "
        "Se o usuário mencionar um novo fato importante (como a linguagem que usa ou o OS), "
        "use a ferramenta de gravação para salvar na memória de longo prazo."
    )
    
    mensagens = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": mensagem_atual}
    ]
    
    # Chamada ao modelo com suporte a ferramentas
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensagens,
        tools=ferramenta_memoria,
        temperature=0.0
    )
    
    mensagem_ia = response.choices[0].message
    
    # PASSO B: Intercepta se a IA decidiu gravar um novo fato na memória de longo prazo
    if mensagem_ia.tool_calls:
        chamada = mensagem_ia.tool_calls[0]
        args = json.loads(chamada.function.arguments)
        
        # Executa a escrita física no banco de dados
        banco_de_dados.salvar_fato_usuario(
            user_id=user_id,
            chave=args["chave_config"],
            fato=args["descricao_fato"]
        )
        return f"[Agente processou a informação e salvou no seu perfil de longo prazo: {args['chave_config']} = {args['descricao_fato']}]"
        
    return mensagem_ia.content


# =====================================================================
# 4. SIMULAÇÃO DAS SESSÕES DE ACESSO (O Teste de Engenharia)
# =====================================================================

print("--- 🗓️ SESSÃO 1: Segunda-feira (Primeiro contato do usuário) ---")
# O usuário inicia um chat limpo e se apresenta
resposta_sessao_1 = rodar_agente_com_historico(
    user_id=99, 
    mensagem_atual="Olá! Estou começando um projeto novo de APIs e vou desenvolver tudo usando a linguagem Go (Golang)."
)
print(f"Resposta: {resposta_sessao_1}\n")


print("--- 🗓️ SESSÃO 2: Sexta-feira (Nova conexão, memória de curto prazo ZERADA) ---")
# O array 'messages' do python foi apagado, o servidor reiniciou, mas o banco de dados guardou o fato.
# O usuário faz uma pergunta vaga sem dizer qual linguagem está usando.
resposta_sessao_2 = rodar_agente_com_historico(
    user_id=99, 
    mensagem_atual="Preciso criar um script rápido para ler um arquivo JSON e printar no console. Como faço?"
)
print(f"\nResposta da IA customizada para o perfil do usuário:\n{resposta_sessao_2}")