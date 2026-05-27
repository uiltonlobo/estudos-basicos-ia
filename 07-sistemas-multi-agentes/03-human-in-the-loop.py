import json

# =====================================================================
# 1. ESTADO DO GRAFO COM SUPORTE A SESSÃO E INTERRUPÇÃO
# =====================================================================
class EstadoReembolso:
    def __init__(self, funcionario: str, valor: float, justificativa: str):
        self.funcionario = funcionario
        self.valor = valor
        self.justificativa = justificativa
        self.analise_agente = ""
        self.status = "PROCESSANDO" # PROCESSANDO, SUSPENSO_PARA_APROVACAO, CONCLUIDO
        self.decisao_humana = ""    # APROVADO ou REJEITADO

# =====================================================================
# 2. OPERAÇÕES DE NÓS DO SISTEMA
# =====================================================================
def no_analista_financeiro_ia(estado: EstadoReembolso):
    print(f"\n[Agente IA] Analisando política de reembolso para {estado.funcionario}...")
    print(f"[Agente IA] Valor requisitado: R$ {estado.valor:.2f}")
    
    # Validação automática preliminar
    if estado.valor > 5000.00:
        estado.analise_agente = "Análise preliminar concluída. O valor excede o teto operacional de aprovação automática da IA (R$ 5.000,00). Encaminhando para auditoria de diretoria humana."
        estado.status = "SUSPENSO_PARA_APROVACAO" # Altera a flag para congelar o fluxo
    else:
        estado.analise_agente = "Gasto dentro dos conformes da empresa. Liberado de forma automática."
        estado.status = "CONCLUIDO"
        estado.decisao_humana = "APROVADO"
        
    return estado

# =====================================================================
# 3. ENGINE DO ORQUESTRADOR DO ENGINE (Com suporte a persistência de estado)
# =====================================================================
class MotorDeFluxoFintech:
    def __init__(self):
        self.banco_estados = {} # Guarda o estado indexado por um ID de transação

    def iniciar_solicitacao(self, tx_id: str, funcionario: str, valor: float, justificativa: str):
        # Cria o estado inicial
        estado = EstadoReembolso(funcionario, valor, justificativa)
        
        # Executa o primeiro nó (Agente Financeiro)
        estado = no_analista_financeiro_ia(estado)
        
        # Salva o estado no "disco" (banco de dados)
        self.banco_estados[tx_id] = estado
        
        if estado.status == "SUSPENSO_PARA_APROVACAO":
            print(f"🛑 [Engine] Transação '{tx_id}' SUSPENSA. Aguardando intervenção via painel do gestor.")
        else:
            print(f"✅ [Engine] Transação '{tx_id}' processada direto até o fim.")
            
        return estado

    def injetar_aprovacao_humana(self, tx_id: str, decisao_operador: str):
        """Acordado por um webhook de clique de botão do frontend"""
        print(f"\n[Webhook HITL] Recebido input humano para a transação '{tx_id}': {decisao_operador}")
        
        # 1. Recupera o estado exatamente de onde ele parou no disco
        estado = self.banco_estados.get(tx_id)
        if not estado or estado.status != "SUSPENSO_PARA_APROVACAO":
            print("[Erro] Transação não encontrada ou não está aguardando aprovação.")
            return None
            
        # 2. Atualiza o estado com as credenciais do humano
        estado.decisao_humana = decisao_operador
        estado.status = "CONCLUIDO"
        
        print(f"🎉 [Engine] Retomando o grafo. Transação '{tx_id}' fechada com status final: {estado.decisao_humana}")
        return estado

# --- EXECUÇÃO DO PIPELINE DE ENGENHARIA DE PRODUTO ---
motor_financeiro = MotorDeFluxoFintech()
ID_TRANSACAO = "tx_99281_finance"

# Passo A: O funcionário submete um gasto alto (Notebook de alta performance)
motor_financeiro.iniciar_solicitacao(
    tx_id=ID_TRANSACAO,
    funcionario = "Ana Silva (Tech Lead)",
    valor = 8450.00,
    justificativa = "Compra de MacBook Pro de reposição para desenvolvimento local de microsserviços."
)

# ... Imagine que horas se passaram aqui. O servidor continuou rodando outras tarefas ...
# O estado está salvo com segurança no dicionário 'banco_estados' aguardando o clique do Diretor.

# Passo B: O Diretor entra no dashboard do sistema e clica em "Aprovar"
estado_finalizado = motor_financeiro.injected_aprovacao_humana = motor_financeiro.injetar_aprovacao_humana(
    tx_id=ID_TRANSACAO, 
    decisao_operador="APROVADO"
)