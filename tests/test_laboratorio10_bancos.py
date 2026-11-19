"""Testes dos requisitos do Laboratório 10 (NoSQL Cosmos DB e SQL PostgreSQL)."""

import pytest
from backend.app import create_api_app
from backend.repositories.catalogo_repo import CatalogoRepository
from backend.repositories.usuario_repo import UsuarioRepository


@pytest.fixture
def client():
    app = create_api_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_nosql_cosmos_catalogo_pelo_menos_10_livros(client):
    """Exercício 10.1: O catálogo NoSQL deve conter pelo menos 10 livros cadastrados."""
    repo = CatalogoRepository()
    livros = repo.listar_todos()
    assert len(livros) >= 10, f"Esperado pelo menos 10 livros, encontrado {len(livros)}"

    # Valida via endpoint HTTP
    response = client.get("/api/v1/livros")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 10
    assert len(data["data"]) >= 10

    # Valida consulta por ISBN de livro recém-adicionado aos 10
    resp_livro = client.get("/api/v1/livros/9788573076103")
    assert resp_livro.status_code == 200
    assert "Padrões de Projeto" in resp_livro.get_json()["data"]["titulo"]


def test_sql_postgres_usuarios_pelo_menos_4_usuarios(client):
    """Exercício 10.2: O banco SQL deve conter pelo menos 4 usuários cadastrados."""
    repo = UsuarioRepository()
    usuarios = repo.listar_todos()
    assert len(usuarios) >= 4, f"Esperado pelo menos 4 usuários, encontrado {len(usuarios)}"

    # Valida via endpoint HTTP GET /api/v1/usuarios
    response = client.get("/api/v1/usuarios")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 4
    assert len(data["data"]) >= 4

    # Valida busca de usuário pelo TIA do aluno (10402800)
    resp_eduardo = client.get("/api/v1/usuarios/10402800")
    assert resp_eduardo.status_code == 200
    user_data = resp_eduardo.get_json()["data"]
    assert user_data["nome"] == "Eduardo Ferreira de Mattos"
    assert user_data["tia"] == "10402800"
    assert user_data["tipo"] == "Aluno"


def test_sql_postgres_cadastrar_novo_usuario(client):
    """Exercício 10.2: Cadastrar um novo usuário no banco SQL via POST."""
    payload = {
        "nome": "Mariana Lima",
        "email": "mariana.lima@mackenzista.com.br",
        "tia": "10409988",
        "tipo": "Aluno"
    }
    response = client.post("/api/v1/usuarios", json=payload)
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["data"]["tia"] == "10409988"
    assert res_data["data"]["nome"] == "Mariana Lima"

    # Confirma que o novo usuário é listado
    resp_lista = client.get("/api/v1/usuarios")
    assert resp_lista.status_code == 200
    assert resp_lista.get_json()["count"] >= 5


def test_database_status_endpoint(client):
    """Valida o endpoint de auditoria dos bancos NoSQL e SQL."""
    response = client.get("/api/v1/database/status")
    assert response.status_code == 200
    dados = response.get_json()

    assert dados["status"] == "online"
    assert "nosql_database" in dados
    assert "sql_database" in dados
    assert dados["nosql_database"]["total_livros_cadastrados"] >= 10
    assert dados["nosql_database"]["status_requisito_10_livros"] == "Aprovado (>= 10)"
    assert dados["sql_database"]["total_usuarios_cadastrados"] >= 4
    assert dados["sql_database"]["status_requisito_4_usuarios"] == "Aprovado (>= 4)"
