"""Script para verificar a qual Nó (Node 1 ou Node 2) o cliente está conectado via Registry do ORB."""

from __future__ import annotations

import asyncio
import os
import sys

# Permite executar o script diretamente ou como módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orb_core.exceptions import ORBError
from orb_core.registry import RegistryClient


async def verificar_no() -> None:
    registry_host = os.getenv("REGISTRY_HOST", "127.0.0.1")
    registry_port = int(os.getenv("REGISTRY_PORT", "8765"))
    registry = RegistryClient(registry_host, registry_port)

    print("\n" + "=" * 65)
    print(" 📍 VERIFICAÇÃO DE CONEXÃO AO NÓ - MIDDLEWARE ORB")
    print("=" * 65)
    print(f"Consultando o Naming Service em {registry_host}:{registry_port}...")

    try:
        # Resolve o endpoint de um serviço de domínio no Registry
        endpoint = await registry.resolve("LivroService")
        
        node_display = endpoint.node_id.upper() if endpoint.node_id else "NÓ DESCONHECIDO"
        
        print("\n" + "🟢 CONEXÃO ESTABELECIDA COM SUCESSO!")
        print("-" * 65)
        print(f"  • Nó Conectado:  {node_display}")
        print(f"  • Host do Nó:    {endpoint.host}")
        print(f"  • Porta TCP:     {endpoint.port}")
        print(f"  • Objeto Remoto: {endpoint.object_id}")
        print("-" * 65)
        print(f"\n💡 Este processo está rodando em segundo plano e vinculado ao [{node_display}].")

    except ORBError as exc:
        print(f"\n❌ Não foi possível resolver o nó [{exc.code}]: {exc.message}")
        print(" Certifique-se de que o Registry e os Nós de Servidor estão em execução.")
    except Exception as exc:
        print(f"\n❌ Erro ao conectar ao Registry: {exc}")

    print("=" * 65)


def main() -> None:
    # Executa a verificação assíncrona do nó
    asyncio.run(verificar_no())
    
    # Mantém o script rodando no terminal aguardando input do usuário
    try:
        input("\n⌨️  Pressione [ENTER] no terminal a qualquer momento para encerrar... ")
        print("\nEncerrando conexão com o nó. Até logo!\n")
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrando script.\n")


if __name__ == "__main__":
    main()
