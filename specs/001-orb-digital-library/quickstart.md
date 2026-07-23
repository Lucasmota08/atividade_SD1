# Quickstart: Middleware ORB para Biblioteca Digital

Este guia valida o fluxo principal e os requisitos de resiliência descritos em
`spec.md`. Os comandos devem ser executados a partir da raiz do repositório.

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Ambiente virtual recomendado

## Instalação local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Em shells Unix, use `source .venv/bin/activate`.

## Validação unitária

```text
pytest tests/test_serializer.py tests/test_registry.py tests/test_auth.py
```

Resultado esperado: serializer, framing, round-robin, JWT e exceções
customizadas passam sem falhas.

## Validação do núcleo ORB

```text
pytest tests/test_broker.py
```

Resultado esperado: uma chamada Stub -> Broker -> Skeleton -> objeto fake retorna
uma resposta `OK`; método inexistente retorna `METHOD_NOT_FOUND`; objeto
inexistente retorna `OBJECT_NOT_FOUND`.

## Subida multinode

```text
docker compose up --build
```

Resultado esperado: os serviços `registry`, `node_1`, `node_2` e `admin_api`
ficam ativos. O Registry deve listar as instâncias de `LivroService`,
`UsuarioService` e `EmprestimoService`.

Verifique a API administrativa em:

- `http://localhost:8000/health`
- `http://localhost:8000/logs?limit=20`
- `http://localhost:8000/docs`

## Fluxo funcional da demonstração

Execute o cliente de exemplo em outro terminal:

```text
python -m client.cliente_exemplo
```

Resultado esperado, nesta ordem:

1. autenticação válida retorna JWT;
2. listagem retorna livros;
3. consulta de disponibilidade retorna `disponivel` e `copias`;
4. empréstimo cria registro ativo e reduz estoque;
5. listagem retorna o empréstimo ativo;
6. devolução muda o status para `devolvido` e restaura estoque.

Os detalhes dos envelopes remotos estão em [contracts/orb-protocol.md](contracts/orb-protocol.md),
e as entidades e invariantes estão em [data-model.md](data-model.md).

## Validação de falhas

### Nó indisponível com failover

1. Inicie o Compose.
2. Faça uma chamada de catálogo pelo cliente.
3. Pare `node_2`:

```text
docker stop node_2
```

4. Faça novas chamadas de `LivroService`.

Resultado esperado: o Registry/Stub direciona a chamada ao nó restante. Se todos
os nós forem interrompidos, o Cliente retorna `CONNECTION_REFUSED` após no máximo
três tentativas, sem traceback cru.

### Servidor lento

```text
pytest tests/test_timeout.py
```

Resultado esperado: o servidor de teste que excede o limite produz `TIMEOUT` em
até aproximadamente 6 segundos com timeout configurado de 5 segundos.

## Suíte completa

```text
pytest
```

Resultado esperado: testes unitários, integração, falhas, failover e end-to-end
passam. A cobertura do cenário completo deve incluir autenticação, catálogo,
empréstimo, devolução e listagem de empréstimos ativos.

## Encerramento

```text
docker compose down
```
