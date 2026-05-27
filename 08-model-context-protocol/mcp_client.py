# Guarde este arquivo como: mcp_client.py
import os
import asyncio
import json
from dotenv import load_dotenv
from openai import OpenAI

# Importações oficiais do ecossistema MCP para gerenciamento de clientes
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicialização do modelo de IA corporativo
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def rodar_pipeline_mcp_completo():
    print("[Client] 1. Configurando parâmetros de inicialização do Servidor...")
    
    # Define como o cliente deve inicializar o servidor MCP localmente.
    # Simulamos a execução do interpretador Python rodando o nosso arquivo de servidor.
    parametros_servidor = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=os.environ.copy()
    )
    
    # 2. Inicializa o canal de transporte stdio (StdIn / StdOut)
    async with stdio_client(parametros_servidor) as (read_stream, write_stream):
        # Cria a sessão oficial de comunicação baseada no protocolo MCP
        async with ClientSession(read_stream, write_stream) as sessao_mcp:
            
            # Executa o HANDSHAKE inicial do protocolo MCP (Aperto de mão estruturado)
            print("[Client] 2. Executando handshake e lendo capacidades do servidor...")
            await sessao_mcp.initialize()
            
            # PASSO A: Descoberta Dinâmica de Recursos (Resources)
            recursos_disponiveis = await sessao_mcp.list_resources()
            print(f"\n[Catálogo] Recursos descobertos no servidor: {[r.uri for r in recursos_disponiveis.resources]}")
            
            # PASSO B: Descoberta Dinâmica de Ferramentas (Tools)
            ferramentas_disponiveis = await sessao_mcp.list_tools()
            print(f"[Catálogo] Ferramentas descobertas no servidor: {[t.name for t in ferramentas_disponiveis.tools]}")
            
            # --- MUDANÇA DE CONTEXTO: ENTRADA DO USUÁRIO ---
            prompt_usuario = "O sistema está apresentando lentidão. Verifique o status do disco do servidor e, se necessário, limpe o cache de logs."
            print(f"\n[User]: '{prompt_usuario}'")
            
            # Traduz as ferramentas do padrão MCP para o formato esperado pelo Function Calling da OpenAI
            ferramentas_openai = []
            for tool in ferramentas_disponiveis.tools:
                ferramentas_openai.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            # PASSO C: O Modelo de IA analisa o problema do usuário e as capacidades do MCP
            print("\n[Client] 3. Consultando inteligência do LLM com o catálogo MCP...")
            resposta_llm = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_usuario}],
                tools=ferramentas_openai,
                tool_choice="auto"
            )
            
            mensagem_modelo = resposta_llm.choices[0].message
            
            # PASSO D: Execução Dinâmica da Ação via Protocolo MCP
            if mensagem_modelo.tool_calls:
                chamada = mensagem_modelo.tool_calls[0]
                nome_tool = chamada.function.name
                argumentos = json.loads(chamada.function.arguments)
                
                print(f"\n[LLM Decisão] Acionar ferramenta MCP '{nome_tool}' com os argumentos: {argumentos}")
                
                # O cliente invoca a ferramenta diretamente no servidor via RPC usando o SDK do MCP
                print(f"[Client] 4. Disparando chamada RPC para o Servidor MCP...")
                resultado_servidor = await sessao_mcp.call_tool(nome_tool, arguments=argumentos)
                
                # Extrai o texto puro retornado pela execução nativa do servidor
                texto_retorno_mcp = resultado_servidor.content[0].text
                print(f"[Server Resposta] Output bruto do servidor MCP: '{texto_retorno_mcp}'")
                
                # PASSO E: Consolidação e Resposta Final ao Usuário
                print("\n[Client] 5. Devolvendo o resultado técnico para a síntese final da IA...")
                resposta_final = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": prompt_usuario},
                        mensagem_modelo,
                        {
                            "role": "tool",
                            "tool_call_id": chamada.id,
                            "name": nome_tool,
                            "content": texto_retorno_mcp
                        }
                    ]
                )
                
                print(f"\n=======================================================")
                print(f"📩 OUTPUT FINAL EXIBIDO AO USUÁRIO:\n{resposta_final.choices[0].message.content}")
                print("=======================================================")
            else:
                print(f"\n[Output Direto]: {mensagem_modelo.content}")

# Executa o loop assíncrono do cliente
if __name__ == "__main__":
    asyncio.run(rodar_pipeline_mcp_completo())