# Data Model: Middleware ORB para Biblioteca Digital

## Livro

Representa uma obra disponível no catálogo.

| Campo | Tipo | Regras |
|---|---|---|
| `id` | texto | Identificador único, obrigatório |
| `titulo` | texto | Obrigatório |
| `autor` | texto | Obrigatório |
| `isbn` | texto | Obrigatório; deve identificar a edição cadastrada |
| `copias_disponiveis` | inteiro | Obrigatório; deve ser maior ou igual a zero |

## Usuario

Representa uma pessoa que pode autenticar e usar a biblioteca.

| Campo | Tipo | Regras |
|---|---|---|
| `id` | texto | Identificador único, obrigatório |
| `nome` | texto | Obrigatório |
| `email` | texto | Obrigatório; único para autenticação |
| `senha_hash` | texto | Obrigatório; senha nunca é persistida em texto puro |
| `status` | texto | Obrigatório; valores `ativo` ou `bloqueado` |

## Emprestimo

Representa a retirada de um Livro por um Usuario.

| Campo | Tipo | Regras |
|---|---|---|
| `id` | texto | Identificador único, obrigatório |
| `livro_id` | texto | FK para `Livro.id`, obrigatório |
| `usuario_id` | texto | FK para `Usuario.id`, obrigatório |
| `data_emprestimo` | timestamp ISO8601 | Obrigatório |
| `data_devolucao_prevista` | timestamp ISO8601 | Obrigatório |
| `status` | texto | Obrigatório; valores `ativo` ou `devolvido` |

## Objeto remoto registrado

Representa uma instância localizável pelo Naming Service.

| Campo | Tipo | Regras |
|---|---|---|
| `object_id` | texto | Nome lógico, por exemplo `LivroService` |
| `host` | texto | Endereço alcançável pelo Cliente/Broker |
| `port` | inteiro | Porta TCP válida |
| `node_id` | texto | Identificador do nó servidor |

O Registry mantém múltiplas localizações para o mesmo `object_id` e escolhe a
próxima por round-robin. O registro é operacional e fica em memória; não é uma
entidade de domínio persistida.

## Requisição remota

| Campo | Tipo | Regras |
|---|---|---|
| `request_id` | UUID v4 | Obrigatório e correlaciona resposta e logs |
| `timestamp` | timestamp ISO8601 | Obrigatório |
| `object_id` | texto | Deve identificar objeto registrado |
| `method` | texto | Deve ser exposto pelo Skeleton |
| `args` | lista JSON | Argumentos posicionais, padrão lista vazia |
| `kwargs` | objeto JSON | Argumentos nomeados, padrão objeto vazio |
| `auth_token` | texto ou nulo | JWT exigido para métodos protegidos |

## Resposta remota

| Campo | Tipo | Regras |
|---|---|---|
| `request_id` | UUID v4 | Deve corresponder à requisição |
| `timestamp` | timestamp ISO8601 | Obrigatório |
| `status` | `OK` ou `ERROR` | Obrigatório |
| `result` | JSON ou nulo | Preenchido em sucesso |
| `error` | objeto ou nulo | Em erro contém `code` e `message` |

## Relações e invariantes

- Um `Usuario` pode possuir zero ou muitos `Emprestimo`.
- Um `Livro` pode aparecer em zero ou muitos `Emprestimo` ao longo do tempo.
- Um `Emprestimo` referencia exatamente um `Usuario` e um `Livro`.
- Um empréstimo bem-sucedido cria uma transação que decrementa uma cópia e cria
  o registro `ativo` de forma atômica.
- Uma devolução válida muda `ativo` para `devolvido` e incrementa uma cópia uma
  única vez, também de forma atômica.
- O estoque nunca pode ficar negativo.
- Uma devolução repetida não pode alterar o estoque.
- Métodos protegidos só podem executar após validação JWT no Broker.

## Transições de estado

```text
Emprestimo: (ausente) --emprestar com cópia--> ativo
Emprestimo: ativo --devolver--> devolvido
Emprestimo: devolvido --devolver novamente--> erro de negócio
```
