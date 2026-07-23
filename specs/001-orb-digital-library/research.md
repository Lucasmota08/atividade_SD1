# Research: Middleware ORB para Biblioteca Digital

## Decisão: Comunicação por sockets TCP puros com framing prefixado

- **Escolha**: implementar a comunicação Stub -> ORB Core -> Skeleton e Registry
  Service com `socket`/`asyncio` da biblioteca padrão, usando JSON e um cabeçalho
  de 4 bytes em network byte order para o tamanho do payload.
- **Rationale**: atende diretamente ao objetivo acadêmico de construir o ORB,
  mantém o protocolo observável e evita bibliotecas RPC prontas proibidas pela
  constituição.
- **Alternativas consideradas**: gRPC, Pyro5, RPyC e XML-RPC foram rejeitados
  porque removeriam do grupo a implementação do middleware estudado.

## Decisão: `asyncio` para isolamento de conexões

- **Escolha**: usar uma coroutine por conexão no Broker e no Registry Service,
  com `asyncio.start_server`, `asyncio.open_connection` e timeouts assíncronos.
- **Rationale**: é a opção recomendada e mantém a concorrência consistente sem
  bloquear chamadas simultâneas; integra naturalmente com sockets TCP.
- **Alternativas consideradas**: `threading` atenderia ao isolamento, mas criaria
  um modelo de concorrência diferente e não é necessário para o escopo local.

## Decisão: SQLite puro com transações explícitas

- **Escolha**: usar `sqlite3`, com schema versionado em `database/schema.sql`,
  conexão utilitária e transações para emprestar/devolver.
- **Rationale**: SQLite é suficiente para a demonstração, já está aprovado pela
  constituição e evita uma camada ORM adicional. As operações de estoque devem
  ser atômicas para impedir que duas chamadas emprestem a última cópia.
- **Alternativas consideradas**: SQLAlchemy permanece permitido, mas foi
  rejeitado nesta etapa por não trazer benefício necessário ao domínio pequeno.

## Decisão: JWT com PyJWT e segredo configurado por ambiente

- **Escolha**: emitir JWT em `UsuarioService.autenticar` e validar o token no
  Broker antes de despachar métodos protegidos; segredo e duração vêm de
  variáveis de ambiente carregadas por `python-dotenv`.
- **Rationale**: atende ao contrato de autenticação sem criar OAuth2 ou provedor
  externo, ambos fora de escopo.
- **Alternativas consideradas**: API Key seria mais simples, mas a constituição
  escolhe JWT e o cenário precisa demonstrar emissão de token.

## Decisão: Registry Service separado com round-robin em memória

- **Escolha**: manter o Naming Service como processo TCP independente, com lista
  de endpoints por `object_id`, índice round-robin e operações de registro e
  resolução enquadradas pelo mesmo serializer.
- **Rationale**: torna visível o conceito de Naming Service e permite dois nós
  independentes sem introduzir consenso ou persistência distribuída.
- **Alternativas consideradas**: arquivo compartilhado ou registry embutido nos
  nós foram rejeitados porque escondem a fronteira de processo exigida pela
  demonstração multinode.

## Decisão: FastAPI apenas para administração

- **Escolha**: expor `/health`, `/logs` e `/docs` via FastAPI/Uvicorn, sem usar
  HTTP para invocações remotas de domínio.
- **Rationale**: cumpre a documentação OpenAPI exigida sem violar a regra de que
  o núcleo ORB deve usar sockets puros.
- **Alternativas consideradas**: endpoints HTTP para os serviços de domínio
  foram rejeitados por duplicarem e descaracterizarem o contrato remoto do ORB.

## Decisão: Testes em camadas com pytest

- **Escolha**: testes unitários para serializer, registry, auth e exceções;
  testes de integração com servidores asyncio em portas efêmeras; testes de
  falha para timeout, conexão recusada, retry e failover; e um teste end-to-end
  do fluxo de biblioteca.
- **Rationale**: cobre os contratos técnicos e as histórias US1-US8, inclusive
  os riscos específicos de framing, concorrência e estado transacional.
- **Alternativas consideradas**: somente testes unitários seriam insuficientes
  para provar o caminho Stub -> Broker -> Skeleton -> banco e o comportamento
  multinode.

## Decisão: Containerização com uma imagem e comandos por serviço

- **Escolha**: um `Dockerfile` Python 3.11-slim e um `docker-compose.yml` com
  `registry`, `node_1`, `node_2` e `admin_api`, usando variáveis de ambiente para
  portas, hosts, segredo JWT e banco.
- **Rationale**: reproduz o cenário obrigatório com um comando e mantém os nós
  independentes, apesar de compartilharem a mesma imagem.
- **Alternativas consideradas**: imagens separadas por nó aumentariam duplicação
  sem agregar valor à demonstração.
