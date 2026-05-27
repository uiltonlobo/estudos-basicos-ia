# Guarde este arquivo como: mcp_remote_server.py
from mcp.server.fastmcp import FastMCP

# 1. Inicializa o servidor MCP Base (Core do Protocolo) com configuração SSE
# FastMCP gerencia automaticamente host/port e transporte SSE
servidor_mcp = FastMCP("CRM_Corporativo_Remoto_MCP", host="127.0.0.1", port=8080)

# 2. Registra uma ferramenta (Tool) de consulta ao banco de dados fictício
@servidor_mcp.tool()
def consultar_perfil_cliente(cpf: str) -> str:
    """Busca dados cadastrais e o score de crédito de um cliente usando o CPF."""
    print(f"[LOG SERVER] Query executada no banco para o CPF: {cpf}")
    
    # Simulação de retorno de um banco de dados relacional
    if cpf == "12345678900":
        perfil = {"nome": "Adriano Souza", "status": "Prime", "score_credito": 950, "limite_cartao": 15000.00}
    else:
        perfil = {"nome": "Cliente Não Encontrado", "status": "Inativo", "score_credito": 0, "limite_cartao": 0.00}
        
    return f"Resultado do CRM: {perfil}"

if __name__ == "__main__":
    print("[Mesa de Infra] Iniciando Servidor MCP Remoto via SSE na porta 8080...")
    # Roda o servidor usando transporte SSE (Server-Sent Events) com Uvicorn automaticamente
    servidor_mcp.run(transport="sse")