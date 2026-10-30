"""Modelos de domínio serializáveis em JSON para a API REST."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any
from .exceptions import EstoqueInsuficienteError, ReservaJaCanceladaError


class StatusReserva(str, Enum):
    ATIVA = "Ativa"
    CANCELADA = "Cancelada"


@dataclass
class EstoqueUnidade:
    unidade: str
    isbn: str
    quantidade: int
    setor: str = ""
    corredor: str = ""
    prateleira: str = ""

    def decrementar(self) -> None:
        if self.quantidade <= 0:
            raise EstoqueInsuficienteError(f"Estoque esgotado na unidade {self.unidade}.")
        self.quantidade -= 1

    def incrementar(self) -> None:
        self.quantidade += 1

    @property
    def localizacao_formatada(self) -> str:
        if self.setor and self.corredor and self.prateleira:
            return f"Setor {self.setor}, corredor {self.corredor}, prateleira {self.prateleira}"
        return "Consulte o balcão da unidade"

    def to_dict(self) -> dict[str, Any]:
        return {
            "unidade": self.unidade,
            "isbn": self.isbn,
            "quantidade": self.quantidade,
            "setor": self.setor,
            "corredor": self.corredor,
            "prateleira": self.prateleira,
            "localizacao_formatada": self.localizacao_formatada,
            "disponivel": self.quantidade > 0,
        }


@dataclass
class Livro:
    isbn: str
    titulo: str
    autor: str
    preco: Decimal

    @property
    def preco_formatado(self) -> str:
        return f"R$ {self.preco:.2f}".replace(".", ",")

    def to_dict(self) -> dict[str, Any]:
        return {
            "isbn": self.isbn,
            "titulo": self.titulo,
            "autor": self.autor,
            "preco": float(self.preco),
            "preco_formatado": self.preco_formatado,
        }


@dataclass
class Reserva:
    codigo: str
    isbn: str
    titulo: str
    unidade: str
    status: StatusReserva = StatusReserva.ATIVA

    def cancelar(self) -> None:
        if self.status == StatusReserva.CANCELADA:
            raise ReservaJaCanceladaError(f"A reserva {self.codigo} já foi cancelada.")
        self.status = StatusReserva.CANCELADA

    def to_dict(self) -> dict[str, Any]:
        return {
            "codigo": self.codigo,
            "isbn": self.isbn,
            "titulo": self.titulo,
            "unidade": self.unidade,
            "status": self.status.value,
        }
