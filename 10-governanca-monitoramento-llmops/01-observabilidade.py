import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Importações do ecossistema OpenTelemetry e OpenInference
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from openinference.instrumentation.openai import OpenAIInstrumentor

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# =====================================================================
# 1. CONFIGURAÇÃO DO PIPELINE DE OBSERVABILIDADE (INFRAESTRUTURA)
# =====================================================================
# Inicializa o provedor de rastreamento do OpenTelemetry
provedor_trace = TracerProvider()

# Configura um exportador simples que joga os logs técnicos no stderr do console
# Em produção, você trocaria o ConsoleSpanExporter por um OTLPSpanExporter apontando para o Datadog, Dynatrace ou Grafica Tempo.
exportador_console = ConsoleSpanExporter(out=sys.stderr)
processador_span = SimpleSpanProcessor(exportador_console)
provedor_trace.add_span_processor(processador_span)

# Define o provedor global do sistema
trace.set_tracer_provider(provedor_trace)

# Ativa a instrumentação automática para interceptar todas as chamadas do SDK da OpenAI
OpenAIInstrumentor().instrument()

# =====================================================================
# 2. CÓDIGO DE APLICATIVO (O Dev não mexe em nada aqui para logar)
# =====================================================================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def executar_chamada_sistema(pergunta_usuario: str):
    print("\n[Sistema] Executando chamada de negócio...")
    
    # O tracer interceptará esta chamada de forma transparente em background
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente conciso de TI."},
            {"role": "user", "content": pergunta_usuario}
        ],
        temperature=0.0
    )
    return resposta.choices[0].message.content

# Executa uma requisição comum de produção
resultado = executar_chamada_sistema("Qual é a diferença básica entre HTTP e HTTPS?")
print(f"\n[Resposta exibida ao Usuário]: {resultado}")