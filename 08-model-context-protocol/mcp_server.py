# Guarde este arquivo como: mcp_server.py
import sys
from mcp.server.fastmcp import FastMCP

# 1. Inicializa a aplicação FastMCP
# O nome fornecido será exibido pelo cliente durante o processo de Handshake
mcp_app = FastMCP("Gerenciador_Infraestrutura_MCP")

# =====================================================================
# 2. DECLARAÇÃO DE UM RESOURCE (Ponteiro de Leitura de Dados)
# =====================================================================
@mcp_app.resource("infra://status/disco")
def obter_status_sistema() -> str:
    """Retorna o estado operacional e estático dos discos do servidor."""
    # Em produção, aqui você executaria funções reais como os.statvfs()
    return "DISCO: OK | USO: 42% | CAPACIDADE RESTANTE: 128GB | AMBIENTE: PROD"

# =====================================================================
# 3. DECLARAÇÃO DE UMA TOOL (Ação Executável por Function Calling)
# =====================================================================
@mcp_app.tool()
def limpar_cache_ambiente(diretorio: str) -> str:
    """
    Executa a limpeza física de arquivos temporários de cache em um diretório específico.
    
    :param diretorio: O nome ou caminho do diretório alvo (ex: 'temp', 'logs', 'cache').
    """
    print(f"[SERVER LOG] Executando ação de limpeza no diretório: '{diretorio}'", file=sys.stderr)
    
    # Validação de segurança simples baseada nas regras de engenharia de software
    diretorios_permitidos = ["temp", "logs", "cache"]
    if diretorio.lower() not in diretorios_permitidos:
        return f"Erro: Ação negada por motivos de segurança. O diretório '{diretorio}' não é elegível para limpeza automática."
        
    # Simulação da execução lógica
    return f"Sucesso: O diretório '{diretorio}' foi limpo e 450MB de espaço foram liberados."

# =====================================================================
# 4. INICIALIZAÇÃO DO SERVIDOR VIA STDIO
# =====================================================================
if __name__ == "__main__":
    # Inicializa o ciclo de vida do servidor escutando requisições JSON-RPC via stdio
    print("[SERVER INICIADO] Aguardando conexões do cliente...", file=sys.stderr)
    mcp_app.run(transport="stdio")