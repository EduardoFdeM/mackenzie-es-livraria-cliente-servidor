"""Repositório de Estoque Físico por Filial."""

from typing import Optional
from backend.domain.models import EstoqueUnidade


class EstoqueRepository:
    def __init__(self) -> None:
        self._estoques: dict[tuple[str, str], EstoqueUnidade] = {}
        self._popular_dados()

    def _popular_dados(self) -> None:
        dados = [
            # 1. Clean Code
            EstoqueUnidade("Higienópolis", "9780132350884", 3, "Tecnologia", "4", "B"),
            EstoqueUnidade("Paulista", "9780132350884", 1, "Informática", "1", "A"),
            EstoqueUnidade("Pinheiros", "9780132350884", 0, "Geral", "2", "C"),

            # 2. Arquitetura Limpa
            EstoqueUnidade("Higienópolis", "9788550804606", 3, "Tecnologia", "4", "C"),
            EstoqueUnidade("Paulista", "9788550804606", 2, "Informática", "1", "B"),

            # 3. O Programador Pragmático
            EstoqueUnidade("Higienópolis", "9788577807000", 4, "Tecnologia", "5", "A"),
            EstoqueUnidade("Pinheiros", "9788577807000", 2, "Geral", "3", "D"),

            # 4. Engenharia de Software Moderna
            EstoqueUnidade("Paulista", "9786500019506", 6, "Informática", "2", "E"),
            EstoqueUnidade("Higienópolis", "9786500019506", 3, "Tecnologia", "4", "D"),

            # 5. Padrões de Projeto (GoF)
            EstoqueUnidade("Higienópolis", "9788573076103", 4, "Tecnologia", "3", "A"),
            EstoqueUnidade("Paulista", "9788573076103", 1, "Informática", "1", "C"),

            # 6. Domain-Driven Design
            EstoqueUnidade("Higienópolis", "9788550800653", 2, "Tecnologia", "5", "B"),
            EstoqueUnidade("Pinheiros", "9788550800653", 3, "Geral", "2", "A"),

            # 7. Refatoração
            EstoqueUnidade("Paulista", "9788575227244", 4, "Informática", "3", "A"),
            EstoqueUnidade("Higienópolis", "9788575227244", 2, "Tecnologia", "4", "A"),

            # 8. Microsserviços Prontos Para a Produção
            EstoqueUnidade("Higienópolis", "9788575225837", 5, "Tecnologia", "2", "C"),
            EstoqueUnidade("Paulista", "9788575225837", 3, "Informática", "2", "B"),

            # 9. Entendendo Algoritmos
            EstoqueUnidade("Higienópolis", "9788575225639", 7, "Tecnologia", "1", "A"),
            EstoqueUnidade("Pinheiros", "9788575225639", 4, "Geral", "1", "B"),

            # 10. Python Fluente
            EstoqueUnidade("Higienópolis", "9788575224625", 3, "Tecnologia", "5", "D"),
            EstoqueUnidade("Paulista", "9788575224625", 2, "Informática", "4", "A"),
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
