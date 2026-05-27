import json

# 1. DADOS BRUTOS (Simulando o que você extraiu do banco de dados do seu sistema)
historico_chamados_suporte = [
    {
        "comando": "Ativar o sensor de temperatura da esteira de produção na porta 4 com intervalo de 10 segundos.",
        "json_esperado": {"acao": "ACTIVATE", "sensor": "temp_sensor", "porta": 4, "intervalo_ms": 10000}
    },
    {
        "comando": "Desligar o medidor de pressão da caldeira principal na porta 2 imediatamente.",
        "json_esperado": {"acao": "DEACTIVATE", "sensor": "pressure_sensor", "porta": 2, "intervalo_ms": 0}
    },
    {
        "comando": "Iniciar o leitor óptico de código de barras na porta 7 configurado para ler a cada 500 milissegundos.",
        "json_esperado": {"acao": "ACTIVATE", "sensor": "optical_sensor", "porta": 7, "intervalo_ms": 500}
    }
]

# A instrução do sistema que CORREMENTE blinda e dita o comportamento fixo do modelo
PROMPT_SISTEMA_FIXO = "Você é um firmware tradutor de IoT. Transforme o comando do operador no esquema JSON industrial obrigatório."

# 2. PROCESSO DE COMPILAÇÃO DO DATASET SEMÂNTICO
def gerar_dataset_finetuning(dados_brutos: list, nome_arquivo_saida: str):
    print(f"[Engenharia de Dados] Processando {len(dados_brutos)} amostras para o formato JSONL...")
    
    with open(nome_arquivo_saida, "w", encoding="utf-8") as arquivo_jsonl:
        for item in dados_brutos:
            
            # Construção da estrutura exata exigida pelo motor de treinamento da OpenAI
            estrutura_exemplo = {
                "messages": [
                    {"role": "system", "content": PROMPT_SISTEMA_FIXO},
                    {"role": "user", "content": item["comando"]},
                    {"role": "assistant", "content": json.dumps(item["json_esperado"])} # A saída alvo formatada como string JSON
                ]
            }
            
            # Escreve a linha convertendo o dicionário para string JSON, adicionando quebra de linha física
            arquivo_jsonl.write(json.dumps(estrutura_exemplo, ensure_ascii=False) + "\n")
            
    print(f"[Engenharia de Dados] Arquivo '{nome_arquivo_saida}' gerado com sucesso!")

# Execução do script local
NOME_ARQUIVO = "dataset_iot_treinamento.jsonl"
gerar_dataset_finetuning(historico_chamados_suporte, NOME_ARQUIVO)

# --- SIMULAÇÃO DE VALIDAÇÃO DE INTEGRIDADE ANTES DO UPLOAD ---
print("\n=======================================================")
print("📄 PREVIEW DO CONTEÚDO DO ARQUIVO JSONL GERADO:")
print("=======================================================\n")
with open(NOME_ARQUIVO, "r", encoding="utf-8") as f:
    for i, linha in enumerate(f):
        print(f"Linha #{i+1}: {linha.strip()}")
print("=======================================================")