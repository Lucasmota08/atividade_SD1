"""Cliente de console para a narrativa de demonstração."""

from __future__ import annotations

import asyncio
import os

from orb_core.exceptions import ORBError
from orb_core.registry import RegistryClient
from orb_core.stub import Stub


async def run_demo() -> None:
    """Executa autenticação, catálogo, empréstimo e devolução."""
    registry = RegistryClient(os.getenv("REGISTRY_HOST", "127.0.0.1"), int(os.getenv("REGISTRY_PORT", "8765")))
    usuario = Stub("UsuarioService", registry=registry)
    livros = Stub("LivroService", registry=registry)
    emprestimos = Stub("EmprestimoService", registry=registry)
    try:
        token = await usuario.invoke_async("autenticar", "admin@gmail.com", "admin")
        print("Autenticado com sucesso")
        catalog = await livros.invoke_async("listarLivros", auth_token=token)
        print(f"Livros encontrados: {len(catalog)}")
        book_id = catalog[0]["id"]
        print(await livros.invoke_async("consultarDisponibilidade", book_id, auth_token=token))
        loan = await emprestimos.invoke_async("emprestarLivro", "usuario-001", book_id, auth_token=token)
        print(f"Empréstimo criado: {loan['id']}")
        print(await emprestimos.invoke_async("listarEmprestimosAtivos", "usuario-001", auth_token=token))
        print(await emprestimos.invoke_async("devolverLivro", loan["id"], auth_token=token))
    except ORBError as exc:
        print(f"Falha tratada [{exc.code}]: {exc.message}")


if __name__ == "__main__":
    asyncio.run(run_demo())
