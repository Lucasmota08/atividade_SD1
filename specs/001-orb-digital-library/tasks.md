# Tasks: Middleware ORB para Biblioteca Digital

**Input**: Design documents from `/specs/001-orb-digital-library/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: ObrigatÃ³rios conforme `.specify/memory/constitution.md`: unitÃ¡rios,
integracao, failure-path e end-to-end.

**Organization**: As tarefas estÃ£o agrupadas por histÃ³ria de usuÃ¡rio. Fases 1 e
2 criam a base compartilhada; cada fase seguinte entrega uma histÃ³ria testÃ¡vel.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criar a estrutura inicial, dependÃªncias aprovadas e configuraÃ§Ã£o
mÃ­nima do projeto.

- [X] T001 Criar os diretÃ³rios `orb_core/`, `domain/`, `server/`, `registry_service/`, `client/`, `admin_api/`, `database/`, `tests/` e `docs/` na raiz do repositÃ³rio.
- [X] T002 [P] Criar `__init__.py` em `orb_core/__init__.py`, `domain/__init__.py`, `server/__init__.py`, `registry_service/__init__.py`, `client/__init__.py` e `admin_api/__init__.py`.
- [X] T003 [P] Criar `requirements.txt` com somente `PyJWT`, `fastapi`, `uvicorn`, `pytest` e `python-dotenv`.
- [X] T004 [P] Criar `.gitignore` com exclusÃµes para `.venv/`, `__pycache__/`, `*.pyc`, `*.db`, `.env` e logs locais.
- [X] T005 [P] Criar `README.md` com seÃ§Ãµes iniciais de objetivo, instalaÃ§Ã£o, execuÃ§Ã£o, testes e demonstraÃ§Ã£o.
- [X] T006 [P] Criar `.env.example` com `JWT_SECRET`, `JWT_EXPIRATION_MINUTES`, hosts, portas e caminhos de banco sem valores secretos reais.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implementar os contratos compartilhados que bloqueiam todas as
histÃ³rias: framing, erros, autenticaÃ§Ã£o, persistÃªncia, logging e convenÃ§Ãµes de
resposta.

**Checkpoint**: A fundaÃ§Ã£o deve estar pronta antes das fases de histÃ³ria; o
serializer, as exceÃ§Ãµes e a persistÃªncia devem ser testÃ¡veis isoladamente.

- [X] T007 [P] Criar `orb_core/exceptions.py` com `ORBError`, `ORBTimeoutError`, `ORBConnectionRefusedError`, `ORBSerializationError`, `ObjectNotFoundError`, `MethodNotFoundError` e `AuthenticationError`, incluindo cÃ³digos tratados.
- [X] T008 [P] Criar `orb_core/serializer.py` com JSON UTF-8, cabeÃ§alho de 4 bytes big-endian, leitura completa do stream e `ORBSerializationError` para framing ou payload invÃ¡lido.
- [X] T009 [P] Criar `orb_core/auth.py` com geraÃ§Ã£o e validaÃ§Ã£o JWT usando `PyJWT`, segredo/duraÃ§Ã£o por ambiente e `AuthenticationError` para token ausente, invÃ¡lido ou expirado.
- [X] T010 [P] Criar `database/schema.sql` com tabelas `livro`, `usuario` e `emprestimo`, chaves, status vÃ¡lidos, email Ãºnico e restriÃ§Ã£o para `copias_disponiveis >= 0`.
- [X] T011 [P] Criar `database/connection.py` com `get_connection(db_path: str)`, aplicaÃ§Ã£o idempotente do schema, foreign keys habilitadas e isolamento adequado para transaÃ§Ãµes.
- [X] T012 [P] Criar `tests/test_exceptions.py` para verificar hierarquia, cÃ³digos e mensagens das exceÃ§Ãµes customizadas em `orb_core/exceptions.py`.
- [X] T013 [P] Criar `tests/test_serializer.py` com round-trip, framing parcial, payload JSON invÃ¡lido, tamanho invÃ¡lido e `ORBSerializationError`.
- [X] T014 [P] Criar `tests/test_auth.py` para token vÃ¡lido, token expirado, assinatura invÃ¡lida, ausÃªncia de token e claims de usuÃ¡rio.
- [X] T015 [P] Criar `tests/test_database.py` para schema, seed de conexÃ£o, constraints de estoque/status e rollback de transaÃ§Ã£o.
- [X] T016 [P] Criar `database/seed.py` para inserir cinco livros e dois usuÃ¡rios de demonstraÃ§Ã£o sem duplicar registros ao ser executado novamente.
- [X] T017 [P] Criar `tests/conftest.py` com fixtures de banco temporÃ¡rio, ambiente JWT, servidor asyncio e cleanup de conexÃµes.
- [X] T018 Criar `orb_core/logging_config.py` com formatter ISO8601 contendo nÃ­vel, componente, `request_id` e mensagem, sem adicionar dependÃªncias.

## Phase 3: User Story 1 - Autenticar usuÃ¡rio (Priority: P1)

**Goal**: Permitir cadastro/autenticaÃ§Ã£o remota e emissÃ£o de JWT para chamadas
protegidas.

**Independent Test**: Com o serviÃ§o de usuÃ¡rio local, credenciais vÃ¡lidas geram
JWT decodificÃ¡vel; credenciais invÃ¡lidas geram `AUTH_INVALID` sem traceback.

### Tests for User Story 1

- [X] T019 [P] [US1] Criar `tests/test_usuario_service.py` para cadastro, email duplicado, autenticaÃ§Ã£o vÃ¡lida, senha invÃ¡lida e usuÃ¡rio bloqueado.
- [X] T020 [P] [US1] Criar `tests/test_auth_contract.py` para verificar que `UsuarioService.autenticar(email, senha)` retorna token e que o token funciona em `validar_token`.

### Implementation for User Story 1

- [X] T021 [US1] Implementar `domain/usuario_service.py` com `cadastrarUsuario`, `consultarUsuario` e `autenticar`, hash seguro de senha usando somente bibliotecas aprovadas/stdlib e status ativo/bloqueado.
- [X] T022 [US1] Definir no `domain/usuario_service.py` o contrato de retorno do usuÃ¡rio sem `senha_hash` e o mapeamento de credenciais invÃ¡lidas para `AuthenticationError`/`AUTH_INVALID`.
- [X] T023 [US1] Adicionar em `orb_core/broker.py` a polÃ­tica de mÃ©todos pÃºblicos/protegidos que permite autenticaÃ§Ã£o sem token e exige JWT nas demais operaÃ§Ãµes.
- [X] T024 [US1] Adicionar em `tests/test_broker_auth.py` o cenÃ¡rio de autenticaÃ§Ã£o remota sem token e rejeiÃ§Ã£o de chamada protegida com token ausente ou invÃ¡lido.

**Checkpoint**: UsuÃ¡rio vÃ¡lido consegue autenticar e obter JWT; credenciais
invÃ¡lidas e chamadas protegidas sem token retornam erro padronizado.

## Phase 4: User Story 2 - Consultar disponibilidade (Priority: P1)

**Goal**: Expor `LivroService.consultarDisponibilidade(id)` com existÃªncia,
disponibilidade e quantidade de cÃ³pias.

**Independent Test**: Livro existente retorna `{disponivel, copias}`; livro
inexistente retorna `OBJECT_NOT_FOUND`.

### Tests for User Story 2

- [X] T025 [P] [US2] Criar `tests/test_livro_service.py` para disponibilidade de livro existente, livro sem cÃ³pias e identificador inexistente.
- [X] T026 [P] [US2] Criar `tests/test_livro_contract.py` para validar o formato `{disponivel: bool, copias: int}` na resposta remota.

### Implementation for User Story 2

- [X] T027 [US2] Implementar `domain/livro_service.py` com consulta por `livro_id`, retorno de disponibilidade e `ObjectNotFoundError` para registro inexistente.
- [X] T028 [US2] Registrar `LivroService` e seus mÃ©todos no dispatch configurado em `orb_core/broker.py` e `orb_core/skeleton.py`.
- [X] T029 [US2] Adicionar logs de consulta em `domain/livro_service.py` e `orb_core/broker.py` com componente e `request_id`.

**Checkpoint**: Consulta remota de disponibilidade funciona com os envelopes do
contrato e cobre sucesso, estoque zero e objeto ausente.

## Phase 5: User Story 3 - Listar livros (Priority: P1)

**Goal**: Expor `LivroService.listarLivros()` retornando sempre uma lista.

**Independent Test**: CatÃ¡logo populado retorna livros; catÃ¡logo vazio retorna
lista vazia sem erro.

### Tests for User Story 3

- [X] T030 [P] [US3] Criar `tests/test_livro_listing.py` para catÃ¡logo populado, catÃ¡logo vazio e campos retornados sem dados sensÃ­veis.
- [X] T031 [P] [US3] Criar `tests/test_livro_listing_integration.py` para invocaÃ§Ã£o Stub -> Broker -> Skeleton -> `LivroService` com resposta de lista.

### Implementation for User Story 3

- [X] T032 [US3] Implementar `listarLivros()` em `domain/livro_service.py` com ordenaÃ§Ã£o determinÃ­stica e lista vazia quando nÃ£o houver registros.
- [X] T033 [US3] Implementar `orb_core/skeleton.py` com dispatch seguro por mÃ©todo, validaÃ§Ã£o de `getattr` e `MethodNotFoundError` sem expor mÃ©todos privados.
- [X] T034 [US3] Implementar `orb_core/broker.py` com `async handle_connection`, unmarshalling, dispatch, resposta `OK/ERROR` e correlaÃ§Ã£o de `request_id`.
- [X] T035 [US3] Implementar `orb_core/stub.py` com `invoke`, abertura TCP, framing, timeout configurÃ¡vel e validaÃ§Ã£o do `request_id` retornado.
- [X] T036 [US3] Criar `tests/test_broker.py` com servidor asyncio de objeto fake para validar o caminho Stub -> Broker -> Skeleton e os erros de objeto/mÃ©todo inexistente.

**Checkpoint**: O MVP de catÃ¡logo estÃ¡ demonstrÃ¡vel com autenticaÃ§Ã£o, consulta
e listagem remotas usando o nÃºcleo ORB.

## Phase 6: User Story 4 - Emprestar livro (Priority: P1)

**Goal**: Criar emprÃ©stimo ativo e decrementar estoque atomicamente, recusando
indisponibilidade e usuÃ¡rios invÃ¡lidos.

**Independent Test**: UsuÃ¡rio autenticado empresta uma cÃ³pia, estoque reduz;
sem cÃ³pia, usuÃ¡rio bloqueado ou token invÃ¡lido produzem erro sem alteraÃ§Ã£o.

### Tests for User Story 4

- [X] T037 [P] [US4] Criar `tests/test_emprestimo_create.py` para emprÃ©stimo vÃ¡lido, livro inexistente, usuÃ¡rio inexistente/bloqueado e `SEM_COPIAS_DISPONIVEIS`.
- [X] T038 [P] [US4] Criar `tests/test_emprestimo_concurrency.py` para duas chamadas concorrentes na Ãºltima cÃ³pia, garantindo no mÃ¡ximo um sucesso e estoque nÃ£o negativo.
- [X] T039 [P] [US4] Criar `tests/test_emprestimo_contract.py` para exigir JWT, validar retorno do emprÃ©stimo e garantir rollback em falha de negÃ³cio.

### Implementation for User Story 4

- [X] T040 [US4] Implementar `domain/emprestimo_service.py` com `emprestarLivro`, validaÃ§Ãµes de usuÃ¡rio/livro, transaÃ§Ã£o atÃ´mica, geraÃ§Ã£o de datas e cÃ³digo `SEM_COPIAS_DISPONIVEIS`.
- [X] T041 [US4] Integrar `EmprestimoService` ao dispatch protegido de `orb_core/broker.py`, preservando `auth_token` e `request_id` nos logs.
- [X] T042 [US4] Adicionar em `database/schema.sql` e `database/connection.py` o suporte necessÃ¡rio a transaÃ§Ãµes concorrentes de estoque sem permitir valor negativo.

**Checkpoint**: O emprÃ©stimo vÃ¡lido persiste estado consistente e todas as
falhas de autorizaÃ§Ã£o ou disponibilidade sÃ£o respostas tratadas.

## Phase 7: User Story 5 - Devolver livro (Priority: P1)

**Goal**: Devolver um emprÃ©stimo ativo, restaurar estoque uma Ãºnica vez e tratar
emprÃ©stimos ausentes ou jÃ¡ devolvidos.

**Independent Test**: DevoluÃ§Ã£o muda `ativo` para `devolvido` e incrementa uma
cÃ³pia; segunda devoluÃ§Ã£o nÃ£o altera estoque e retorna erro.

### Tests for User Story 5

- [X] T043 [P] [US5] Criar `tests/test_emprestimo_return.py` para devoluÃ§Ã£o vÃ¡lida, emprÃ©stimo inexistente, jÃ¡ devolvido e token invÃ¡lido.
- [X] T044 [P] [US5] Criar `tests/test_emprestimo_return_transaction.py` para verificar atomicidade de status e estoque em falhas de persistÃªncia.

### Implementation for User Story 5

- [X] T045 [US5] Implementar `devolverLivro(emprestimo_id)` em `domain/emprestimo_service.py` com transiÃ§Ã£o idempotentemente rejeitada e incremento atÃ´mico de estoque.
- [X] T046 [US5] Adicionar no `orb_core/broker.py` a autorizaÃ§Ã£o e o mapeamento de erros de devoluÃ§Ã£o para `OBJECT_NOT_FOUND` ou cÃ³digo de negÃ³cio tratado.
- [X] T047 [US5] Adicionar logs de transiÃ§Ã£o em `domain/emprestimo_service.py` com status anterior, status novo e `request_id`, sem registrar tokens ou senhas.

**Checkpoint**: O ciclo de estoque emprÃ©stimo/devoluÃ§Ã£o permanece consistente
mesmo em repetiÃ§Ã£o ou falha.

## Phase 8: User Story 6 - Listar emprÃ©stimos ativos (Priority: P1)

**Goal**: Expor apenas os emprÃ©stimos ativos do usuÃ¡rio autenticado.

**Independent Test**: UsuÃ¡rio com emprÃ©stimos ativos e devolvidos recebe somente
os ativos; sem ativos recebe lista vazia.

### Tests for User Story 6

- [X] T048 [P] [US6] Criar `tests/test_emprestimo_listing.py` para filtrar status `ativo`, lista vazia e isolamento por `usuario_id`.
- [X] T049 [P] [US6] Criar `tests/test_emprestimo_listing_contract.py` para validar a resposta remota e rejeiÃ§Ã£o sem JWT.

### Implementation for User Story 6

- [X] T050 [US6] Implementar `listarEmprestimosAtivos(usuario_id)` em `domain/emprestimo_service.py` com consulta parametrizada e ordenaÃ§Ã£o por data.
- [X] T051 [US6] Integrar o mÃ©todo ao Skeleton/Broker protegido e registrar logs de quantidade retornada em `orb_core/broker.py`.

**Checkpoint**: A consulta remota retorna somente emprÃ©stimos ativos e nÃ£o vaza
registros de outros usuÃ¡rios.

## Phase 9: User Story 7 - ResiliÃªncia a falhas (Priority: P1)

**Goal**: Converter timeout, conexÃ£o recusada e falhas transitÃ³rias em erros
tratados, com retry e recuperaÃ§Ã£o de outro nÃ³ quando possÃ­vel.

**Independent Test**: Servidor lento produz `TIMEOUT`; todos os endpoints
indisponÃ­veis produzem `CONNECTION_REFUSED`; endpoint alternativo saudÃ¡vel Ã©
alcanÃ§ado sem stack trace.

### Tests for User Story 7

- [X] T052 [P] [US7] Criar `tests/test_timeout.py` com servidor asyncio lento e verificar `ORBTimeoutError`/`TIMEOUT` dentro do limite configurado.
- [X] T053 [P] [US7] Criar `tests/test_connection_refused.py` para porta fechada, trÃªs tentativas e `ORBConnectionRefusedError`/`CONNECTION_REFUSED` final.
- [X] T054 [P] [US7] Criar `tests/test_retry.py` para backoff de 0,5/1/2 segundos, limite de tentativas e preservaÃ§Ã£o do `request_id` lÃ³gico.
- [X] T055 [P] [US7] Criar `tests/test_protocol_failures.py` para resposta com `request_id` divergente, JSON invÃ¡lido e conexÃ£o encerrada durante resposta.

### Implementation for User Story 7

- [X] T056 [US7] Implementar no `orb_core/stub.py` timeout de 5 segundos configurÃ¡vel, classificaÃ§Ã£o de falhas, retry mÃ¡ximo de trÃªs tentativas e backoff 0,5/1/2 segundos.
- [X] T057 [US7] Implementar em `orb_core/exceptions.py` e `orb_core/stub.py` a conversÃ£o de falhas de socket/stream em exceÃ§Ãµes customizadas sem vazamento de exceÃ§Ã£o crua.
- [X] T058 [US7] Adicionar no `orb_core/broker.py` respostas padronizadas para serializaÃ§Ã£o, autenticaÃ§Ã£o, objeto, mÃ©todo e erro interno, com `result: null` em erros.

**Checkpoint**: Falhas de transporte deixam de ser crashes e os testes de timeout,
conexÃ£o recusada, retry e protocolo passam isoladamente.

## Phase 10: User Story 8 - MÃºltiplos nÃ³s e failover (Priority: P1)

**Goal**: Registrar dois nÃ³s independentes para os mesmos serviÃ§os e distribuir
chamadas por round-robin, mantendo atendimento quando um nÃ³ cai.

**Independent Test**: Dois nÃ³s registrados alternam respostas; apÃ³s derrubar um,
o nÃ³ restante atende sem reconfigurar o Cliente.

### Tests for User Story 8

- [X] T059 [P] [US8] Criar `tests/test_registry.py` para registrar mÃºltiplos endpoints, lookup, round-robin, objeto ausente e isolamento de registros.
- [X] T060 [P] [US8] Criar `tests/test_registry_service.py` para operaÃ§Ãµes TCP `register`/`resolve`, framing compartilhado e concorrÃªncia de clientes.
- [X] T061 [P] [US8] Criar `tests/test_failover.py` para dois nÃ³s, parada de um endpoint, resoluÃ§Ã£o do nÃ³ restante e `CONNECTION_REFUSED` quando ambos caem.
- [X] T062 [P] [US8] Criar `tests/test_multinode_integration.py` para chamadas sucessivas distribuÃ­das entre dois `LivroService` e verificaÃ§Ã£o de round-robin.

### Implementation for User Story 8

- [X] T063 [US8] Implementar `orb_core/registry.py` com registro de endpoints, resoluÃ§Ã£o round-robin, cursor por `object_id` e `ObjectNotFoundError`.
- [X] T064 [US8] Implementar `registry_service/main.py` como servidor TCP asyncio independente com operaÃ§Ãµes `register` e `resolve` usando `orb_core/serializer.py`.
- [X] T065 [US8] Implementar `server/node_1.py` com Broker, trÃªs serviÃ§os, banco `biblioteca_node1.db` e registro de todos os objetos no Registry Service.
- [X] T066 [US8] Implementar `server/node_2.py` com configuraÃ§Ã£o equivalente, banco independente `biblioteca_node2.db` e porta TCP distinta.
- [X] T067 [US8] Atualizar `orb_core/stub.py` para resolver endpoints pelo Registry e tentar o prÃ³ximo endpoint quando o atual falhar.

**Checkpoint**: Dois nÃ³s independentes executam os serviÃ§os, round-robin Ã©
observÃ¡vel por testes e failover funciona sem alterar o Cliente.

## Phase 11: Integration and End-to-End Completion

**Purpose**: Integrar todas as histÃ³rias em uma demonstraÃ§Ã£o reproduzÃ­vel e
confirmar os contratos administrativos.

- [X] T068 Criar `tests/test_end_to_end.py` cobrindo autenticar, listar livros, consultar disponibilidade, emprestar, listar ativos e devolver via chamadas TCP reais.
- [X] T069 Criar `tests/test_end_to_end_failures.py` cobrindo nÃ³ fora do ar, servidor lento, retry e ausÃªncia de stack trace no resultado do Cliente.
- [X] T070 Implementar `client/cliente_exemplo.py` com roteiro completo da demonstraÃ§Ã£o, captura de todas as exceÃ§Ãµes customizadas e mensagens amigÃ¡veis sem traceback.
- [X] T071 Criar `admin_api/main.py` com `GET /health`, `GET /logs` e `/docs`, consulta ao Registry e estado degradado tratado quando o Registry falhar.
- [X] T072 Criar `tests/test_admin_api.py` para `/health`, `/logs` com limite e `/docs`, garantindo que nenhum endpoint administrativo execute mÃ©todos de domÃ­nio.

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Empacotar, documentar, observar e executar a validaÃ§Ã£o final.

- [X] T073 [P] Aplicar logging estruturado em `orb_core/stub.py`, `orb_core/broker.py`, `orb_core/skeleton.py`, `orb_core/registry.py`, `registry_service/main.py` e serviÃ§os de `domain/` com timestamp ISO8601, componente e `request_id`.
- [X] T074 [P] Criar `Dockerfile` com Python 3.11-slim, instalaÃ§Ã£o de `requirements.txt` e comando parametrizÃ¡vel por serviÃ§o.
- [X] T075 [P] Criar `docker-compose.yml` com `registry`, `node_1`, `node_2` e `admin_api`, portas, healthchecks, variÃ¡veis e volumes de banco/log.
- [X] T076 [P] Criar `docs/architecture.md` com diagrama Mermaid, Stub, Skeleton, Broker, Registry, framing, autenticaÃ§Ã£o, concorrÃªncia, multinode, vantagens e limitaÃ§Ãµes.
- [X] T077 Atualizar `README.md` com prÃ©-requisitos, `docker compose up`, `pytest`, execuÃ§Ã£o do cliente, endpoints administrativos, falhas e roteiro de apresentaÃ§Ã£o.
- [X] T078 Criar `tests/test_logging.py` para verificar timestamp ISO8601, nÃ­vel, componente, `request_id` e ausÃªncia de segredos nos logs.
- [X] T079 Criar `tests/test_quickstart.py` ou script de validaÃ§Ã£o em `tests/` para confirmar os comandos e cenÃ¡rios documentados em `quickstart.md`.
- [ ] T080 Executar `pytest` e corrigir falhas no escopo do projeto em `tests/`, sem introduzir dependÃªncias fora de `requirements.txt`.
- [ ] T081 Executar `docker compose config` e `docker compose up --build` para validar `docker-compose.yml`, a subida do registry, dois nÃ³s e API administrativa.
- [ ] T082 Verificar manualmente os endpoints de `admin_api/main.py` em `http://localhost:8000/health`, `http://localhost:8000/logs?limit=20` e `http://localhost:8000/docs`, conforme `contracts/admin-api.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: sem dependÃªncias; cria a estrutura e configuraÃ§Ã£o inicial.
- **Phase 2 Foundational**: depende da Phase 1; bloqueia todas as histÃ³rias.
- **US1**: depende da fundaÃ§Ã£o; habilita autenticaÃ§Ã£o usada pelas operaÃ§Ãµes protegidas.
- **US2 e US3**: dependem da fundaÃ§Ã£o; podem comeÃ§ar em paralelo com US1 se o Broker suportar o mÃ©todo pÃºblico/protegido definido.
- **US4**: depende de US1 e do modelo de Livro; cria estado de emprÃ©stimo.
- **US5**: depende de US4 para ter emprÃ©stimo ativo a devolver.
- **US6**: depende de US4/US5 para validar ativos e devolvidos.
- **US7**: depende do Stub/Broker da fundaÃ§Ã£o e pode ser validada antes dos nÃ³s finais.
- **US8**: depende do Broker, Stub, Registry e serviÃ§os de domÃ­nio; habilita failover real.
- **Phase 11**: depende de US1-US8 e integra o fluxo completo.
- **Phase 12 Polish**: depende dos cenÃ¡rios integrados; Ã© o gate final de execuÃ§Ã£o e documentaÃ§Ã£o.

### User Story Dependencies

- **US1**: independente apÃ³s fundaÃ§Ã£o; MVP de autenticaÃ§Ã£o.
- **US2**: independente apÃ³s fundaÃ§Ã£o; consulta simples de catÃ¡logo.
- **US3**: depende do serializer/Broker/Skeleton e pode ser desenvolvida em paralelo com US1/US2.
- **US4**: depende de autenticaÃ§Ã£o, Livro e banco.
- **US5**: depende de emprÃ©stimo criado por US4.
- **US6**: depende do estado criado por US4 e alterado por US5.
- **US7**: pode ser desenvolvida em paralelo apÃ³s Stub/Broker, mas sua validaÃ§Ã£o multinode usa US8.
- **US8**: depende do nÃºcleo remoto e dos serviÃ§os de domÃ­nio; Ã© prÃ©-requisito para failover end-to-end.

### Parallel Opportunities

- Setup T002-T006 pode ser executado em paralelo.
- FundaÃ§Ã£o T007-T018 pode ser dividida por arquivo, mantendo T017 disponÃ­vel para os testes.
- Dentro de cada histÃ³ria, todas as tarefas de teste marcadas `[P]` podem ser escritas em paralelo antes da implementaÃ§Ã£o.
- US1, US2 e US3 podem ser distribuÃ­das entre pessoas apÃ³s a fundaÃ§Ã£o.
- US7 pode avanÃ§ar em paralelo com US4-US6 depois que `stub.py` e `broker.py` estiverem estÃ¡veis.
- US8 separa Registry, nÃ³s e testes em arquivos diferentes.
- T073-T076 sÃ£o paralelizÃ¡veis antes da validaÃ§Ã£o final T080-T082.

## Parallel Example: MVP (US1 + catÃ¡logo mÃ­nimo)

```text
T012/T013/T014  -> testes da fundaÃ§Ã£o em paralelo
T019/T020       -> testes de autenticaÃ§Ã£o em paralelo
T021/T022       -> serviÃ§o de usuÃ¡rio
T023/T024       -> polÃ­tica do Broker e teste remoto
T025/T026       -> testes de consulta
T027/T028/T029  -> LivroService e dispatch
T030/T031       -> testes de listagem
T032/T033/T034/T035/T036 -> implementaÃ§Ã£o do caminho ORB de catÃ¡logo
```

O MVP recomendado Ã© concluir Phase 1, Phase 2, US1, US2 e US3, validar
`tests/test_broker.py` e demonstrar autenticaÃ§Ã£o, consulta e listagem antes de
implementar emprÃ©stimos e multinode.

## Parallel Example: Domain Stories

```text
US4: T037/T038/T039 em paralelo; depois T040-T042
US5: T043/T044 em paralelo; depois T045-T047
US6: T048/T049 em paralelo; depois T050-T051
```

## Parallel Example: Resilience and Multinode

```text
US7: T052/T053/T054/T055 em paralelo; depois T056-T058
US8: T059/T060/T061/T062 em paralelo; depois T063-T067
```

## Implementation Strategy

### MVP First

1. Completar Setup e Foundational.
2. Implementar US1 para emitir JWT.
3. Implementar US2 e US3 com Stub -> Broker -> Skeleton -> SQLite.
4. Executar os testes unitÃ¡rios e de integraÃ§Ã£o do catÃ¡logo.
5. Parar e validar a demonstraÃ§Ã£o mÃ­nima antes de adicionar mutaÃ§Ãµes de estado.

### Incremental Delivery

1. Adicionar US4 e US5 com transaÃ§Ãµes atÃ´micas.
2. Adicionar US6 e confirmar isolamento por usuÃ¡rio.
3. Adicionar US7 com timeout, retry e erros tratados.
4. Adicionar US8 com Registry separado, round-robin e failover.
5. Integrar cliente, API administrativa, Docker e documentaÃ§Ã£o.
6. Executar pytest, Compose e o roteiro do quickstart antes da aceitaÃ§Ã£o.

## Notes

- Toda tarefa segue `- [X] Txxx [P?] [US?] descriÃ§Ã£o com caminho de arquivo`.
- `[P]` sÃ³ aparece quando a tarefa usa arquivos diferentes e nÃ£o depende de trabalho incompleto da mesma fase.
- Tarefas de histÃ³rias tÃªm label `[US1]` a `[US8]`; Setup, Foundational e Polish nÃ£o tÃªm label de histÃ³ria.
- Nenhum RPC pronto, frontend, TLS, consenso ou dependÃªncia nÃ£o aprovada deve ser adicionado.

