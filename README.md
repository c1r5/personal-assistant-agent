# Personal Assistant Core

Um agente orquestrador de conectores e ações.

## Conceito Central

Este projeto é um agente inteligente projetado para atuar como um orquestrador central. Ele recebe requisições de diferentes "conectores" (como um chat, um endpoint de API, etc.), interpreta a intenção do usuário e aciona as ferramentas ou subagentes apropriados para executar a ação solicitada.

A arquitetura é construída para ser modular e extensível, permitindo que novas capacidades e integrações (conectores) sejam adicionadas de forma simples e desacoplada.

## Principais Funcionalidades

- **Orquestração Inteligente**: Um agente principal (`root_agent`) analisa as solicitações e delega para o subagente ou ferramenta mais adequado.
- **Arquitetura de Conectores Extensível**: O sistema carrega dinamicamente "ferramentas" que atuam como conectores para serviços externos. O `mcp_loader.py` é um exemplo que permite a integração com qualquer ferramenta que siga o protocolo MCP via `stdio`, `sse` ou `http`.
- **Subagentes Modulares**: Funcionalidades específicas são encapsuladas em subagentes (ex: `notes_agent`, `weather_agent`), facilitando a manutenção e a adição de novas habilidades internas.
- **Interface via API**: Expõe uma API REST (FastAPI) para receber mensagens e gerenciar sessões de conversa, permitindo a integração com qualquer frontend ou serviço de cliente.
- **Gerenciamento de Sessão**: Mantém o contexto da conversa para interações mais fluidas e personalizadas.

## Como Funciona

1.  **Requisição**: Um cliente envia uma mensagem para a API, especificando o conteúdo e o conector de origem.
2.  **Roteamento**: A API recebe a mensagem e a encaminha para o `AgentClient`, associando-a a uma sessão de usuário.
3.  **Orquestração**: O `root_agent` avalia a mensagem. Com base em suas instruções, ele decide se pode responder diretamente ou se precisa acionar uma ferramenta ou subagente.
4.  **Execução**: O subagente ou a ferramenta selecionada é executado com os parâmetros extraídos da mensagem.
5.  **Resposta**: O resultado da execução é processado pelo agente, que formata uma resposta em linguagem natural.
6.  **Entrega**: A resposta final é enviada de volta ao cliente através do canal de comunicação original.

## Estrutura do Projeto

-   `app/main.py`: Ponto de entrada da aplicação. Inicializa o servidor FastAPI, gerencia sessões e roteia as mensagens para o agente.
-   `app/agents/agent.py`: Define o `root_agent`, o cérebro do sistema. É aqui que a lógica de orquestração e o prompt principal residem.
-   `app/agents/client.py`: O cliente que encapsula a interação com o `root_agent`.
-   `app/agents/sub_agents/`: Contém os agentes especializados em tarefas específicas (ex: `notes_agent.py`). Para adicionar uma nova habilidade interna, você pode criar um novo arquivo aqui.
-   `app/agents/tools/`: Contém a lógica para se conectar a ferramentas externas. O `mcp_loader.py` é um exemplo poderoso de como carregar conectores dinamicamente.
-   `app/server/`: Controladores da API FastAPI.
-   `pyproject.toml` / `uv.lock`: Dependências do projeto.
-   `docker-compose.yml` / `Dockerfile`: Arquivos para conteinerização da aplicação.

## Como Executar com Docker

O projeto está configurado para ser executado facilmente com Docker.

### Ambiente de Desenvolvimento

Este comando sobe o serviço com hot-reload, refletindo as alterações no código automaticamente.

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build --watch
```

### Ambiente de Produção

Este comando sobe o serviço otimizado para produção.

```bash
docker compose -f docker-compose.yml up --build
```

## Como Estender

### Adicionando um Novo Subagente

1.  Crie um novo arquivo Python em `app/agents/sub_agents/` definindo seu agente.
2.  Importe e adicione o novo agente à lista `sub_agents` no arquivo `app/agents/agent.py`.
3.  Atualize o `instruction` do `root_agent` para que ele saiba quando utilizar seu novo subagente.

### Adicionando uma Nova Ferramenta

Para ferramentas que seguem o protocolo MCP, basta adicionar a configuração no seu arquivo de configuração MCP (ex: `./mcp.json`). O `mcp_loader` irá carregá-la automaticamente no início da aplicação.
