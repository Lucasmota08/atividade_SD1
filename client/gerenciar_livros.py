"""Script interativo para gerenciar (adicionar e excluir) livros na biblioteca."""

from __future__ import annotations

import asyncio
import os
import sys

from orb_core.exceptions import ORBError
from orb_core.registry import RegistryClient
from orb_core.stub import Stub


async def main() -> None:
    host = os.getenv("REGISTRY_HOST", "127.0.0.1")
    port = int(os.getenv("REGISTRY_PORT", "8765"))
    
    print(f"Conectando ao Registry em {host}:{port}...")
    registry = RegistryClient(host, port)
    usuario = Stub("UsuarioService", registry=registry)
    livros = Stub("LivroService", registry=registry)
    
    try:
        print("Autenticando...")
        token = await usuario.invoke_async("autenticar", "ana@example.com", "senha123")
        print("Autenticado com sucesso!\n")
    except ORBError as exc:
        print(f"Erro ao autenticar [{exc.code}]: {exc.message}")
        return
    except Exception as exc:
        print(f"Erro inesperado de conexão: {exc}")
        return

    while True:
        print("\n=== GERENCIAMENTO DE LIVROS ===")
        print("1. Listar livros cadastrados")
        print("2. Adicionar novo livro")
        print("3. Excluir um livro")
        print("4. Sair")
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            try:
                catalog = await livros.invoke_async("listarLivros", auth_token=token)
                print("\n--- CATÁLOGO DE LIVROS ---")
                if not catalog:
                    print("Nenhum livro cadastrado.")
                else:
                    for livro in catalog:
                        print(f"ID: {livro['id']} | Título: {livro['titulo']} | Autor: {livro['autor']} | ISBN: {livro['isbn']} | Cópias: {livro['copias_disponiveis']}")
            except ORBError as exc:
                print(f"Erro ao obter catálogo [{exc.code}]: {exc.message}")
                
        elif opcao == "2":
            print("\n--- ADICIONAR NOVO LIVRO ---")
            livro_id = input("ID do livro (ex: livro-006): ").strip()
            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            isbn = input("ISBN (único): ").strip()
            try:
                copias = int(input("Quantidade de cópias: ").strip())
            except ValueError:
                print("Quantidade de cópias deve ser um número inteiro!")
                continue
                
            if not (livro_id and titulo and autor and isbn):
                print("Todos os campos de texto são obrigatórios!")
                continue
                
            try:
                res = await livros.invoke_async("adicionarLivro", livro_id, titulo, autor, isbn, copias, auth_token=token)
                print(f"\nSucesso: Livro '{titulo}' (ID: {res['id']}) adicionado com sucesso!")
            except ORBError as exc:
                print(f"\nErro ao adicionar livro [{exc.code}]: {exc.message}")
                
        elif opcao == "3":
            print("\n--- EXCLUIR LIVRO ---")
            livro_id = input("Digite o ID do livro a ser excluído (ex: livro-006): ").strip()
            if not livro_id:
                print("ID é obrigatório!")
                continue
            
            confirmar = input(f"Tem certeza que deseja excluir o livro '{livro_id}'? (s/n): ").strip().lower()
            if confirmar != "s":
                print("Operação cancelada.")
                continue
                
            try:
                res = await livros.invoke_async("excluirLivro", livro_id, auth_token=token)
                print(f"\nSucesso: {res['message']}")
            except ORBError as exc:
                print(f"\nErro ao excluir livro [{exc.code}]: {exc.message}")
                
        elif opcao == "4":
            print("Saindo do gerenciador de livros. Até logo!")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    # Permite rodar o loop assíncrono interativamente
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecução encerrada pelo usuário.")
