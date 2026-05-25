import asyncio
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# 1. Inicializa o client tradicional da OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# URL de onde o seu servidor MCP independente está rodando
SERVER_SSE_URL = "http://localhost:8000/sse"

async def rodar_agente_mcp_remoto():
    print(f"[Client] Conectando ao endpoint MCP remoto: {SERVER_SSE_URL}...")
    
    # 1. Conecta ao servidor rodando separadamente via HTTP/SSE
    async with sse_client(url=SERVER_SSE_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as sessao:
            
            # Inicializa o handshake do protocolo MCP
            await sessao.initialize()
            print("[Client] Conexão de rede estabelecida com o MCP Server!")

            # 2. Descoberta Dinâmica de Ferramentas via Rede
            ferramentas_mcp = await sessao.list_tools()
            
            openai_tools = []
            for tool in ferramentas_mcp.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            # 3. Prompt do Usuário
            prompt_usuario = "Verifique os arquivos do diretório '.' usando o servidor remoto."
            
            # 4. Primeira chamada ao LLM
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_usuario}],
                tools=openai_tools
            )

            mensagem_llm = response.choices[0].message

            # 5. Se o LLM decidir agir, disparamos a chamada de rede para o servidor
            if mensagem_llm.tool_calls:
                tool_call = mensagem_llm.tool_calls[0]
                nome_ferramenta = tool_call.function.name
                argumentos = json.loads(tool_call.function.arguments)

                print(f"\n[LLM]: Decidiu invocar a ferramenta remota '{nome_ferramenta}'")
                
                # 6. A requisição HTTP/RPC trafega até o servidor independente aqui:
                resultado_mcp = await sessao.call_tool(nome_ferramenta, arguments=argumentos)
                conteudo_resultado = resultado_mcp.content[0].text
                
                # 7. Retorna o resultado técnico para a consolidação do modelo
                resposta_final = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": prompt_usuario},
                        mensagem_llm,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": nome_ferramenta,
                            "content": conteudo_resultado
                        }
                    ]
                )

                print(f"\n[Assistente Resposta Final]:\n{resposta_final.choices[0].message.content}")

if __name__ == "__main__":
    asyncio.run(rodar_agente_mcp_remoto())