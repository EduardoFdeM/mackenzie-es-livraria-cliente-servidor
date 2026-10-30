"""Serviço de Livros e Estoques."""

from typing import Any, Optional
from backend.domain.exceptions import LivroNaoEncontradoError
from backend.repositories.catalogo_repo import CatalogoRepository
from backend.repositories.estoque_repo import EstoqueRepository


class LivrariaService:
    def __init__(
        self,
        catalogo_repo: Optional[CatalogoRepository] = None,
        estoque_repo: Optional[EstoqueRepository] = None,
    ) -> None:
        self.catalogo_repo = catalogo_repo or CatalogoRepository()
        self.estoque_repo = estoque_repo or EstoqueRepository()

    def listar_livros(self, termo: Optional[str] = None) -> list[dict[str, Any]]:
        if termo:
            livros = self.catalogo_repo.buscar_por_termo(termo)
        else:
            livros = self.catalogo_repo.listar_todos()

        resultado = []
        for livro in livros:
            estoques = self.estoque_repo.listar_por_isbn(livro.isbn)
            total = sum(e.quantidade for e in estoques)
            item = livro.to_dict()
            item["total_exemplares"] = total
            item["estoques"] = [e.to_dict() for e in estoques]
            resultado.append(item)
        return resultado

    def obter_livro(self, isbn: str) -> dict[str, Any]:
        livro = self.catalogo_repo.buscar_por_isbn(isbn)
        if not livro:
            raise LivroNaoEncontradoError(f"Livro com ISBN {isbn} não encontrado.")

        estoques = self.estoque_repo.listar_por_isbn(isbn)
        total = sum(e.quantidade for e in estoques)
        item = livro.to_dict()
        item["total_exemplares"] = total
        item["estoques"] = [e.to_dict() for e in estoques]
        return item

    def obter_estoques(self, isbn: str) -> list[dict[str, Any]]:
        if not self.catalogo_repo.buscar_por_isbn(isbn):
            raise LivroNaoEncontradoError(f"Livro com ISBN {isbn} não encontrado.")
        estoques = self.estoque_repo.listar_por_isbn(isbn)
        return [e.to_dict() for e in estoques]
