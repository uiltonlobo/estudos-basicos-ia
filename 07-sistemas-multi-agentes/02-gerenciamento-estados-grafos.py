import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================================
# 1. DEFINIÇÃO DO ESTADO GLOBAL COMPARTILHADO (A Memória do Grafo)
# =====================================================================
class EstadoDoGrafo:
    def __init__(self, solicitacao_usuario: str):
        self.solicitacao = solicitacao_usuario
        self.codigo_gerado = ""
        self.feedback_auditoria = ""
        self.status_aprovacao = "PENDENTE"
        self.tentativas = 0

# =====================================================================
# 2. DEFINIÇÃO DOS NÓS (AGENTES ESPECIALISTAS)
# =====================================================================
def no_gerador_codigo(estado: EstadoDoGrafo):
    print(f"\n[Nó Gerador] Escrevendo código para a demanda... (Tentativa {estado.tentativas + 1})")
    estado.tentativas += 1
    
    prompt = f"Solicitação: {estado.solicitacao}\nFeedback anterior se houver: {estado.feedback_auditoria}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um programador Python focado em backend. Escreva apenas o código limpo dentro do padrão exigido pelo usuário."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    # Atualiza o estado global com a produção do agente
    estado.codigo_gerado = response.choices[0].message.content
    return estado

def no_auditor_seguranca(estado: EstadoDoGrafo):
    print("[Nó Auditor] Analisando superfícies de ataque e boas práticas no código gerado...")
    
    # Simulação de análise semântica rígida
    if "admin" in estado.codigo_gerado.lower() or "password" in estado.codigo_gerado.lower() or "exec(" in estado.codigo_gerado.lower():
        estado.status_aprovacao = "REJEITADO"
        estado.feedback_auditoria = "ERRO DE SEGURANÇA CRÍTICO: Foi detectado o uso de strings hardcoded de credenciais ou funções perigosas como 'exec()'. Remova e use variáveis de ambiente."
    else:
        estado.status_aprovacao = "APROVADO"
        estado.feedback_auditoria = "Código limpo e em conformidade com as diretrizes de SecOps."
        
    return estado

# =====================================================================
# 3. O ORQUESTRADOR DO ENGINE DO GRAFO (Roteamento de Arestas Condicionais)
# =====================================================================
def executar_grafo_multi_agente(solicitacao: str):
    # Inicializa o estado com o input do cliente
    estado_sistema = EstadoDoGrafo(solicitacao)
    
    MAX_CICLOS = 3
    while estado_sistema.tentativas < MAX_CICLOS:
        # Passo 1: Executa o Nó de Criação
        estado_sistema = no_gerador_codigo(estado_sistema)
        
        # Passo 2: Passa o resultado obrigatoriamente para o Nó de Auditoria
        estado_sistema = no_auditor_seguranca(estado_sistema)
        
        # ARESTA CONDICIONAL: Avalia o estado para decidir o roteamento
        print(f"[Grafo Engine] Avaliando Aresta Condicional... Status: {estado_sistema.status_aprovacao}")
        
        if estado_sistema.status_aprovacao == "APROVADO":
            print("\n🎉 [Grafo Engine] Fluxo finalizado com sucesso! Código aprovado em produção.")
            break
        else:
            print("⚠️ [Grafo Engine] Código reprovado. Redirecionando fluxo de volta para o gerador corrigir.")
            
    return estado_sistema

# --- SIMULAÇÃO DE INPUT COMPLEXO ---
# O usuário pede algo perigoso de propósito (colocar a senha direto no código)
pedido_usuario = "Escreva uma função em Python para conectar no banco de dados. Use a senha padrão 'admin123' para facilitar os testes."

estado_final_processado = executar_grafo_multi_agente(pedido_usuario)

print("\n=======================================================")
print("💻 ENTREGÁVEL FINAL PRODUZIDO PELO GRAFO MUTLI-AGENTE:")
print("=======================================================\n")
print(estado_final_processado.codigo_gerado)
print("\n=======================================================")