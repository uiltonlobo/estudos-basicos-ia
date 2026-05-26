import os
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMemoryManager:
    def __init__(self):
        # Estado do agente persistido na memória da aplicação
        self.resumo_historico_antigo = ""
        self.mensagens_recentes = []
        self.TOKEN_LIMIT_TRIGGER = 5 # Simulação didática: comprime a cada 5 mensagens

    def adicionar_mensagem(self, role: str, content: str):
        self.mensagens_recentes.append({"role": role, "content": content})
        
        # Dispara o gatilho de compressão se o histórico estiver crescendo muito
        if len(self.mensagens_recentes) >= self.TOKEN_LIMIT_TRIGGER:
            self._comprimir_memoria()

    def _comprimir_memoria(self):
        print("\n[Memória] ⚠️ Gatilho de segurança ativado! Comprimindo histórico para liberar janela de contexto...")
        
        # Usamos o LLM para resumir as mensagens acumuladas até aqui
        prompt_resumo = f"""
        Sua tarefa é ler o histórico de mensagens abaixo e mesclá-lo com o 'Resumo Antigo' (se houver), 
        gerando um novo e único resumo consolidado contendo apenas os fatos técnicos essenciais.
        
        Resumo Antigo: {self.resumo_historico_antigo}
        Histórico para processar: {self.mensagens_recentes}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_resumo}],
            temperature=0.0
        )
        
        # Atualiza o estado global da memória
        self.resumo_historico_antigo = response.choices[0].message.content
        
        # Limpa o array de mensagens recentes (mantendo apenas o resumo estruturado no estado)
        self.mensagens_recentes = []
        print(f"[Memória] ✅ Novo estado consolidado da memória: '{self.resumo_historico_antigo}'\n")

    def montar_contexto_para_llm(self) -> list:
        # Injeta o resumo histórico como uma diretiva de sistema para o modelo lembrar do passado
        prompt_sistema = f"Você é um assistente técnico. REGRAS DO PASSADO DA CONVERSA: {self.resumo_historico_antigo}"
        
        return [{"role": "system", "content": prompt_sistema}] + self.mensagens_recentes

# --- SIMULAÇÃO DE FLUXO DE CONVERSA EXTENSA ---
gerenciador_memoria = ChatMemoryManager()

# Simulação do usuário conversando ao longo do dia
print("[User] Olá, meu nome é Carlos e sou admin do time de DevOps.")
gerenciador_memoria.adicionar_mensagem("user", "Olá, meu nome é Carlos e sou admin do time de DevOps.")

print("[User] Estamos migrando nossos servidores para a AWS na região us-east-1.")
gerenciador_memoria.adicionar_mensagem("user", "Estamos migrando nossos servidores para a AWS na região us-east-1.")

print("[User] Meu banco de dados principal de escolha é o PostgreSQL.")
gerenciador_memoria.adicionar_mensagem("user", "Meu banco de dados principal de escolha é o PostgreSQL.")

print("[User] Acabei de configurar uma instância RDS m5.large.")
gerenciador_memoria.adicionar_mensagem("user", "Acabei de configurar uma instância RDS m5.large.")

# A quinta mensagem vai disparar a nossa função de limpeza e resumo automática de engenharia
print("[User] Preciso de ajuda para configurar o backup automático dela.")
gerenciador_memoria.adicionar_mensagem("user", "Preciso de ajuda para configurar o backup automático dela.")

# 4. Enviando o payload final limpo e otimizado para o modelo responder
payload_otimizado = gerenciador_memoria.montar_contexto_para_llm()

print("\n=======================================================")
print("🚀 PAYLOAD REAL ENVIADO PARA A API DA OPENAI (OTIMIZADO):")
print("=======================================================\n")
print(payload_otimizado)
print("=======================================================")