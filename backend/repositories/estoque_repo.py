"""Repositório de Estoque Físico por Filial."""

from typing import Optional
from backend.domain.models import EstoqueUnidade


class EstoqueRepository:
    def __init__(self) -> None:
        self._estoques: dict[tuple[str, str], EstoqueUnidade] = {}
        self._popular_dados()

    def _popular_dados(self) -> None:
        dados = [
            EstoqueUnidade("Higienópolis", "9780132350884", 3, "Tecnologia", "4", "B"),
            EstoqueUnidade("Paulista", "9780132350884", 1, "Informática", "1", "A"),
            EstoqueUnidade("Pinheiros", "9780132350884", 0, "Geral", "2", "C"),

            EstoqueUnidade("Higienópolis", "9788550804606", 2, "Tecnologia", "4", "C"),
            EstoqueUnidade("Paulista", "9788550804606", 0, "Informática", "1", "B"),

            EstoqueUnidade("Higienópolis", "9788577807000", 4, "Tecnologia", "5", "A"),
            EstoqueUnidade("Pinheiros", "9788577807000", 2, "Geral", "3", "D"),

            EstoqueUnidade("Paulista", "9786500019506", 5, "Informática", "2", "E"),
            EstoqueUnidade("Higienópolis", "9786500019506", 1, "Tecnologia", "4", "D"),
        ]
        for item in dados:
            self.salvar(item)

    def salvar(self, estoque: EstoqueUnidade) -> None:
        self._estoques[(estoque.isbn, estoque.unidade)] = estoque

    def obter(self, isbn: str, unidade: str) -> Optional[EstoqueUnidade]:
        return self._estoques.get((isbn, unidade))

    def listar_por_isbn(self, isbn: str) -> list[EstoqueUnidade]:
        return [
            item for (book_isbn, _), item in self._estoques.items()
            if book_isbn == isbn
        ]
