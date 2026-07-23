from domain.livro_service import LivroService


def test_listing_returns_catalog_without_sensitive_fields(database_path):
    books = LivroService(database_path).listarLivros()
    assert len(books) == 5
    assert all("senha_hash" not in book for book in books)
    assert [book["id"] for book in books] == sorted(book["id"] for book in books)
