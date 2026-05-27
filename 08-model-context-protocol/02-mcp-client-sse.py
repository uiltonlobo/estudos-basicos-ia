# Guarde este arquivo como: mcp_remote_client.py
import os
import asyncio
import json
from dotenv import load_dotenv
from openai import OpenAI

# Importações específicas do ecossistema MCP para conexões remotas de rede (SSE)
from mcp import ClientSession
from mcp.client.sse import sse_client

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicialização do cliente do modelo de linguagem (OpenAI)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
# URL de gateway do nosso servidor MCP distribuído na rede
URL_SERVIDOR_MCP = "http://localhost:8080/sse"

async def rodar_cliente_mcp_remoto():
    print(f"[Client Remoto] 1. Estabelecendo conexão de rede com: {URL_SERVIDOR_MCP}")
    
    # 1. Abre a conexão persistente via Server-Sent Events (SSE) com o servidor remoto
    async with sse_client(url=URL_SERVIDOR_MCP) as (read_stream, write_stream):
        
        # 2. Inicializa a sessão de protocolo MCP sobre a camada de rede criada
        async with ClientSession(read_stream, write_stream) as sessao_mcp:
            print("[Client Remoto] 2. Executando handshake HTTP com o microsserviço...")
            await sessao_mcp.initialize()
            
            # PASSO A: Descoberta dinâmica das ferramentas expostas remotamente pela empresa
            catalogo_ferramentas = await sessao_mcp.list_tools()
            nomes_descobertos = [t.name for t in catalogo_ferramentas.tools]
            print(f"[Catálogo Remoto] Ferramentas disponíveis no microsserviço: {nomes_descobertos}")
            
            # --- CONTEXTO DE NEGÓCIO ---
            pergunta_usuario = "Consulte os dados do cliente com o CPF 12345678900 para mim, por favor."
            print(f"\n[User]: '{pergunta_usuario}'")
            
            # Adapta as definições de schemas remotos obtidos via rede para o formato aceito pela OpenAI
            ferramentas_mapeadas_openai = []
            for tool in catalogo_ferramentas.tools:
                ferramentas_mapeadas_openai.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
                
            # PASSO B: O LLM analisa o prompt do usuário e decide usar a ferramenta remota do CRM
            print("\n[Client Remoto] 3. Solicitando decisão de orquestração ao LLM...")
            resposta_llm = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": pergunta_usuario}],
                tools=ferramentas_mapeadas_openai,
                tool_choice="auto"
            )
            
            mensagem_modelo = resposta_llm.choices[0].message
            
            # PASSO C: Executando a ferramenta de rede
            if mensagem_modelo.tool_calls:
                chamada = mensagem_modelo.tool_calls[0]
                nome_tool = chamada.function.name
                argumentos_calc = json.loads(chamada.function.arguments)
                
                print(f"\n[LLM Decisão] Invocar ferramenta de rede '{nome_tool}' com os dados: {argumentos_calc}")
                
                # O cliente executa uma requisição HTTP POST transparente (RPC) enviando a ordem ao servidor remoto
                print("[Client Remoto] 4. Transmitindo execução de Tool via requisição de rede...")
                resultado_remoto = await sessao_mcp.call_tool(nome_tool, arguments=argumentos_calc)
                
                # Extrai o texto gerado na execução física do servidor remoto
                texto_retorno_crm = resultado_remoto.content[0].text
                print(f"[Resposta de Rede] Output bruto retornado pelo servidor remoto: '{texto_retorno_crm}'")
                
                # PASSO D: Geração da resposta final amigável ao usuário
                print("\n[Client Remoto] 5. Gerando síntese de negócio com o LLM...")
                resposta_final = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": pergunta_usuario},
                        mensagem_modelo,
                        {
                            "role": "tool",
                            "tool_call_id": chamada.id,
                            "name": nome_tool,
                            "content": texto_retorno_crm
                        }
                    ]
                )
                
                print(f"\n=======================================================")
                print(f"📩 OUTPUT EM REDE EXIBIDO AO USUÁRIO:\n{resposta_final.choices[0].message.content}")
                print("=======================================================")
            else:
                print(f"\n[Output Direto]: {mensagem_modelo.content}")

if __name__ == "__main__":
    # Roda o cliente assincronamente
    asyncio.run(rodar_cliente_mcp_remoto())
