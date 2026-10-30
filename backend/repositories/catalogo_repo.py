"""Repositório de Livros e Catálogo."""

from decimal import Decimal
from typing import Optional
from backend.domain.models import Livro


class CatalogoRepository:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}
        self._popular_catalogo()

    def _popular_catalogo(self) -> None:
        exemplos = [
            Livro(
                isbn="9780132350884",
                titulo="Clean Code",
                autor="Robert C. Martin",
                preco=Decimal("89.90"),
            ),
            Livro(
                isbn="9788550804606",
                titulo="Arquitetura Limpa",
                autor="Robert C. Martin",
                preco=Decimal("94.50"),
            ),
            Livro(
                isbn="9788577807000",
                titulo="O Programador Pragmático",
                autor="Andrew Hunt e David Thomas",
                preco=Decimal("99.00"),
            ),
            Livro(
                isbn="9786500019506",
                titulo="Engenharia de Software Moderna",
                autor="Marco Tulio Valente",
                preco=Decimal("79.00"),
            ),
        ]
        for livro in exemplos:
            self.salvar(livro)

    def listar_todos(self) -> list[Livro]:
        return list(self._livros.values())

    def buscar_por_isbn(self, isbn: str) -> Optional[Livro]:
        return self._livros.get(isbn)

    def buscar_por_termo(self, termo: str) -> list[Livro]:
        termo_limpo = termo.strip().casefold()
        if not termo_limpo:
            return []
        return [
            livro for livro in self._livros.values()
            if termo_limpo in livro.titulo.casefold()
            or termo_limpo in livro.autor.casefold()
            or termo_limpo == livro.isbn.casefold()
        ]

    def salvar(self, livro: Livro) -> None:
        self._livros[livro.isbn] = livro
