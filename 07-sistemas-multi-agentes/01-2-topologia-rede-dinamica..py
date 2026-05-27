import os
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================================
# 1. MOTOR DE EXECUÇÃO DE PEER-TO-PEER (O Contexto Compartilhado)
# =====================================================================
def executar_agente_na_mesa(nome_agente: str, persona_prompt: str, historico_compartilhado: list) -> list:
    """
    Roda um agente específico dando a ele acesso a TODA a conversa dos colegas anteriores.
    Ele adicionará sua contribuição na mesa redonda.
    """
    print(f"\n[Mesa Redonda] 🎙️ {nome_agente} assume a palavra...")
    
    # Injeta a persona do agente atual como a diretiva do sistema
    contexto_chamada = [
        {"role": "system", "content": persona_prompt}
    ] + historico_compartilhado # Concatena o histórico completo da mesa até aqui
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=contexto_chamada,
        temperature=0.4 # Temperatura moderada para permitir criatividade e complementação
    )
    
    resposta_texto = response.choices[0].message.content
    print(f"\n[{nome_agente}]: {resposta_texto}\n" + "-"*50)
    
    # Adiciona a resposta ao histórico para que o PRÓXIMO agente da mesa possa ler
    historico_compartilhado.append({"role": "assistant", "name": nome_agente, "content": resposta_texto})
    return historico_compartilhado


# =====================================================================
# 2. DEFINIÇÃO DAS PERSONAS TÉCNICAS (Prompts de Especialistas)
# =====================================================================
PROMPT_PROGRAMADOR = """
Você é o 'Dev_Junior'. Sua tarefa é receber o pedido de uma funcionalidade do usuário e escrever o código inicial em Python de forma simples e direta, sem se preocupar demais com otimizações extremas.
"""

PROMPT_PERFORMANCE = """
Você é o 'Expert_Performance'. Sua tarefa é ler o código que o 'Dev_Junior' colocou na mesa e reescrevê-lo ou adicionar melhorias com foco estrito em eficiência computacional (complexidade de tempo, algoritmos melhores, uso de cache ou geradores). 
Mantenha o foco apenas em performance.
"""

PROMPT_CLEAN_CODE = """
Você é o 'Linus_CleanCode'. Sua tarefa é ler as iterações anteriores do código e fazer o refactoring estético final. Adicione tipagem de dados (type hints), docstrings elegantes e garanta que o código siga estritamente o PEP 8.
"""

# =====================================================================
# 3. COREOGRAFIA DINÂMICA (O Fluxo de Trabalho por Bastão)
# =====================================================================
# O usuário joga o desafio inicial na mesa
solicitacao_usuario = "Preciso de uma função que receba uma lista de números e encontre todos os números duplicados."

# O histórico começa apenas com a dor do cliente
mesa_de_discussao = [
    {"role": "user", "content": solicitacao_usuario}
]

# PASSO 1: O Dev Junior cria a primeira versão funcional
mesa_de_discussao = executar_agente_na_mesa("Dev_Junior", PROMPT_PROGRAMADOR, mesa_de_discussao)

# PASSO 2: O Expert de Performance lê o código do Júnior e o otimiza na mesa
mesa_de_discussao = executar_agente_na_mesa("Expert_Performance", PROMPT_PERFORMANCE, mesa_de_discussao)

# PASSO 3: O Crítico de Clean Code limpa a bagunça dos anteriores e entrega o produto final
mesa_de_discussao = executar_agente_na_mesa("Linus_CleanCode", PROMPT_CLEAN_CODE, mesa_de_discussao)