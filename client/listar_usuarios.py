"""Script para listar todos os usuários cadastrados na Biblioteca Digital via Middleware ORB."""

from __future__ import annotations

import asyncio
import os
import sys

# Permite executar o script diretamente ou como módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orb_core.exceptions import ORBError
from orb_core.registry import RegistryClient
from orb_core.stub import Stub


async def main() -> None:
    registry_host = os.getenv("REGISTRY_HOST", "127.0.0.1")
    registry_port = int(os.getenv("REGISTRY_PORT", "8765"))
    registry = RegistryClient(registry_host, registry_port)

    usuario_stub = Stub("UsuarioService", registry=registry)

    print("\n" + "=" * 65)
    print(" 📋 CONSULTA DE USUÁRIOS CADASTRADOS - MIDDLEWARE ORB")
    print("=" * 65)
    print(f"Conectando ao Registry em {registry_host}:{registry_port}...")

    try:
        # Autentica com as credenciais padrão do sistema (seed)
        email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
        senha = os.getenv("ADMIN_PASSWORD", "admin")
        
        token = await usuario_stub.invoke_async("autenticar", email, senha)
        print("✅ Autenticação realizada com sucesso!")

        # Invoca o método remoto listarUsuarios
        usuarios = await usuario_stub.invoke_async("listarUsuarios", auth_token=token)

        print("\n" + "-" * 65)
        print(f" Total de Usuários Encontrados: {len(usuarios)}")
        print("-" * 65)
        
        for index, user in enumerate(usuarios, start=1):
            print(f" {index}. ID: {user['id']}")
            print(f"    Nome:   {user['nome']}")
            print(f"    Email:  {user['email']}")
            print(f"    Status: {user['status'].upper()}")
            print("    " + "-" * 40)
            
    except ORBError as exc:
        print(f"\n❌ Falha na invocação remota [{exc.code}]: {exc.message}")
    except Exception as exc:
        print(f"\n❌ Erro inesperado: {exc}")

    print("=" * 65 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
