"""Exceções de domínio da Livraria Mackenzie (Backend REST API)."""


class LivrariaError(Exception):
    """Exceção base de regras de negócio."""
    status_code: int = 400

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class LivroNaoEncontradoError(LivrariaError):
    def __init__(self, message: str = "Livro não encontrado.") -> None:
        super().__init__(message, status_code=404)


class EstoqueInsuficienteError(LivrariaError):
    def __init__(self, message: str = "Estoque insuficiente para esta unidade.") -> None:
        super().__init__(message, status_code=409)


class ReservaNaoEncontradaError(LivrariaError):
    def __init__(self, message: str = "Reserva não encontrada.") -> None:
        super().__init__(message, status_code=404)


class ReservaJaCanceladaError(LivrariaError):
    def __init__(self, message: str = "Esta reserva já se encontra cancelada.") -> None:
        super().__init__(message, status_code=409)


class DadosInvalidosError(LivrariaError):
    def __init__(self, message: str = "Dados da requisição inválidos.") -> None:
        super().__init__(message, status_code=400)
