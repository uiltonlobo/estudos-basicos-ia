import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
NOME_ARQUIVO_DATASET = "dataset_iot_treinamento.jsonl"

def executar_pipeline_finetuning_completo():
    # =====================================================================
    # PASSO 1: FAZER O UPLOAD DO ARQUIVO PARA A NUVEM
    # =====================================================================
    print("[Pipeline] 1. Fazendo upload do dataset para a infraestrutura OpenAI...")
    
    arquivo_remoto = client.files.create(
        file=open(NOME_ARQUIVO_DATASET, "rb"),
        purpose="fine-tune" # Define o propósito do arquivo para habilitar o treino
    )
    
    file_id = arquivo_remoto.id
    print(f"[Pipeline] ✅ Upload concluído com sucesso. File ID gerado: {file_id}")
    
    # =====================================================================
    # PASSO 2: SOLICITAR A CRIAÇÃO DO JOB DE TREINAMENTO (FINE-TUNING)
    # =====================================================================
    print("\n[Pipeline] 2. Solicitando inicialização do Job de Fine-Tuning...")
    
    job_treinamento = client.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-4o-mini" # Escolha do modelo base leve e de baixo custo
    )
    
    job_id = job_treinamento.id
    print(f"[Pipeline] ✅ Job agendado com sucesso! Job ID gerado: {job_id}")
    
    # =====================================================================
    # PASSO 3: MONITORAMENTO ASSÍNCRONO DA FILA DE PROCESSAMENTO
    # =====================================================================
    print("\n[Pipeline] 3. Iniciando pooling de monitoramento do status do Job...")
    
    model_id_customizado = None
    while True:
        # Atualiza o status do Job consultando a API da OpenAI
        status_atual = client.fine_tuning.jobs.retrieve(job_id)
        print(f"   [Status]: {status_atual.status} | Tokens Processados: {status_atual.trained_tokens}")
        
        if status_atual.status == "succeeded":
            model_id_customizado = status_atual.fine_tuned_model
            print(f"\n🎉 [Pipeline] Treinamento FINALIZADO com sucesso!")
            print(f"[Pipeline] O ID exclusivo do seu novo modelo é: {model_id_customizado}")
            break
        elif status_atual.status in ["failed", "cancelled"]:
            print(f"\n❌ [Erro] O treinamento falhou ou foi cancelado de forma inesperada.")
            return
            
        # Aguarda 30 segundos antes de realizar a próxima checagem para não estourar rate-limits
        time.sleep(30)
        
    # =====================================================================
    # PASSO 4: CONSUMINDO O SEU MODELO CUSTOMIZADO EM PRODUÇÃO
    # =====================================================================
    print("\n[Pipeline] 4. Testando o novo modelo especializado em produção...")
    
    comando_operador = "Ativar o medidor de fluxo de água na porta 9 com amostragem a cada 2000 milissegundos."
    print(f"[User]: '{comando_operador}'")
    
    resposta_modelo = client.chat.completions.create(
        model=model_id_customizado, # Invocamos o ID do modelo gerado no passo 3
        messages=[
            {"role": "system", "content": "Você é um firmware tradutor de IoT. Transforme o comando do operador no esquema JSON industrial obrigatório."},
            {"role": "user", "content": comando_operador}
        ],
        temperature=0.0 # Mantemos estável e determinístico
    )
    
    print(f"\n=======================================================")
    print(f"💻 OUTPUT EXCLUSIVO DO SEU MODELO AJUSTADO (FINE-TUNED):")
    print(f"=======================================================\n")
    print(resposta_modelo.choices[0].message.content)
    print("=======================================================")

# Dispara a automação completa do ciclo de vida
if __name__ == "__main__":
    executar_pipeline_finetuning_completo()