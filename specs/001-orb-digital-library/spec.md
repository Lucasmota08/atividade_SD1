# Especificação: Middleware ORB para Biblioteca Digital

**Feature Branch**: `001-orb-digital-library`

**Created**: 2026-07-23

**Status**: Draft

**Constitution**: Esta especificação MUST respeitar `.specify/memory/constitution.md`, que é a fonte única de verdade para stack, protocolo, arquitetura, escopo, observabilidade e testes.

## Resumo

Um sistema de Biblioteca Digital onde um Usuário consulta livros, realiza empréstimos e devoluções por meio de um Cliente que se comunica exclusivamente com um middleware ORB desenvolvido pelo grupo. O Cliente invoca métodos remotos como se os objetos estivessem localmente, enquanto o Stub encaminha as chamadas pela rede ao ORB, ao Skeleton e ao objeto de domínio correto.

O valor principal da funcionalidade é demonstrar invocação remota de objetos com desacoplamento entre Cliente e Servidor, autenticação, persistência, múltiplos nós e tratamento observável de falhas.

## Usuários / Atores

- **Usuário da Biblioteca**: consulta livros, realiza empréstimos e devoluções.
- **Cliente**: aplicação de console que representa o Usuário e executa chamadas remotas por meio do Stub.
- **Servidor**: nó que hospeda objetos remotos de domínio e o banco de dados.
- **Naming Service**: serviço que registra e localiza instâncias dos objetos remotos.

## User Scenarios & Testing

### US1 - Autenticar usuário (Priority: P1)

Como Usuário da Biblioteca, quero informar meu email e senha para receber um token de autenticação que possa ser usado nas chamadas remotas seguintes.

**Why this priority**: A autenticação protege todas as operações de usuário e é pré-requisito para empréstimos, devoluções e listagem de empréstimos.

**Independent Test**: Com o Cliente e um nó disponíveis, executar uma autenticação válida e uma inválida e verificar, respectivamente, o recebimento de um token e o erro tratado `AUTH_INVALID`.

**Acceptance Scenarios**:

1. **Given** um Usuário cadastrado com credenciais válidas, **When** o Cliente invoca `UsuarioService.autenticar(email, senha)`, **Then** recebe um token JWT válido para chamadas seguintes.
2. **Given** email ou senha inválidos, **When** o Cliente invoca `UsuarioService.autenticar(email, senha)`, **Then** recebe uma resposta de erro com código `AUTH_INVALID`, sem exceção crua.

### US2 - Consultar disponibilidade de livro (Priority: P1)

Como Usuário da Biblioteca, quero consultar um livro pelo identificador para saber se há cópias disponíveis.

**Why this priority**: A consulta é a operação principal da Biblioteca Digital e permite demonstrar uma chamada remota simples antes de alterar dados.

**Independent Test**: Com um livro existente e outro inexistente, invocar `LivroService.consultarDisponibilidade(id)` e verificar uma resposta de disponibilidade e um erro `OBJECT_NOT_FOUND`.

**Acceptance Scenarios**:

1. **Given** um livro cadastrado, **When** o Cliente invoca `LivroService.consultarDisponibilidade(id)`, **Then** recebe um objeto contendo `disponivel` (booleano) e `copias` (inteiro).
2. **Given** um identificador não cadastrado, **When** o Cliente invoca o método, **Then** recebe `OBJECT_NOT_FOUND` tratado.

### US3 - Listar livros (Priority: P1)

Como Usuário da Biblioteca, quero listar os livros cadastrados para escolher um livro para consulta ou empréstimo.

**Why this priority**: A listagem fornece descoberta de conteúdo e compõe o fluxo demonstrável da Biblioteca Digital.

**Independent Test**: Invocar `LivroService.listarLivros()` em um banco populado e em um banco vazio, verificando que a resposta é sempre uma lista.

**Acceptance Scenarios**:

1. **Given** livros cadastrados, **When** o Cliente invoca `LivroService.listarLivros()`, **Then** recebe uma lista com os livros disponíveis no catálogo.
2. **Given** nenhum livro cadastrado, **When** o Cliente invoca o método, **Then** recebe uma lista vazia, sem erro.

### US4 - Emprestar livro (Priority: P1)

Como Usuário autenticado, quero pegar um livro emprestado para registrar a retirada e atualizar a disponibilidade do catálogo.

**Why this priority**: O empréstimo é a principal operação de negócio e demonstra uma chamada remota que altera o banco de dados.

**Independent Test**: Autenticar um Usuário, emprestar um livro com cópia disponível e tentar emprestar um livro sem cópia, verificando os estados e respostas resultantes.

**Acceptance Scenarios**:

1. **Given** um Usuário autenticado e um livro com cópia disponível, **When** o Cliente invoca `EmprestimoService.emprestarLivro(usuario_id, livro_id)`, **Then** um empréstimo ativo é criado, `copias_disponiveis` é decrementado e os dados do empréstimo são retornados.
2. **Given** um Usuário autenticado e um livro sem cópias, **When** o Cliente tenta emprestar o livro, **Then** recebe erro de negócio `SEM_COPIAS_DISPONIVEIS`, sem criar empréstimo.
3. **Given** um token ausente, expirado ou inválido, **When** o Cliente tenta emprestar um livro, **Then** recebe `AUTH_INVALID` tratado.
4. **Given** um Usuário inexistente ou bloqueado, **When** o Cliente tenta emprestar um livro, **Then** recebe erro de negócio tratado e o estado do livro permanece inalterado.

### US5 - Devolver livro (Priority: P1)

Como Usuário autenticado, quero devolver um empréstimo para registrar a devolução e tornar a cópia disponível novamente.

**Why this priority**: A devolução completa o ciclo de empréstimo e garante que o estoque possa ser reutilizado.

**Independent Test**: Criar um empréstimo ativo, devolvê-lo e repetir a devolução, verificando a transição de estado e o tratamento de duplicidade.

**Acceptance Scenarios**:

1. **Given** um empréstimo ativo pertencente ao Usuário, **When** o Cliente invoca `EmprestimoService.devolverLivro(emprestimo_id)`, **Then** o empréstimo passa a `devolvido`, `copias_disponiveis` é incrementado e a confirmação é retornada.
2. **Given** um identificador de empréstimo inexistente, **When** o Cliente invoca o método, **Then** recebe erro tratado `OBJECT_NOT_FOUND`.
3. **Given** um empréstimo já devolvido, **When** o Cliente tenta devolvê-lo novamente, **Then** recebe erro de negócio tratado e a disponibilidade não é incrementada novamente.
4. **Given** um token ausente, expirado ou inválido, **When** o Cliente tenta devolver um livro, **Then** recebe `AUTH_INVALID` tratado.

### US6 - Listar empréstimos ativos do usuário (Priority: P1)

Como Usuário autenticado, quero consultar meus empréstimos ativos para acompanhar os livros que ainda estão comigo.

**Why this priority**: A consulta fecha o fluxo de acompanhamento do Usuário e fornece evidência da persistência do estado do domínio.

**Independent Test**: Criar empréstimos ativos e devolvidos para um Usuário, invocar `EmprestimoService.listarEmprestimosAtivos(usuario_id)` e verificar que somente os ativos são retornados.

**Acceptance Scenarios**:

1. **Given** um Usuário autenticado com empréstimos ativos e devolvidos, **When** o Cliente invoca o método, **Then** recebe somente os empréstimos cujo status é `ativo`.
2. **Given** um Usuário autenticado sem empréstimos ativos, **When** o Cliente invoca o método, **Then** recebe uma lista vazia.
3. **Given** um token ausente, expirado ou inválido, **When** o Cliente invoca o método, **Then** recebe `AUTH_INVALID` tratado.

### US7 - Tratar falhas de comunicação (Priority: P1)

Como Usuário, quero receber uma mensagem de erro clara quando o nó que atenderia minha chamada estiver indisponível ou demorar além do limite, sem travamento ou crash do Cliente.

**Why this priority**: Tolerância básica a falhas é parte central da demonstração de um ORB e diferencia a invocação remota de uma chamada local comum.

**Independent Test**: Interromper o nó de destino e simular um servidor lento, verificando os códigos tratados após as tentativas e o timeout configurados.

**Acceptance Scenarios**:

1. **Given** todos os nós que oferecem o objeto estão indisponíveis, **When** o Cliente faz uma chamada remota, **Then** recebe `CONNECTION_REFUSED` após as tentativas de retry definidas na constituição.
2. **Given** o servidor não responde dentro do timeout configurado, **When** o Cliente faz uma chamada remota, **Then** recebe `TIMEOUT` tratado e recupera o controle sem espera indefinida.
3. **Given** uma falha em uma tentativa e outro nó saudável registrado para o mesmo objeto, **When** o Stub realiza retry, **Then** a chamada pode ser atendida pelo nó saudável sem expor exceção de socket ao Usuário.

### US8 - Distribuir chamadas entre múltiplos nós (Priority: P1)

Como grupo, queremos demonstrar que o mesmo `LivroService` pode ser executado em dois nós independentes registrados no Naming Service, enquanto o ORB distribui as chamadas entre eles.

**Why this priority**: Multinode é requisito obrigatório da atividade e demonstra escalabilidade básica e localização transparente dos objetos remotos.

**Independent Test**: Iniciar dois nós, registrar ambos para `LivroService`, fazer chamadas sucessivas e depois derrubar um nó, verificando distribuição e continuidade pelo nó restante.

**Acceptance Scenarios**:

1. **Given** dois nós saudáveis registrados para `LivroService`, **When** o Cliente faz chamadas sucessivas, **Then** o ORB distribui as chamadas por round-robin sem o Cliente precisar conhecer o nó atendente.
2. **Given** um dos dois nós foi derrubado, **When** o Cliente invoca `LivroService`, **Then** o nó restante continua respondendo e o Cliente não precisa ser reconfigurado.
3. **Given** o Naming Service está disponível, **When** um nó inicia, **Then** ele registra suas instâncias de objetos remotos e fica localizável pelo ORB.

### Edge Cases

- O Cliente recebe resposta com `request_id` diferente da requisição; a resposta deve ser rejeitada ou tratada como erro de protocolo, sem ser associada a outra chamada.
- O token JWT está ausente, expirado ou inválido em qualquer operação protegida; a resposta deve usar `AUTH_INVALID`.
- O `object_id` não está registrado; a resposta deve usar `OBJECT_NOT_FOUND`.
- O método solicitado não pertence ao objeto remoto; a resposta deve usar `METHOD_NOT_FOUND`.
- O payload não pode ser serializado ou desserializado como JSON; a resposta deve usar `SERIALIZATION_ERROR`.
- A conexão é recusada, o servidor fecha a conexão ou o servidor não responde; o Cliente deve retornar `CONNECTION_REFUSED` ou `TIMEOUT` de acordo com a causa final.
- O livro não existe, o Usuário está bloqueado, o empréstimo não existe ou já foi devolvido; nenhuma alteração parcial de estoque ou empréstimo deve permanecer.
- Duas chamadas concorrentes tentam emprestar a última cópia; no máximo uma pode concluir com sucesso, e o estoque não pode ficar negativo.
- O catálogo ou a lista de empréstimos não contém registros; a resposta deve ser uma lista vazia.

## Requirements

### Functional Requirements

- **FR-001**: O sistema MUST permitir autenticar um Usuário por email e senha via `UsuarioService.autenticar(email, senha)` e retornar um token JWT quando as credenciais forem válidas.
- **FR-002**: O sistema MUST retornar `AUTH_INVALID` para token ausente, expirado, inválido ou credenciais inválidas em operações protegidas.
- **FR-003**: O sistema MUST permitir cadastrar e consultar Usuários por meio do `UsuarioService`, respeitando os dados definidos para a entidade.
- **FR-004**: O sistema MUST permitir listar livros por `LivroService.listarLivros()` e retornar uma lista, inclusive quando vazia.
- **FR-005**: O sistema MUST permitir consultar a disponibilidade de um Livro por `LivroService.consultarDisponibilidade(id)`, retornando `disponivel` e `copias`.
- **FR-006**: O sistema MUST retornar `OBJECT_NOT_FOUND` quando o Livro ou outro objeto de domínio solicitado não existir.
- **FR-007**: O sistema MUST permitir criar um empréstimo ativo por `EmprestimoService.emprestarLivro(usuario_id, livro_id)` quando houver cópia disponível.
- **FR-008**: Ao criar um empréstimo, o sistema MUST persistir o empréstimo e decrementar `copias_disponiveis` de forma consistente.
- **FR-009**: O sistema MUST rejeitar empréstimo sem cópia disponível com o código de negócio `SEM_COPIAS_DISPONIVEIS`, sem alterar o estado persistido.
- **FR-010**: O sistema MUST rejeitar empréstimos para Usuários inexistentes ou bloqueados com erro de negócio tratado.
- **FR-011**: O sistema MUST permitir devolver empréstimos ativos por `EmprestimoService.devolverLivro(emprestimo_id)`.
- **FR-012**: Ao devolver um empréstimo, o sistema MUST marcá-lo como `devolvido` e incrementar `copias_disponiveis` uma única vez.
- **FR-013**: O sistema MUST retornar erro tratado ao tentar devolver um empréstimo inexistente ou já devolvido.
- **FR-014**: O sistema MUST permitir listar, por `EmprestimoService.listarEmprestimosAtivos(usuario_id)`, somente os empréstimos ativos do Usuário informado.
- **FR-015**: O Cliente MUST expor as interfaces dos objetos remotos por meio de Stubs, sem exigir que o Usuário conheça detalhes de rede, serialização ou localização física do objeto.
- **FR-016**: O ORB MUST localizar o objeto pelo `object_id`, despachar pelo método solicitado e retornar uma resposta associada ao mesmo `request_id`.
- **FR-017**: Toda requisição e resposta do núcleo remoto MUST usar o envelope JSON e o enquadramento definidos na constituição.
- **FR-018**: O Naming Service MUST registrar múltiplas instâncias de um mesmo `object_id` e o ORB MUST distribuí-las por round-robin.
- **FR-019**: O sistema MUST executar pelo menos dois nós de servidor independentes, registrando os objetos remotos no mesmo Naming Service.
- **FR-020**: O Stub MUST aplicar timeout configurável, com padrão de 5 segundos, e retry de no máximo três tentativas com backoff de 0,5 s, 1 s e 2 s.
- **FR-021**: O Cliente MUST converter indisponibilidade final em `CONNECTION_REFUSED` e demora além do limite em `TIMEOUT`, sem expor exceção crua de socket.
- **FR-022**: Cada conexão recebida pelo ORB MUST ser tratada isoladamente para não bloquear chamadas concorrentes.
- **FR-023**: O sistema MUST registrar cada chamada com timestamp ISO8601, nível, componente, `request_id` e mensagem.
- **FR-024**: A API administrativa MUST oferecer `/health`, `/logs` e `/docs`, sem transportar invocações remotas do ORB.
- **FR-025**: O sistema MUST fornecer README, documentação de arquitetura com diagrama Mermaid, containerização com registry, dois nós e API administrativa, e instruções reproduzíveis de execução, incluindo `docker compose up`.
- **FR-026**: O sistema MUST ter testes unitários para serialização, registry e exceções, testes de integração para o fluxo completo e testes de falha para `CONNECTION_REFUSED` e `TIMEOUT`, executáveis com `pytest`.
- **FR-027**: O sistema MUST usar somente as dependências aprovadas pela constituição; qualquer dependência adicional exige alteração constitucional prévia.

### Key Entities

- **Livro**: representa uma obra do catálogo, com `id`, `titulo`, `autor`, `isbn` e `copias_disponiveis`. A quantidade disponível não pode ser negativa.
- **Usuario**: representa uma pessoa autorizada a usar a biblioteca, com `id`, `nome`, `email`, `senha_hash` e `status` (`ativo` ou `bloqueado`).
- **Emprestimo**: representa a relação entre um Usuário e um Livro, com `id`, `livro_id`, `usuario_id`, `data_emprestimo`, `data_devolucao_prevista` e `status` (`ativo` ou `devolvido`).
- **Objeto remoto**: representa um serviço identificado por `object_id`, seus métodos expostos e suas instâncias registradas no Naming Service.
- **Requisição remota**: representa uma chamada com `request_id`, timestamp, objeto, método, argumentos e token de autenticação.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Em ambiente local com dois nós saudáveis, pelo menos 99 de cada 100 chamadas válidas de catálogo e empréstimo concluem com a resposta esperada durante um teste de 100 chamadas.
- **SC-002**: Uma chamada para um servidor lento retorna `TIMEOUT` em até 6 segundos quando o timeout configurado é de 5 segundos, sem manter o Cliente bloqueado indefinidamente.
- **SC-003**: Quando todos os nós de um objeto estão indisponíveis, 100% das chamadas de teste terminam com `CONNECTION_REFUSED` tratado após no máximo três tentativas por chamada.
- **SC-004**: Em uma demonstração com dois nós, o Cliente continua consultando livros após a interrupção de um nó, sem alteração manual da configuração do Cliente.
- **SC-005**: 100% das mensagens de log produzidas por chamadas remotas contêm timestamp ISO8601, componente e `request_id` verificáveis.
- **SC-006**: Um Usuário consegue completar o fluxo de demonstração autenticar -> listar -> consultar -> emprestar -> listar empréstimos -> devolver usando apenas o Cliente de console e as interfaces dos Stubs.
- **SC-007**: 100% dos testes unitários, de integração e de falhas definidos para o projeto passam antes da aceitação final.
- **SC-008**: Uma pessoa com Python, Docker e Docker Compose instalados consegue iniciar o sistema e executar o fluxo principal seguindo somente o README, sem editar código-fonte.

## Assumptions

- A concorrência será implementada com `asyncio`, conforme a recomendação da constituição, e não será criada uma decisão alternativa de `threading` durante o planejamento.
- A persistência usará `sqlite3` puro nesta etapa, evitando adicionar a dependência opcional `sqlalchemy` sem necessidade demonstrada.
- O banco será inicializado com dados suficientes para a demonstração; a sugestão inicial é de cinco livros e dois Usuários, mas a quantidade exata é detalhe de preparação e não altera os contratos funcionais.
- O Cliente será uma aplicação de console, sem interface gráfica.
- O JWT será emitido pelo serviço de Usuários e exigido nas operações protegidas.
- O naming service será um processo separado acessível por TCP.
- Os nós de servidor compartilharão o cenário de dados necessário para a demonstração local; decisões detalhadas de sincronização e implantação serão definidas no plano sem introduzir consenso distribuído.
- Os critérios de desempenho são medidos em ambiente local de demonstração, não representam metas para a futura etapa em AWS.
- O comando `docker compose up` será o caminho padrão para iniciar registry, dois nós e API administrativa, e `pytest` será o caminho padrão para executar a suíte de testes.

## Out of Scope

- Interface gráfica ou frontend.
- Multas por atraso, reservas, fila de espera e outras regras avançadas de negócio.
- OAuth2 completo, múltiplos provedores de identidade e TLS.
- Eleição de líder ou consenso distribuído.
- RPC pronto como núcleo do middleware.
- Bancos de dados gerenciados em nuvem.
- Qualquer item explicitamente excluído pela seção 12 da constituição.
