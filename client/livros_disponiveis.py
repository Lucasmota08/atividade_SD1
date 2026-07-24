"""Script para listar todos os livros disponíveis na biblioteca."""

from __future__ import annotations

import asyncio
import os

from orb_core.exceptions import ORBError
from orb_core.registry import RegistryClient
from orb_core.stub import Stub


async def listar_livros_disponiveis() -> None:
    """Obtém e exibe os livros com cópias disponíveis."""
    host = os.getenv("REGISTRY_HOST", "127.0.0.1")
    port = int(os.getenv("REGISTRY_PORT", "8765"))
    
    print(f"Conectando ao Registry em {host}:{port}...")
    registry = RegistryClient(host, port)
    usuario = Stub("UsuarioService", registry=registry)
    livros = Stub("LivroService", registry=registry)
    
    try:
        # Autenticação
        print("Autenticando...")
        token = await usuario.invoke_async("autenticar", "ana@example.com", "senha123")
        print("Autenticado com sucesso!")
        
        # Obter catálogo de livros
        print("Buscando catálogo de livros...")
        catalog = await livros.invoke_async("listarLivros", auth_token=token)
        
        # Filtrar livros disponíveis (copias_disponiveis > 0)
        livros_disponiveis = [livro for livro in catalog if livro.get("copias_disponiveis", 0) > 0]
        
        print("\n=== LIVROS DISPONÍVEIS NA BIBLIOTECA ===")
        if not livros_disponiveis:
            print("Nenhum livro disponível no momento.")
        else:
            for livro in livros_disponiveis:
                print(f"ID: {livro['id']}")
                print(f"Título: {livro['titulo']}")
                print(f"Autor: {livro['autor']}")
                print(f"ISBN: {livro['isbn']}")
                print(f"Cópias Disponíveis: {livro['copias_disponiveis']}")
                print("-" * 40)
        print(f"Total de livros disponíveis: {len(livros_disponiveis)}")
        
    except ORBError as exc:
        print(f"\nErro no protocolo ORB [{exc.code}]: {exc.message}")
    except Exception as exc:
        print(f"\nErro inesperado: {exc}")


if __name__ == "__main__":
    asyncio.run(listar_livros_disponiveis())
