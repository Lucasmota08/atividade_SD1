"""CLI Interativo para a Biblioteca Digital Distribuída (Middleware ORB)."""

from __future__ import annotations

import asyncio
import os
import sys

from orb_core.exceptions import ORBError
from orb_core.registry import RegistryClient
from orb_core.stub import Stub


async def main() -> None:
    registry_host = os.getenv("REGISTRY_HOST", "127.0.0.1")
    registry_port = int(os.getenv("REGISTRY_PORT", "8765"))
    registry = RegistryClient(registry_host, registry_port)

    usuario_stub = Stub("UsuarioService", registry=registry)
    livro_stub = Stub("LivroService", registry=registry)
    emprestimo_stub = Stub("EmprestimoService", registry=registry)

    token: str | None = None
    usuario_id: str | None = None

    print("\n" + "=" * 60)
    print("  📚 BIBLIOTECA DIGITAL DISTRIBUÍDA - MIDDLEWARE ORB")
    print("=" * 60)
    print(f"Conectando ao Registry em {registry_host}:{registry_port}...\n")

    while True:
        status_str = f"Autenticado (User: {usuario_id})" if token else "Não Autenticado"
        print("\n" + "-" * 60)
        print(f"Status Atual: [{status_str}]")
        print("-" * 60)
        print("1. Autenticar (Login)")
        print("2. Cadastrar Novo Usuário")
        print("3. Listar Todos os Livros")
        print("4. Consultar Disponibilidade de um Livro")
        print("5. Realizar Empréstimo de Livro")
        print("6. Listar Meus Empréstimos Ativos")
        print("7. Devolver Livro")
        print("8. Sair")
        print("-" * 60)

        try:
            opcao = input("Escolha uma opção (1-8): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando cliente.")
            break

        if opcao == "1":
            email = input("Digite o email: ").strip()
            senha = input("Digite a senha: ").strip()
            try:
                token = await usuario_stub.invoke_async("autenticar", email, senha)
                usuario_id = "usuario-001" if ("admin" in email or "ana" in email) else "usuario-002"
                print(f"\n✅ Login realizado com sucesso!")
                print(f"Token JWT obtido: {token[:30]}...")
            except ORBError as exc:
                print(f"\n❌ Erro na autenticação [{exc.code}]: {exc.message}")

        elif opcao == "2":
            if not token:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            nome = input("Nome completo: ").strip()
            email = input("Email: ").strip()
            senha = input("Senha: ").strip()
            try:
                res = await usuario_stub.invoke_async("cadastrarUsuario", nome, email, senha, auth_token=token)
                print(f"\n✅ Usuário cadastrado com sucesso! ID: {res.get('id')}")
            except ORBError as exc:
                print(f"\n❌ Erro no cadastro [{exc.code}]: {exc.message}")

        elif opcao == "3":
            if not token:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            try:
                livros = await livro_stub.invoke_async("listarLivros", auth_token=token)
                print(f"\n📚 Catálogo de Livros ({len(livros)} disponíveis):")
                for item in livros:
                    print(f"  • ID: {item['id']} | Título: {item['titulo']} | Autor: {item['autor']} | Cópias: {item['copias_disponiveis']}")
            except ORBError as exc:
                print(f"\n❌ Erro ao listar livros [{exc.code}]: {exc.message}")

        elif opcao == "4":
            if not token:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            livro_id = input("Digite o ID do livro (ex: livro-001): ").strip()
            try:
                disp = await livro_stub.invoke_async("consultarDisponibilidade", livro_id, auth_token=token)
                status = "DISPONÍVEL" if disp.get("disponivel") else "INDISPONÍVEL"
                print(f"\n📖 Livro '{livro_id}': Status = {status} | Cópias restantes: {disp.get('copias')}")
            except ORBError as exc:
                print(f"\n❌ Erro ao consultar disponibilidade [{exc.code}]: {exc.message}")

        elif opcao == "5":
            if not token:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            uid = input(f"ID do Usuário [{usuario_id or 'usuario-001'}]: ").strip() or (usuario_id or "usuario-001")
            livro_id = input("ID do Livro a emprestar (ex: livro-001): ").strip()
            try:
                loan = await emprestimo_stub.invoke_async("emprestarLivro", uid, livro_id, auth_token=token)
                print(f"\n✅ Empréstimo realizado com sucesso!")
                print(f"   ID Empréstimo: {loan['id']}")
                print(f"   Devolução prevista: {loan['data_devolucao_prevista']}")
            except ORBError as exc:
                print(f"\n❌ Erro ao emprestar livro [{exc.code}]: {exc.message}")

        elif opcao == "6":
            if not token:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            uid = input(f"ID do Usuário [{usuario_id or 'usuario-001'}]: ").strip() or (usuario_id or "usuario-001")
            try:
                loans = await emprestimo_stub.invoke_async("listarEmprestimosAtivos", uid, auth_token=token)
                print(f"\n📋 Empréstimos Ativos do usuário {uid} ({len(loans)}):")
                for l in loans:
                    print(f"  • ID Empréstimo: {l['id']} | Livro ID: {l['livro_id']} | Devolução em: {l['data_devolucao_prevista']}")
            except ORBError as exc:
                print(f"\n❌ Erro ao listar empréstimos [{exc.code}]: {exc.message}")

        elif opcao == "7":
            if not token:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            loan_id = input("Digite o ID do Empréstimo a devolver: ").strip()
            try:
                res = await emprestimo_stub.invoke_async("devolverLivro", loan_id, auth_token=token)
                print(f"\n✅ Livro devolvido com sucesso! Status: {res.get('status')}")
            except ORBError as exc:
                print(f"\n❌ Erro ao devolver livro [{exc.code}]: {exc.message}")

        elif opcao == "8":
            print("\nEncerrando cliente da Biblioteca Digital. Até logo!\n")
            break
        else:
            print("\nOpção inválida, por favor tente novamente.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCliente encerrado.")
