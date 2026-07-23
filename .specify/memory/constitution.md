<!--
Sync Impact Report
- Version change: template/unversioned -> 1.0.0
- Modified principles: none; this is the initial project constitution.
- Added sections: project metadata, ORB objective, digital library domain,
	architecture, stack, protocol, non-functional requirements, acceptance criteria,
	glossary, and governance.
- Removed sections: generic template placeholders.
- Templates requiring updates: [plan-template.md](../templates/plan-template.md) updated;
	[spec-template.md](../templates/spec-template.md) updated;
	[tasks-template.md](../templates/tasks-template.md) updated;
	[.github/agents/speckit.tasks.agent.md](../../.github/agents/speckit.tasks.agent.md) updated.
- Deferred TODOs: original ratification date is unknown and is recorded below.
-->

# Constituição do Sistema Distribuído

Este documento é a fonte única de verdade do projeto. Qualquer especificação,
plano ou tarefa gerada a partir daqui DEVE respeitar todas as decisões abaixo.
Nada aqui deve ser reinterpretado, substituído ou melhorado silenciosamente.
Em caso de ambiguidade, a seção 12 (Fora de Escopo) prevalece antes de qualquer
solução alternativa ser inventada.

## 0. Metadados do Projeto

- **Disciplina:** Sistemas Distribuídos
- **Tema do grupo:** Object Request Broker (ORB)
- **Objetivo do middleware:** Invocação remota de objetos (Remote Object Invocation)
- **Cenário de aplicação:** Biblioteca Digital
- **Linguagem:** Python 3.11+
- **Etapa atual:** Implementação do middleware, antes do projeto final em AWS

## 1. Objetivo do Projeto

O projeto MUST implementar um middleware do tipo **ORB (Object Request Broker)**,
no estilo CORBA/Java RMI, permitindo que um Cliente invoque métodos de objetos
remotos hospedados em um Servidor sem conhecer detalhes de rede, serialização ou
localização física do objeto.

O sistema MUST demonstrar desacoplamento entre cliente e servidor por meio de
Stub, marshalling e unmarshalling, comunicação síncrona cliente-servidor via
TCP, múltiplos nós independentes e tolerância básica a falhas com timeout,
retry e conexão recusada tratada.

## 2. Cenário de Aplicação: Biblioteca Digital

O cenário foi escolhido por ter poucos conceitos de domínio e mapear diretamente
para objetos remotos com métodos.

### 2.1 Entidades de Domínio

- **Livro:** `id`, `titulo`, `autor`, `isbn`, `copias_disponiveis`.
- **Usuario:** `id`, `nome`, `email`, `status` (ativo/bloqueado).
- **Emprestimo:** `id`, `livro_id`, `usuario_id`, `data_emprestimo`,
	`data_devolucao_prevista`, `status`.

### 2.2 Objetos Remotos

| Objeto Remoto | Métodos expostos |
|---|---|
| `LivroService` | `consultarLivro(id)`, `listarLivros()`, `consultarDisponibilidade(id)` |
| `UsuarioService` | `cadastrarUsuario(dados)`, `consultarUsuario(id)`, `autenticar(email, senha)` |
| `EmprestimoService` | `emprestarLivro(usuario_id, livro_id)`, `devolverLivro(emprestimo_id)`, `listarEmprestimosAtivos(usuario_id)` |

### 2.3 Narrativa de Demonstração

1. O Cliente se autentica e recebe um JWT.
2. O Cliente invoca `LivroService.consultarDisponibilidade("livro-042")`
	 como uma chamada local; o Stub serializa e envia a chamada ao ORB, que
	 localiza o objeto, executa o método e devolve o resultado.
3. O Cliente invoca `EmprestimoService.emprestarLivro(...)`, que atualiza o
	 banco de dados no Servidor.
4. Se um Servidor cair durante a chamada, o Cliente MUST receber um erro de
	 timeout tratado, nunca uma exceção crua.

## 3. Arquitetura da Solução

```text
[Cliente]
	 |
	 | chamada de método "local" (Python)
	 v
[Stub / Proxy]
	 |
	 | marshalling + TCP + JWT
	 v
[ORB Core / Broker]
	 | Connection Handler, unmarshalling, Object Registry, dispatch, auth, logs
	 v
[Skeleton]
	 | chama o objeto real do domínio
	 v
[Servidor / Objeto de Domínio real]
	 |
	 v
[Banco de Dados] (SQLite)
```

### 3.1 Componentes Obrigatórios do ORB

- **Stub:** expõe a interface remota e envia chamadas serializadas pela rede.
- **Skeleton:** recebe a chamada desserializada e a repassa ao objeto real.
- **Object Registry / Naming Service:** mapeia `object_id` para host, porta e
	instância, suportando várias instâncias do mesmo serviço.
- **Marshaller/Serializer:** único módulo autorizado a converter chamadas e
	retornos em JSON.
- **Dispatcher:** roteia a mensagem para o Skeleton correto por `object_id` e
	`method`.

### 3.2 Multinode

Devem existir no mínimo dois processos de servidor independentes, cada um com
sua instância do ORB Core e dos Skeletons, registrados no mesmo Object Registry.
O projeto MUST usar um processo separado simples, `registry_service.py`, em TCP
próprio, como Naming Service.

## 4. Stack Tecnológico

| Camada | Tecnologia escolhida |
|---|---|
| Linguagem | Python 3.11+ |
| Comunicação do ORB | TCP sockets puros (`socket` da stdlib) |
| Concorrência | `asyncio`, de forma consistente em todo o código |
| Serialização | JSON (`json` da stdlib) |
| Autenticação | JWT via `PyJWT` |
| Persistência | SQLite via `sqlite3` (ou SQLAlchemy se o grupo optar por ORM) |
| Logging | `logging` da stdlib, em formato estruturado |
| API administrativa | FastAPI somente para `/health`, `/logs` e `/docs` |
| Testes | `pytest` |
| Containerização | Docker + Docker Compose |
| Documentação | Markdown em `docs/architecture.md` + Mermaid |

O núcleo Stub -> ORB Core -> Skeleton MUST ser implementado do zero usando
`socket`. gRPC, Pyro5, RPyC e XML-RPC não podem ser usados como núcleo de RPC.
FastAPI não pode transportar invocações remotas.

### 4.1 Dependências Aprovadas

O escopo de dependências é fechado: `PyJWT`, `fastapi`, `uvicorn`, `pytest`,
`python-dotenv` e, opcionalmente, `sqlalchemy`. Qualquer outra dependência MUST
ser justificada e adicionada a esta constituição antes de ser usada.

## 5. Protocolo de Comunicação do ORB

Toda comunicação Stub-ORB Core MUST usar JSON sobre TCP com cabeçalho de 4 bytes
indicando o tamanho da mensagem (length-prefixed framing).

### 5.1 Envelope de Requisição

```json
{
	"request_id": "uuid-v4",
	"timestamp": "2026-07-22T14:30:00Z",
	"object_id": "LivroService",
	"method": "consultarDisponibilidade",
	"args": ["livro-042"],
	"kwargs": {},
	"auth_token": "jwt-aqui"
}
```

### 5.2 Envelope de Resposta

```json
{
	"request_id": "uuid-v4",
	"timestamp": "2026-07-22T14:30:00Z",
	"status": "OK",
	"result": {"disponivel": true, "copias": 2},
	"error": null
}
```

Respostas de erro MUST manter `status: "ERROR"`, `result: null` e um objeto
`error` com `code` e `message`.

### 5.3 Códigos de Erro Padronizados

`AUTH_INVALID`, `OBJECT_NOT_FOUND`, `METHOD_NOT_FOUND`, `SERIALIZATION_ERROR`,
`TIMEOUT`, `CONNECTION_REFUSED` e `INTERNAL_ERROR` são os códigos permitidos
para as situações correspondentes.

## 6. Restrições de Arquitetura

- MUST haver no mínimo dois nós independentes registrados no mesmo Naming Service.
- O timeout padrão por chamada MUST ser configurável e igual a 5 segundos.
- O Stub MUST tentar novamente no máximo três vezes, com backoff de 0,5 s, 1 s
	e 2 s.
- Indisponibilidade de todos os nós MUST retornar `CONNECTION_REFUSED` tratado.
- O Registry MUST suportar várias instâncias por `object_id`, com balanceamento
	round-robin simples no ORB Core.
- Cada conexão TCP MUST ser isolada em sua própria coroutine.
- Eleição de líder e consenso distribuído estão fora de escopo nesta etapa.

## 7. Requisitos Obrigatórios

O projeto MUST atender comunicação cliente-servidor via Stub, ORB Core e
Skeleton; middleware próprio com TCP; JWT emitido por `UsuarioService.autenticar`;
logs estruturados com timestamp; erros e retry padronizados; `/docs` via FastAPI;
testes funcionais; repositório Git; README executável; e `docs/architecture.md`
com diagrama e descrição dos componentes.

## 8. Padrões de Código

### 8.1 Idioma

Nomes técnicos MUST ser em inglês, enquanto comentários e docstrings MUST ser em
português. Nomes de domínio em português podem permanecer quando fizerem parte
do vocabulário da Biblioteca Digital.

### 8.2 Estilo

PEP 8 é obrigatório. Todas as funções públicas MUST ter type hints e docstrings
no estilo Google em módulos, classes e métodos públicos.

### 8.3 Exceções Customizadas

O código MUST usar as exceções customizadas `ORBError`, `ORBTimeoutError`,
`ORBConnectionRefusedError`, `ORBSerializationError`, `ObjectNotFoundError`,
`MethodNotFoundError` e `AuthenticationError`, sem usar `Exception` genérica para
representar falhas do domínio ou do middleware.

### 8.4 Logging

Toda entrada MUST conter timestamp ISO8601, nível, componente entre `Stub`,
`ORBCore`, `Skeleton` e `Registry`, `request_id` e mensagem. Exemplo:

```text
[2026-07-22T14:30:00Z] [INFO] [ORBCore] [req-abc123] Dispatch LivroService.consultarDisponibilidade -> node-2
```

## 9. Estrutura de Diretórios do Repositório

```text
biblioteca-orb/
├── README.md
├── docker-compose.yml
├── docs/architecture.md
├── orb_core/                 # stub.py, skeleton.py, broker.py, registry.py,
│                             # serializer.py, auth.py, exceptions.py
├── domain/                   # livro_service.py, usuario_service.py,
│                             # emprestimo_service.py
├── server/                   # node_1.py, node_2.py
├── registry_service/main.py
├── client/cliente_exemplo.py
├── admin_api/main.py
├── database/schema.sql
├── tests/                    # serializer, broker, timeout e end-to-end
└── requirements.txt
```

## 10. Documentação Obrigatória

`README.md` MUST explicar objetivo, cenário, `docker compose up`, testes e uma
chamada remota passo a passo. `docs/architecture.md` MUST conter o diagrama,
componentes, decisões, vantagens e limitações. O FastAPI MUST gerar `/docs`.

## 11. Testes

Testes são obrigatórios e MUST cobrir serializer, registry com lookup e
round-robin, exceções customizadas, chamada Stub -> Broker -> Skeleton ->
Domínio -> DB, nó fora do ar com `CONNECTION_REFUSED` e servidor lento com
`TIMEOUT`, sem travamento indefinido.

## 12. Fora de Escopo

- RPC pronto como núcleo, incluindo gRPC, Pyro5, RPyC e XML-RPC.
- Eleição de líder e consenso, incluindo Raft, Paxos e Bully.
- OAuth2 completo e múltiplos provedores de identidade.
- Banco gerenciado em nuvem nesta etapa.
- Frontend ou interface gráfica.
- TLS, salvo solicitação explícita do professor.

## 13. Critérios de Aceite

- [ ] Dois nós rodam simultaneamente e de forma independente.
- [ ] O Cliente autentica e recebe JWT válido.
- [ ] Há chamada bem-sucedida para cada objeto remoto.
- [ ] Derrubar um nó produz erro tratado, sem crash.
- [ ] Todo log contém timestamp, componente e `request_id`.
- [ ] `pytest` passa sem falhas.
- [ ] `docker compose up` sobe registry, dois nós e admin API.
- [ ] O README permite executar o projeto do zero.
- [ ] `docs/architecture.md` está completo.

## 14. Glossário

- **ORB:** middleware que permite invocar métodos de objetos remotos como locais.
- **Stub:** proxy no cliente que representa o objeto remoto.
- **Skeleton:** proxy no servidor que repassa a chamada ao objeto real.
- **Marshalling/Unmarshalling:** serialização e desserialização para transporte.
- **Naming Service / Object Registry:** resolve `object_id` para localização remota.

## Governance

Esta constituição prevalece sobre specs, planos, tarefas e práticas locais que a
contradigam. Toda alteração MUST registrar motivação, impacto e atualização dos
artefatos dependentes. A revisão de conformidade MUST ocorrer na geração do
plano, na geração das tarefas e antes da aceitação final.

Versões seguem SemVer: MAJOR para remoção ou redefinição incompatível de regras,
MINOR para novo princípio ou expansão material de escopo, e PATCH para
clarificações sem mudança semântica. Alterações MUST atualizar a data e o Sync
Impact Report.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): data original de adoção não informada | **Last Amended**: 2026-07-23
