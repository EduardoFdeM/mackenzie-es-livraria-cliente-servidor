"""Serviço de Reservas."""

from typing import Any, Optional
from backend.domain.exceptions import (
    DadosInvalidosError,
    EstoqueInsuficienteError,
    LivroNaoEncontradoError,
    ReservaNaoEncontradaError,
)
from backend.domain.models import Reserva, StatusReserva
from backend.repositories.catalogo_repo import CatalogoRepository
from backend.repositories.estoque_repo import EstoqueRepository
from backend.repositories.reserva_repo import ReservaRepository


class ReservaService:
    def __init__(
        self,
        reserva_repo: Optional[ReservaRepository] = None,
        catalogo_repo: Optional[CatalogoRepository] = None,
        estoque_repo: Optional[EstoqueRepository] = None,
    ) -> None:
        self.reserva_repo = reserva_repo or ReservaRepository()
        self.catalogo_repo = catalogo_repo or CatalogoRepository()
        self.estoque_repo = estoque_repo or EstoqueRepository()

    def criar_reserva(self, isbn: str, unidade: str) -> dict[str, Any]:
        if not isbn or not unidade:
            raise DadosInvalidosError("Campos 'isbn' e 'unidade' são obrigatórios.")

        livro = self.catalogo_repo.buscar_por_isbn(isbn)
        if not livro:
            raise LivroNaoEncontradoError(f"Livro com ISBN {isbn} não existe no catálogo.")

        estoque = self.estoque_repo.obter(isbn, unidade)
        if not estoque or estoque.quantidade <= 0:
            raise EstoqueInsuficienteError(f"Não há exemplares disponíveis na unidade {unidade}.")

        estoque.decrementar()
        self.estoque_repo.salvar(estoque)

        codigo = self.reserva_repo.gerar_codigo()
        reserva = Reserva(
            codigo=codigo,
            isbn=livro.isbn,
            titulo=livro.titulo,
            unidade=unidade,
            status=StatusReserva.ATIVA,
        )
        self.reserva_repo.salvar(reserva)
        return reserva.to_dict()

    def cancelar_reserva(self, codigo: str) -> dict[str, Any]:
        reserva = self.reserva_repo.buscar_por_codigo(codigo)
        if not reserva:
            raise ReservaNaoEncontradaError(f"Reserva {codigo} não encontrada.")

        reserva.cancelar()

        # Devolução de saldo ao estoque físico da unidade
        estoque = self.estoque_repo.obter(reserva.isbn, reserva.unidade)
        if estoque:
            estoque.incrementar()
            self.estoque_repo.salvar(estoque)

        self.reserva_repo.salvar(reserva)
        return reserva.to_dict()

    def listar_reservas(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.reserva_repo.listar_todas()]

    def obter_reserva(self, codigo: str) -> dict[str, Any]:
        reserva = self.reserva_repo.buscar_por_codigo(codigo)
        if not reserva:
            raise ReservaNaoEncontradaError(f"Reserva {codigo} não encontrada.")
        return reserva.to_dict()
