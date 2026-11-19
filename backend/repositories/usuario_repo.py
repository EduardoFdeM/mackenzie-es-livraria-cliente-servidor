"""Repositório de Usuários com suporte a SQL (PostgreSQL) e fallback local."""

import os
import logging
from typing import Optional, Any
from backend.domain.models import Usuario

logger = logging.getLogger(__name__)

USUARIOS_INICIAIS = [
    Usuario(
        id=1,
        nome="Eduardo Ferreira de Mattos",
        email="10402800@mackenzista.com.br",
        tia="10402800",
        tipo="Aluno",
        ativo=True,
    ),
    Usuario(
        id=2,
        nome="Prof. Dr. Rodrigo Juliani",
        email="rodrigo.juliani@mackenzie.br",
        tia="99001234",
        tipo="Professor",
        ativo=True,
    ),
    Usuario(
        id=3,
        nome="Ana Paula Silveira",
        email="ana.silveira@mackenzista.com.br",
        tia="10401122",
        tipo="Aluno",
        ativo=True,
    ),
    Usuario(
        id=4,
        nome="Carlos Alberto Santos",
        email="carlos.santos@mackenzie.br",
        tia="88005566",
        tipo="Bibliotecário",
        ativo=True,
    ),
]


class UsuarioRepository:
    """Repositório de Usuários com persistência SQL (PostgreSQL) e fallback resiliente."""

    def __init__(self, connection_uri: Optional[str] = None) -> None:
        self.uri = connection_uri or os.environ.get("POSTGRES_URI") or os.environ.get("DATABASE_URL")
        self.tipo_banco = "In-Memory SQL (Fallback)"
        self._usuarios_memoria: dict[int, Usuario] = {}
        self._conn: Any = None

        self._conectar_e_inicializar()

    def _conectar_e_inicializar(self) -> None:
        for u in USUARIOS_INICIAIS:
            self._usuarios_memoria[u.id] = u

        if self.uri:
            try:
                import psycopg2
                self._conn = psycopg2.connect(self.uri, connect_timeout=3)
                self.tipo_banco = "Azure Database for PostgreSQL (SQL Ativo)"
                self._criar_tabela_e_popular_postgres()
                logger.info("Conectado com sucesso ao PostgreSQL.")
            except Exception as e:
                logger.warning(f"Não foi possível conectar ao PostgreSQL ({e}). Usando modo resiliente em memória.")
                self.tipo_banco = "In-Memory SQL (Simulado)"
        else:
            self.tipo_banco = "In-Memory SQL (Modo Local/Dev)"

    def _criar_tabela_e_popular_postgres(self) -> None:
        if self._conn is None:
            return
        try:
            with self._conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(150) NOT NULL,
                        email VARCHAR(150) UNIQUE NOT NULL,
                        tia VARCHAR(20) UNIQUE NOT NULL,
                        tipo VARCHAR(50) NOT NULL,
                        ativo BOOLEAN DEFAULT TRUE
                    );
                """)
                cur.execute("SELECT COUNT(*) FROM usuarios;")
                total = cur.fetchone()[0]
                if total < len(USUARIOS_INICIAIS):
                    for u in USUARIOS_INICIAIS:
                        cur.execute("""
                            INSERT INTO usuarios (id, nome, email, tia, tipo, ativo)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING;
                        """, (u.id, u.nome, u.email, u.tia, u.tipo, u.ativo))
                self._conn.commit()
        except Exception as e:
            logger.warning(f"Erro ao inicializar schema PostgreSQL: {e}")
            if self._conn:
                self._conn.rollback()

    def listar_todos(self) -> list[Usuario]:
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute("SELECT id, nome, email, tia, tipo, ativo FROM usuarios ORDER BY id ASC;")
                    rows = cur.fetchall()
                    if rows:
                        return [
                            Usuario(id=r[0], nome=r[1], email=r[2], tia=r[3], tipo=r[4], ativo=bool(r[5]))
                            for r in rows
                        ]
            except Exception as e:
                logger.warning(f"Erro ao consultar PostgreSQL, usando cache: {e}")
        return list(self._usuarios_memoria.values())

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute("SELECT id, nome, email, tia, tipo, ativo FROM usuarios WHERE id = %s;", (usuario_id,))
                    r = cur.fetchone()
                    if r:
                        return Usuario(id=r[0], nome=r[1], email=r[2], tia=r[3], tipo=r[4], ativo=bool(r[5]))
            except Exception as e:
                logger.warning(f"Erro ao buscar por ID no PostgreSQL: {e}")
        return self._usuarios_memoria.get(usuario_id)

    def buscar_por_tia(self, tia: str) -> Optional[Usuario]:
        tia_limpo = tia.strip()
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute("SELECT id, nome, email, tia, tipo, ativo FROM usuarios WHERE tia = %s;", (tia_limpo,))
                    r = cur.fetchone()
                    if r:
                        return Usuario(id=r[0], nome=r[1], email=r[2], tia=r[3], tipo=r[4], ativo=bool(r[5]))
            except Exception as e:
                logger.warning(f"Erro ao buscar por TIA no PostgreSQL: {e}")
        for u in self._usuarios_memoria.values():
            if u.tia == tia_limpo:
                return u
        return None

    def salvar(self, usuario: Usuario) -> Usuario:
        if usuario.id == 0:
            usuario.id = max(self._usuarios_memoria.keys(), default=0) + 1

        self._usuarios_memoria[usuario.id] = usuario

        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO usuarios (id, nome, email, tia, tipo, ativo)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            nome = EXCLUDED.nome,
                            email = EXCLUDED.email,
                            tia = EXCLUDED.tia,
                            tipo = EXCLUDED.tipo,
                            ativo = EXCLUDED.ativo;
                    """, (usuario.id, usuario.nome, usuario.email, usuario.tia, usuario.tipo, usuario.ativo))
                    self._conn.commit()
            except Exception as e:
                logger.warning(f"Erro ao persistir usuário no PostgreSQL: {e}")
                if self._conn:
                    self._conn.rollback()

        return usuario
