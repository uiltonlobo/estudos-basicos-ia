import json

# Exemplo de como você deve estruturar seus logs ou dados legados 
# para treinar um modelo a se comportar como um tradutor de linguagem natural para SQL interno.
dataset_treinamento = [
    {
        "messages": [
            {"role": "system", "content": "Você é um compilador interno que converte perguntas em queries Postgres estritas."},
            {"role": "user", "content": "Quantos usuários ativos temos na região Sudeste?"},
            {"role": "assistant", "content": "SELECT COUNT(*) FROM usuarios WHERE status = 'ativo' AND regiao = 'SUDESTE';"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "Você é um compilador interno que converte perguntas em queries Postgres estritas."},
            {"role": "user", "content": "Lista o email dos top 3 clientes inadimplentes."},
            {"role": "assistant", "content": "SELECT email FROM clientes WHERE status = 'inadimplente' ORDER BY debito DESC LIMIT 3;"}
        ]
    }
]

# Salvando no formato aceito pelas APIs de Fine-Tuning (.jsonl)
caminho_arquivo = "dataset_sql_interno.jsonl"
with open(caminho_arquivo, "w", encoding="utf-8") as f:
    for exemplo in dataset_treinamento:
        f.write(json.dumps(exemplo, ensure_ascii=False) + "\n")

print(f"Dataset gerado com sucesso em '{caminho_arquivo}' pronto para upload!")

# Fluxo conceitual de disparo via SDK da OpenAI:
# 1. client.files.create(file=open(caminho_arquivo, "rb"), purpose="fine-tune")
# 2. client.fine_tuning.jobs.create(training_file="file_id_retornado", model="gpt-4o-mini")