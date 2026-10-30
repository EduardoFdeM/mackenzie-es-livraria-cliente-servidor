"""Pacote de repositórios."""
from .catalogo_repo import CatalogoRepository
from .estoque_repo import EstoqueRepository
from .reserva_repo import ReservaRepository

__all__ = ["CatalogoRepository", "EstoqueRepository", "ReservaRepository"]
