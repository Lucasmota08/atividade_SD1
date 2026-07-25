# Middleware ORB para Biblioteca Digital

Middleware de invocação remota de objetos, construído com sockets TCP puros,
JSON com framing de 4 bytes, `asyncio`, JWT e SQLite. O cenário demonstra um
Cliente invocando `LivroService`, `UsuarioService` e `EmprestimoService` sem
conhecer a localização física dos objetos.

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Todas as bibliotecas do requirements.txt

## Executar com Docker Compose

```text
docker compose up --build
```

Serviços:

- Registry: `localhost:8765`
- Nó 1: `localhost:9001`
- Nó 2: `localhost:9002`
- API administrativa: `http://localhost:8000/docs`

Em outro terminal, execute o cliente automático de demonstração:

```text
python -m client.cliente_exemplo
```

Ou execute o **CLI interativo** para navegar pelas opções do menu no console:

```text
python -m client.cli
```

Credenciais seed: `ana@example.com` / `senha123` e `bruno@example.com` /
`senha123`.

## Executar localmente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m registry_service.main
```

Em terminais separados, inicie `server.node_1`, `server.node_2` e a API
administrativa. Use `.env.example` como referência de configuração.

## Testes

```text
pytest
```

A suíte cobre framing, exceções, JWT, Registry, dispatch, domínio, transações,
timeout, retry, failover, API administrativa e o fluxo end-to-end.

## Roteiro de demonstração

1. Execute `docker compose up --build`.
2. Autentique pelo cliente e observe o JWT ser usado nas chamadas seguintes.
3. Liste livros e consulte disponibilidade.
4. Empreste um livro e liste os empréstimos ativos.
5. Derrube um nó com `docker stop atividadeSD1-node_2-1` ou pelo nome exibido por `docker compose ps`.
6. Repita a consulta: o outro nó continua respondendo.
7. Pare ambos os nós para observar `CONNECTION_REFUSED` tratado.
8. Execute `pytest tests/test_timeout.py` para demonstrar `TIMEOUT`.
9. Devolva o livro.

## API administrativa

- `GET /health`: Registry e nós conhecidos.
- `GET /logs?limit=20`: últimas entradas de log estruturado.
- `GET /docs`: Swagger/OpenAPI.

A API administrativa não executa métodos de domínio; as invocações remotas usam
exclusivamente o protocolo TCP do ORB.
