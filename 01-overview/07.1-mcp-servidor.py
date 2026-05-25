# servidor_mcp.py (Roda de forma independente, ex: porta 8000)

# Instalação necessária no ambiente: pip install mcp
from mcp.server.fastmcp import FastMCP
import os

# 1. Inicializa o Servidor MCP
mcp_server = FastMCP("Gerenciador_Logs_Producao", host="127.0.0.1", port=8000)

# 2. Expondo uma Recurso (Resource - Apenas leitura de contexto estático)
@mcp_server.resource("logs://hoje")
def obter_logs_hoje() -> str:
    return "[2026-05-22] ERROR: Falha de conexão na tabela de usuários."

# 3. Expondo uma Ferramenta (Tool - Executável com parâmetros estruturados)
@mcp_server.tool()
def analisar_diretorio_codigo(caminho_projeto: str) -> str:
    if not os.path.exists(caminho_projeto):
        return f"Erro: O caminho {caminho_projeto} não existe."
    return f"Arquivos: {', '.join(os.listdir(caminho_projeto))}"

if __name__ == "__main__":
    # 4. Executa o servidor via SSE (para comunicação remota)
    # Nesta versão do FastMCP, host/port vão no construtor.
    mcp_server.run(transport="sse")