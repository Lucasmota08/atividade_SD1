# Contrato: API Administrativa

A API administrativa existe apenas para observabilidade e documentação. Ela não
executa métodos de `LivroService`, `UsuarioService` ou `EmprestimoService`.

## `GET /health`

Retorna o estado do processo administrativo e os nós conhecidos pelo Registry.

Resposta `200`:

```json
{
  "status": "ok",
  "nodes": [
    {
      "node_id": "node-1",
      "host": "node_1",
      "port": 9001,
      "objects": ["LivroService", "UsuarioService", "EmprestimoService"]
    }
  ]
}
```

O endpoint deve informar estado degradado quando o Registry não puder ser
consultado, sem expor traceback ao consumidor.

## `GET /logs?limit=100`

Retorna as últimas entradas do log estruturado, limitadas por `limit`.

Resposta `200`:

```json
{
  "entries": [
    "[2026-07-23T14:30:00Z] [INFO] [ORBCore] [req-abc123] Dispatch LivroService.listarLivros -> node-1"
  ],
  "limit": 100
}
```

`limit` deve aceitar um valor positivo configurável e aplicar um limite máximo
para evitar leitura excessiva do arquivo.

## `GET /docs`

A documentação Swagger/OpenAPI gerada pelo FastAPI deve estar disponível neste
caminho. Os endpoints administrativos são documentados; os métodos remotos do
ORB permanecem definidos no contrato TCP.
