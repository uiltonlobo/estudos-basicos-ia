## 🛠️ Conceitos de Engenharia de IA Estudados neste Projeto

Este repositório consolida o meu aprendizado prático inicial na transição de sistemas determinísticos para sistemas probabilísticos utilizando LLMs. Abaixo estão listados os pilares conceituais que guiaram a arquitetura das soluções aqui desenvolvidas:

### 1. Engenharia de Prompt (Prompt Engineering)
Foco na contextualização, restrição e formatação de entradas para garantir saídas previsíveis de modelos probabilísticos. Aplicação prática de padrões de arquitetura de prompts para ambiente corporativo, incluindo **Few-Shot Prompting** (calibragem de formato por exemplos), **Chain-of-Thought** (indução de cadeias lógicas de raciocínio intermediárias) e geração estrita de saídas estruturadas em payloads JSON estáveis para integração de microsserviços.

### 2. Busca Semântica (Semantic Search)
Substituição da busca clássica por correspondência de palavras-chave (indexação textual) pela busca baseada em significado. Utilização de **Embeddings** para mapear textos em vetores numéricos de alta dimensionalidade, permitindo encontrar dados correlacionados através de cálculos de proximidade geométrica utilizando a métrica de **Similaridade de Cosseno** e Produto Escalar.

### 3. Bancos de Dados Vetoriais (Vector DBs)
Armazenamento, indexação e recuperação performática de coleções de vetores de alta dimensão. Estudo de algoritmos de **ANN (Approximate Nearest Neighbors)**, com ênfase em estruturas de grafos **HNSW (Hierarchical Navigable Small World)** para varredura de milhões de vetores em milissegundos. Prática em modelagem de coleções, injeção idempotente de dados e aplicação de filtros híbridos correlacionando metadados relacionais na própria busca vetorial.

### 4. RAG (Retrieval-Augmented Generation)
Implementação de um padrão de design de injeção de dependência em tempo de execução para mitigar alucinações e contornar a data de corte de conhecimento de um LLM. O pipeline intercepta a query do usuário, realiza um processo de **Chunking** e extração semântica em bases de dados privadas, e injeta dinamicamente os trechos mais relevantes como contexto fixo para a resposta do modelo.

### 5. Agentes de IA (AI Agents)
Evolução de fluxos de execução lineares para sistemas dinâmicos baseados em loops contínuos de decisão. Implementação do padrão **ReAct (Reasoning and Acting)**, onde o LLM atua como motor central de orquestração, gerenciando de forma autônoma o planejamento de subtarefas, a retenção de memória de curto/longo prazo e a invocação de ferramentas (*Function Calling*) baseadas em código do sistema legado.

### 6. Sistemas Multi-Agentes (Multi-Agent Systems)
Arquitetura de sistemas distribuídos baseada no princípio de responsabilidade única (SRP) do SOLID. Quebra de problemas macros complexos através da criação de equipes de agentes especialistas atômicos (ex: Desenvolvedor, QA, Analista de Dados). Gerenciamento de estado complexo modelado através de **Grafos Direcionados Cíclicos (DAGs)** ou Máquinas de Estado para coordenar a troca de mensagens entre os nós.

### 7. Model Context Protocol (MCP)
Adoção do protocolo aberto universal (JSON-RPC 2.0) criado para desacoplar a camada de modelos (Clients) da camada de infraestrutura de dados e ferramentas (Servers). Criação e consumo de servidores MCP agnósticos operando nativamente via entrada/saída padrão (`stdio`) e arquiteturas de redes distribuídas utilizando **SSE (Server-Sent Events) sobre HTTP**, centralizando a governança e segurança das APIs.

### 8. Ajuste Fino (Fine-Tuning)
Modificação profunda do comportamento e comportamento sináptico de redes neurais. Enquanto o RAG fornece conhecimento dinâmico, o Fine-Tuning foi estudado para ensinar novos tons de voz, formatações ríspidas de escrita e sintaxes de nicho (ex: conversão de texto puro para queries de banco interno). Foco no padrão de eficiência **LoRA (Low-Rank Adaptation)**, injetando adaptadores matemáticos nas camadas de atenção sem a necessidade de re-treinamento completo do modelo base.

### 9. Governança e Monitoramento (LLMOps)
Garantia de segurança, resiliência e controle financeiro de aplicações de IA em escala de produção. Práticas de blindagem arquitetural através de **Guardrails** de entrada e saída (mitigando ataques de *Prompt Injection*, vazamentos de PII/LGPD e alucinações), implementação de **Cache Semântico** vetorial para redução drástica no consumo de tokens e adoção de ferramentas de observabilidade técnica e tracing para auditoria de grafos de agentes.