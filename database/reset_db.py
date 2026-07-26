"""Script utilitário para resetar o banco de dados SQLite local e recarregar o seed inicial."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from database.connection import get_connection
from database.seed import seed_database


def reset_local_databases() -> None:
    """Remove os arquivos de banco de dados SQLite (incluindo WAL/SHM) e recria o banco limpo com seed."""
    root_dir = Path(__file__).resolve().parent.parent
    db_files = [f for f in root_dir.glob("*.db*") if f.is_file()]

    print("\n" + "=" * 60)
    print(" RESET DO BANCO DE DADOS LOCAL E DOCKER - MIDDLEWARE ORB")
    print("=" * 60)

    if not db_files:
        print("Nenhum arquivo .db local encontrado para remover.")
    else:
        for db in db_files:
            try:
                os.remove(db)
                print(f"   [Host] Arquivo removido: {db.name}")
            except Exception as exc:
                print(f"   [Host] Erro/Bloqueio ao remover {db.name}: {exc}")

    target_db = str(root_dir / "biblioteca.db")
    print(f"\nRecriando banco de dados local limpo em: biblioteca.db...")
    seed_database(target_db)

    # Verifica e limpa volumes do Docker Compose se estiver ativo
    try:
        res = subprocess.run(["docker", "compose", "ps", "-q"], cwd=root_dir, capture_output=True, text=True)
        if res.stdout.strip():
            print("\n[Docker] Containers em execucao detectados. Resetando volume Docker (node1-data)...")
            subprocess.run(["docker", "compose", "down", "-v"], cwd=root_dir, check=True)
            subprocess.run(["docker", "compose", "up", "-d"], cwd=root_dir, check=True)
            print("   [Docker] Volume resetado e containers reiniciados com sucesso!")
    except Exception as exc:
        print("   Nota sobre Docker: Se estiver usando Docker Compose, rode: docker compose down -v && docker compose up -d")

    print("\n[OK] Banco de dados resetado com sucesso!")
    print("   - Emprestimos: 0")
    print("   - Usuarios extras: Removidos (Restaurados apenas admin@gmail.com e bruno@example.com)")
    print("   - Livros: 4 titulos padrao restaurados com estoque completo.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    reset_local_databases()
