"""Repositório de Livros e Catálogo com suporte a NoSQL (Azure Cosmos DB for MongoDB)."""

import os
import logging
from decimal import Decimal
from typing import Optional, Any
from backend.domain.models import Livro

logger = logging.getLogger(__name__)

LIVROS_INICIAIS = [
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
    Livro(
        isbn="9788573076103",
        titulo="Padrões de Projeto: Soluções Reutilizáveis de Software Orientado a Objetos",
        autor="Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        preco=Decimal("115.00"),
    ),
    Livro(
        isbn="9788550800653",
        titulo="Domain-Driven Design: Atacando as Complexidades no Coração do Software",
        autor="Eric Evans",
        preco=Decimal("110.00"),
    ),
    Livro(
        isbn="9788575227244",
        titulo="Refatoração: Aperfeiçoando o Design de Códigos Existentes",
        autor="Martin Fowler",
        preco=Decimal("98.00"),
    ),
    Livro(
        isbn="9788575225837",
        titulo="Microsserviços Prontos Para a Produção",
        autor="Susan J. Fowler",
        preco=Decimal("75.00"),
    ),
    Livro(
        isbn="9788575225639",
        titulo="Entendendo Algoritmos: Um Guia Ilustrado Para Programadores",
        autor="Aditya Y. Bhargava",
        preco=Decimal("68.00"),
    ),
    Livro(
        isbn="9788575224625",
        titulo="Python Fluente: Programação Clara, Concisa e Eficaz",
        autor="Luciano Ramalho",
        preco=Decimal("130.00"),
    ),
]


class CatalogoRepository:
    """Repositório de catálogo com persistência NoSQL (Cosmos DB for MongoDB) e fallback em memória."""

    def __init__(self, connection_uri: Optional[str] = None) -> None:
        self.uri = connection_uri or os.environ.get("COSMOS_MONGODB_URI") or os.environ.get("MONGODB_URI")
        self.tipo_banco = "In-Memory NoSQL (Fallback)"
        self._livros_memoria: dict[str, Livro] = {}
        self._db: Any = None
        self._collection: Any = None

        self._conectar_e_inicializar()

    def _conectar_e_inicializar(self) -> None:
        # Inicializa sempre o cache em memória com os 10 livros padrão
        for livro in LIVROS_INICIAIS:
            self._livros_memoria[livro.isbn] = livro

        if self.uri:
            try:
                import pymongo
                client: pymongo.MongoClient = pymongo.MongoClient(
                    self.uri,
                    serverSelectionTimeoutMS=2000,
                    connectTimeoutMS=2000
                )
                # Tenta pingar o servidor Cosmos DB / MongoDB
                client.admin.command('ping')
                self._db = client.get_database("livraria_mackenzie")
                self._collection = self._db.get_collection("catalogo_livros")
                self.tipo_banco = "Azure Cosmos DB for MongoDB (NoSQL Ativo)"
                self._sincronizar_cosmos()
                logger.info("Conectado com sucesso ao Cosmos DB for MongoDB.")
            except Exception as e:
                logger.warning(f"Não foi possível conectar ao Cosmos DB MongoDB ({e}). Usando modo resiliente em memória.")
                self.tipo_banco = "In-Memory NoSQL (Simulado)"
        else:
            self.tipo_banco = "In-Memory NoSQL (Modo Local/Dev)"

    def _sincronizar_cosmos(self) -> None:
        """Garante que a coleção no Cosmos DB possui pelo menos os 10 livros cadastrados."""
        if self._collection is None:
            return
        try:
            total = self._collection.count_documents({})
            if total < len(LIVROS_INICIAIS):
                for livro in LIVROS_INICIAIS:
                    doc = {
                        "isbn": livro.isbn,
                        "titulo": livro.titulo,
                        "autor": livro.autor,
                        "preco": float(livro.preco),
                    }
                    self._collection.update_one({"isbn": livro.isbn}, {"$set": doc}, upsert=True)
        except Exception as e:
            logger.warning(f"Erro ao sincronizar livros no Cosmos DB: {e}")

    def listar_todos(self) -> list[Livro]:
        if self._collection is not None:
            try:
                docs = list(self._collection.find({}, {"_id": 0}))
                if docs:
                    return [
                        Livro(
                            isbn=d["isbn"],
                            titulo=d["titulo"],
                            autor=d["autor"],
                            preco=Decimal(str(d["preco"]))
                        )
                        for d in docs
                    ]
            except Exception as e:
                logger.warning(f"Erro ao ler do Cosmos DB, usando cache: {e}")
        return list(self._livros_memoria.values())

    def buscar_por_isbn(self, isbn: str) -> Optional[Livro]:
        if self._collection is not None:
            try:
                doc = self._collection.find_one({"isbn": isbn}, {"_id": 0})
                if doc:
                    return Livro(
                        isbn=doc["isbn"],
                        titulo=doc["titulo"],
                        autor=doc["autor"],
                        preco=Decimal(str(doc["preco"]))
                    )
            except Exception as e:
                logger.warning(f"Erro ao buscar no Cosmos DB, usando cache: {e}")
        return self._livros_memoria.get(isbn)

    def buscar_por_termo(self, termo: str) -> list[Livro]:
        termo_limpo = termo.strip().casefold()
        if not termo_limpo:
            return []
        todos = self.listar_todos()
        return [
            livro for livro in todos
            if termo_limpo in livro.titulo.casefold()
            or termo_limpo in livro.autor.casefold()
            or termo_limpo == livro.isbn.casefold()
        ]

    def salvar(self, livro: Livro) -> None:
        self._livros_memoria[livro.isbn] = livro
        if self._collection is not None:
            try:
                doc = {
                    "isbn": livro.isbn,
                    "titulo": livro.titulo,
                    "autor": livro.autor,
                    "preco": float(livro.preco),
                }
                self._collection.update_one({"isbn": livro.isbn}, {"$set": doc}, upsert=True)
            except Exception as e:
                logger.warning(f"Erro ao salvar no Cosmos DB: {e}")
