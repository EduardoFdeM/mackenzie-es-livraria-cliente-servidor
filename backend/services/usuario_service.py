"""Serviço de Domínio para Gestão de Usuários (SQL PostgreSQL)."""

from typing import Optional
from backend.domain.models import Usuario
from backend.repositories.usuario_repo import UsuarioRepository


class UsuarioService:
    def __init__(self, usuario_repo: UsuarioRepository) -> None:
        self.repo = usuario_repo

    def listar_usuarios(self) -> list[Usuario]:
        return self.repo.listar_todos()

    def obter_usuario_por_id_ou_tia(self, identificador: str) -> Optional[Usuario]:
        identificador = identificador.strip()
        if identificador.isdigit():
            usuario = self.repo.buscar_por_id(int(identificador))
            if usuario:
                return usuario
        return self.repo.buscar_por_tia(identificador)

    def cadastrar_usuario(self, nome: str, email: str, tia: str, tipo: str = "Aluno") -> Usuario:
        existente = self.repo.buscar_por_tia(tia)
        if existente:
            raise ValueError(f"Já existe usuário cadastrado com o TIA {tia}.")

        novo_usuario = Usuario(
            id=0,
            nome=nome.strip(),
            email=email.strip().lower(),
            tia=tia.strip(),
            tipo=tipo.strip(),
            ativo=True,
        )
        return self.repo.salvar(novo_usuario)
