# Contrato: Protocolo ORB sobre TCP

## Transporte

- Comunicação entre Stub e ORB Core, e entre nós e Registry Service, usa TCP.
- Cada mensagem é um payload JSON UTF-8 precedido por um cabeçalho unsigned de
  4 bytes em network byte order (`big-endian`) com o tamanho do payload.
- Uma conexão atende a uma requisição e uma resposta; o servidor pode fechá-la
  depois da resposta.
- O tratamento de cada conexão é isolado em uma coroutine `asyncio`.

## Requisição de invocação

```json
{
  "request_id": "uuid-v4",
  "timestamp": "2026-07-23T14:30:00Z",
  "object_id": "LivroService",
  "method": "consultarDisponibilidade",
  "args": ["livro-042"],
  "kwargs": {},
  "auth_token": "jwt-aqui"
}
```

### Regras

- `request_id` é obrigatório, único por tentativa lógica e preservado na resposta.
- `timestamp` é ISO8601 em UTC.
- `object_id` e `method` são strings não vazias.
- `args` é lista JSON; `kwargs` é objeto JSON.
- `auth_token` pode ser nulo apenas para métodos públicos, como autenticação.
- O serializer é o único módulo que cria ou interpreta framing e JSON.

## Resposta de sucesso

```json
{
  "request_id": "uuid-v4",
  "timestamp": "2026-07-23T14:30:00Z",
  "status": "OK",
  "result": {"disponivel": true, "copias": 2},
  "error": null
}
```

## Resposta de erro

```json
{
  "request_id": "uuid-v4",
  "timestamp": "2026-07-23T14:30:05Z",
  "status": "ERROR",
  "result": null,
  "error": {
    "code": "OBJECT_NOT_FOUND",
    "message": "Objeto ou registro não encontrado"
  }
}
```

Códigos padronizados: `AUTH_INVALID`, `OBJECT_NOT_FOUND`, `METHOD_NOT_FOUND`,
`SERIALIZATION_ERROR`, `TIMEOUT`, `CONNECTION_REFUSED` e `INTERNAL_ERROR`.
Erros de domínio adicionais, como `SEM_COPIAS_DISPONIVEIS`, devem conservar o
mesmo envelope e ter mensagem clara.

## Mapeamento de exceções do Stub

| Condição | Resultado no Cliente |
|---|---|
| Timeout de leitura/escrita excedido | `ORBTimeoutError` / código `TIMEOUT` |
| `ConnectionRefusedError` após retries | `ORBConnectionRefusedError` / `CONNECTION_REFUSED` |
| JSON ou framing inválido | `ORBSerializationError` / `SERIALIZATION_ERROR` |
| Resposta com `request_id` divergente | erro de protocolo tratado, sem associação à chamada |

## Contrato do Registry Service

O Registry usa o mesmo framing, com envelopes operacionais:

```json
{
  "operation": "register",
  "object_id": "LivroService",
  "host": "node_1",
  "port": 9001,
  "node_id": "node-1"
}
```

```json
{
  "operation": "resolve",
  "object_id": "LivroService"
}
```

Uma resolução bem-sucedida retorna uma localização `{object_id, host, port,
node_id}`. A operação `resolve` deve avançar o cursor round-robin para o próximo
registro da mesma lista.
