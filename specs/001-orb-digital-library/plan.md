# Implementation Plan: Middleware ORB para Biblioteca Digital

**Branch**: `001-orb-digital-library` | **Date**: 2026-07-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-orb-digital-library/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

## Summary

Implementar uma Biblioteca Digital demonstrável através de um ORB próprio. O
Cliente usará Stubs para enviar envelopes JSON com framing TCP ao ORB Core; o
Broker validará JWT, localizará instâncias via Registry, despachará pelo
Skeleton e retornará respostas correlacionadas por `request_id`. Os serviços de
domínio persistirão Livro, Usuario e Emprestimo em SQLite, enquanto dois nós
independentes, o Registry Service e a API administrativa serão executáveis com
Docker Compose.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+

**Primary Dependencies**: PyJWT, FastAPI, Uvicorn, pytest, python-dotenv; `asyncio`, `socket`, `json`, `sqlite3` e `logging` da stdlib

**Storage**: SQLite via `sqlite3`, com schema SQL e banco independente por nó

**Testing**: pytest; testes unitários, integração, falhas e end-to-end

**Target Platform**: Containers Linux Python 3.11-slim e execução local em Windows/Linux/macOS com Python 3.11+

**Project Type**: Middleware/library Python com serviços TCP, cliente CLI e API administrativa auxiliar

**Performance Goals**: 100 chamadas válidas de catálogo/empréstimo em ambiente local com pelo menos 99 respostas corretas; timeout padrão de 5 s e retorno de timeout em até 6 s

**Constraints**: ORB sem RPC pronto; TCP puro com cabeçalho de 4 bytes; JSON; `asyncio`; JWT; máximo de 3 retries com backoff 0,5/1/2 s; dois nós; dependências aprovadas; TLS, frontend e consenso fora de escopo

**Scale/Scope**: Demonstração local com 5 livros, 2 usuários seed, 3 serviços remotos, 2 nós, 1 Registry, 1 API administrativa e fluxo completo de biblioteca

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The gate passes before research because the constitution and specification agree
on all required choices:

- TCP sockets puros, JSON e framing de 4 bytes para o núcleo ORB.
- `asyncio` para uma coroutine isolada por conexão.
- JWT via PyJWT, SQLite via `sqlite3` e dependências aprovadas apenas.
- Dois nós independentes, um Registry Service separado e round-robin.
- Timeout padrão configurável de 5 segundos, no máximo 3 retries e backoff
  0,5/1/2 segundos, convertendo falhas em códigos tratados.
- Logs ISO8601 estruturados com componente e `request_id`.
- Testes unitários, integração, falhas e end-to-end, além de README e
  `docs/architecture.md`.

No violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/001-orb-digital-library/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
orb_core/
├── __init__.py
├── exceptions.py
├── serializer.py
├── auth.py
├── registry.py
├── skeleton.py
├── broker.py
└── stub.py
domain/
├── __init__.py
├── livro_service.py
├── usuario_service.py
└── emprestimo_service.py
server/
├── __init__.py
├── node_1.py
└── node_2.py
registry_service/
├── __init__.py
└── main.py
admin_api/
├── __init__.py
└── main.py
client/
├── __init__.py
└── cliente_exemplo.py
database/
├── schema.sql
├── connection.py
└── seed.py
tests/
├── test_serializer.py
├── test_registry.py
├── test_auth.py
├── test_broker.py
├── test_domain.py
├── test_timeout.py
├── test_failover.py
└── test_end_to_end.py
docs/architecture.md
README.md
requirements.txt
Dockerfile
docker-compose.yml
```

**Structure Decision**: Single Python repository with reusable `orb_core`, domain
services separated from transport, executable server/registry/client processes,
administrative FastAPI, SQLite support files and pytest tests at the root. This
matches the constitution's mandated directory layout and keeps the ORB core
independent of the application domain.

## Requirements Traceability

| Requirement range | Design coverage |
|---|---|
| FR-001-FR-003 | `orb_core/auth.py`, `domain/usuario_service.py`, US1 tests |
| FR-004-FR-006 | `domain/livro_service.py`, `database/schema.sql`, US2-US3 tests |
| FR-007-FR-014 | `domain/emprestimo_service.py`, transactions, US4-US6 tests |
| FR-015-FR-018 | `stub.py`, `broker.py`, `skeleton.py`, `serializer.py`, contracts |
| FR-019-FR-022 | `server/node_1.py`, `server/node_2.py`, Registry, retry/failure tests |
| FR-023-FR-024 | logging configuration and `admin_api/main.py` |
| FR-025-FR-027 | Docker, README, architecture docs, pytest and dependency checks |

## Post-Design Constitution Check

PASS. The design artifacts introduce no new dependency, protocol, transport,
concurrency model, persistence technology or scope beyond the constitution.
`contracts/orb-protocol.md` centralizes the wire contract; `data-model.md`
defines atomic state transitions; and `quickstart.md` validates the mandatory
two-node, authentication, domain, failover and timeout scenarios.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | No constitution violations or unjustified complexity identified. |
