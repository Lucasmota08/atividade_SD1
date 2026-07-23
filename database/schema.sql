PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS livro (
    id TEXT PRIMARY KEY,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    isbn TEXT NOT NULL UNIQUE,
    copias_disponiveis INTEGER NOT NULL CHECK (copias_disponiveis >= 0)
);

CREATE TABLE IF NOT EXISTS usuario (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ativo', 'bloqueado'))
);

CREATE TABLE IF NOT EXISTS emprestimo (
    id TEXT PRIMARY KEY,
    livro_id TEXT NOT NULL REFERENCES livro(id),
    usuario_id TEXT NOT NULL REFERENCES usuario(id),
    data_emprestimo TEXT NOT NULL,
    data_devolucao_prevista TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ativo', 'devolvido'))
);

CREATE INDEX IF NOT EXISTS idx_emprestimo_usuario_status
    ON emprestimo(usuario_id, status);
