"""Script utilitário para resetar o banco de dados SQLite local e recarregar o seed inicial."""

from __future__ import annotations

import os
from pathlib import Path

from database.connection import get_connection
from database.seed import seed_database


def reset_local_databases() -> None:
    """Remove os arquivos de banco de dados SQLite e recria o banco limpo com seed."""
    root_dir = Path(__file__).resolve().parent.parent
    db_files = list(root_dir.glob("*.db"))

    print("\n" + "=" * 60)
    print(" RESET DO BANCO DE DADOS LOCAL - MIDDLEWARE ORB")
    print("=" * 60)

    if not db_files:
        print("Nenhum arquivo .db local encontrado para remover.")
    else:
        for db in db_files:
            try:
                os.remove(db)
                print(f"   Arquivo removido: {db.name}")
            except Exception as exc:
                print(f"   Erro ao remover {db.name}: {exc}")

    target_db = str(root_dir / "biblioteca.db")
    print(f"\nRecriando banco de dados limpo com a carga inicial em: biblioteca.db...")
    
    # Recria o banco e aplica o seed inicial
    seed_database(target_db)
    
    print("\n[OK] Banco de dados resetado com sucesso!")
    print("   - Emprestimos: 0")
    print("   - Usuarios extras: Removidos (Restaurados apenas admin@gmail.com e bruno@example.com)")
    print("   - Livros: 4 titulos padrao restaurados com estoque completo.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    reset_local_databases()
