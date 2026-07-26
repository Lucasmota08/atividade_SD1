"""CLI Interativo para a Biblioteca Digital Distribuída (Middleware ORB)."""

from __future__ import annotations

import asyncio
from datetime import datetime
import os
import sys

from orb_core.exceptions import ORBError
from orb_core.registry import RegistryClient
from orb_core.stub import Stub


def format_date(iso_str: str | None) -> str:
    """Format de datas ISO8601 em exibição amigável para o usuário (ex: DD/MM/AAAA às HH:MM)."""
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(str(iso_str).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        return str(iso_str).split(".")[0].replace("T", " ")


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
        status_str = f"Autenticado como [{usuario_id}]" if token else "Não Autenticado"
        print("\n" + "-" * 60)
        print(f"Status Atual: {status_str}")
        print("-" * 60)

        if not token:
            print("1. Autenticar / Criar Nova Conta")
        else:
            print("1. Desconectar (Sair da Conta)")

        print("2. Listar Todos os Livros")
        print("3. Consultar Disponibilidade de um Livro")
        print("4. Realizar Empréstimo de Livro")
        print("5. Listar Meus Empréstimos Ativos")
        print("6. Devolver Livro")
        print("7. Sair")
        print("-" * 60)

        try:
            opcao = input("Escolha uma opção (1-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando cliente.")
            break

        if opcao == "1":
            if token:
                print(f"\n✅ Usuário [{usuario_id}] desconectado com sucesso.")
                token = None
                usuario_id = None
                continue

            print("\n--- AUTENTICAÇÃO / NOVO CADASTRO ---")
            print("1. Fazer Login (Autenticar)")
            print("2. Criar Nova Conta (Cadastrar Usuário)")
            print("3. Voltar")
            sub_op = input("Escolha uma opção (1-3): ").strip()

            if sub_op == "1":
                email = input("Email: ").strip()
                senha = input("Senha: ").strip()
                try:
                    auth_res = await usuario_stub.invoke_async("autenticar", email, senha)
                    if isinstance(auth_res, dict):
                        token = auth_res.get("token")
                        usuario_id = auth_res.get("usuario_id")
                    else:
                        token = auth_res
                        usuario_id = ""
                    print(f"\n✅ Login realizado com sucesso!")
                    print(f"   ID do Usuário: {usuario_id}")
                    print(f"   Token JWT obtido: {str(token)[:30]}...")
                except ORBError as exc:
                    print(f"\n❌ Erro na autenticação [{exc.code}]: {exc.message}")

            elif sub_op == "2":
                nome = input("Nome completo: ").strip()
                email = input("Email: ").strip()
                senha = input("Senha: ").strip()
                try:
                    res = await usuario_stub.invoke_async("cadastrarUsuario", nome, email, senha)
                    new_id = res.get("id")
                    print(f"\n✅ Usuário cadastrado com sucesso!")
                    print(f"   SEU ID DE USUÁRIO É: {new_id}")
                    # Inicia a sessão automaticamente com a conta criada
                    try:
                        auth_res = await usuario_stub.invoke_async("autenticar", email, senha)
                        if isinstance(auth_res, dict):
                            token = auth_res.get("token")
                            usuario_id = auth_res.get("usuario_id", new_id)
                        else:
                            token = auth_res
                            usuario_id = new_id
                        print(f"   ✅ Sessão iniciada automaticamente como [{usuario_id}]!")
                    except Exception:
                        pass
                except ORBError as exc:
                    print(f"\n❌ Erro no cadastro [{exc.code}]: {exc.message}")

        elif opcao == "2":
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

        elif opcao == "3":
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

        elif opcao == "4":
            if not token or not usuario_id:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            print(f"\n📖 Emprestando livro para sua conta [{usuario_id}]...")
            livro_id = input("Digite o ID do Livro (ex: livro-001): ").strip()
            try:
                loan = await emprestimo_stub.invoke_async("emprestarLivro", usuario_id, livro_id, auth_token=token)
                data_formatada = format_date(loan.get("data_devolucao_prevista"))
                print(f"\n✅ Empréstimo realizado com sucesso!")
                print(f"   ID do Empréstimo: {loan['id']}")
                print(f"   Devolução prevista: {data_formatada}")
            except ORBError as exc:
                print(f"\n❌ Erro ao emprestar livro [{exc.code}]: {exc.message}")

        elif opcao == "5":
            if not token or not usuario_id:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            try:
                loans = await emprestimo_stub.invoke_async("listarEmprestimosAtivos", usuario_id, auth_token=token)
                print(f"\n📋 Meus Empréstimos Ativos ({len(loans)}):")
                for l in loans:
                    data_formatada = format_date(l.get("data_devolucao_prevista"))
                    print(f"  • ID Empréstimo: {l['id']} | Livro ID: {l['livro_id']} | Devolução em: {data_formatada}")
            except ORBError as exc:
                print(f"\n❌ Erro ao listar empréstimos [{exc.code}]: {exc.message}")

        elif opcao == "6":
            if not token or not usuario_id:
                print("\n⚠️ Você precisa se autenticar primeiro (Opção 1).")
                continue
            loan_id = input("Digite o ID do Empréstimo a devolver: ").strip()
            try:
                res = await emprestimo_stub.invoke_async("devolverLivro", loan_id, usuario_id=usuario_id, auth_token=token)
                print(f"\n✅ Livro devolvido com sucesso! Status: {res.get('status')}")
            except ORBError as exc:
                print(f"\n❌ Erro ao devolver livro [{exc.code}]: {exc.message}")

        elif opcao == "7":
            print("\nEncerrando cliente da Biblioteca Digital. Até logo!\n")
            break
        else:
            print("\nOpção inválida, por favor tente novamente.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCliente encerrado.")
