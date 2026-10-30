"""Testes dos endpoints de catálogo e livros da API REST."""

import pytest
from backend.app import create_api_app


@pytest.fixture
def client():
    app = create_api_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_api_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "Livraria Mackenzie" in data["service"]


def test_api_cors_headers_and_preflight(client):
    res = client.options("/api/v1/livros")
    assert res.headers.get("Access-Control-Allow-Origin") == "*"
    assert "GET" in res.headers.get("Access-Control-Allow-Methods")

    res_get = client.get("/api/v1/livros")
    assert res_get.headers.get("Access-Control-Allow-Origin") == "*"


def test_api_listar_livros_e_busca(client):
    res = client.get("/api/v1/livros")
    assert res.status_code == 200
    data = res.get_json()
    assert "data" in data
    assert data["count"] >= 2
    assert any(b["titulo"] == "Clean Code" for b in data["data"])

    # Teste de busca por termo
    res_busca = client.get("/api/v1/livros?q=Clean")
    assert res_busca.status_code == 200
    data_busca = res_busca.get_json()
    assert len(data_busca["data"]) >= 1
    assert "Clean Code" in [b["titulo"] for b in data_busca["data"]]


def test_api_obter_livro_detalhes_e_404(client):
    res = client.get("/api/v1/livros/9780132350884")
    assert res.status_code == 200
    livro = res.get_json()["data"]
    assert livro["isbn"] == "9780132350884"
    assert "estoques" in livro
    assert len(livro["estoques"]) >= 1

    # Inexistente
    res_404 = client.get("/api/v1/livros/0000000000000")
    assert res_404.status_code == 404
    assert res_404.get_json()["status"] == 404


def test_api_obter_estoque_livro(client):
    res = client.get("/api/v1/livros/9780132350884/estoque")
    assert res.status_code == 200
    estoques = res.get_json()["data"]
    assert any(e["unidade"] == "Higienópolis" for e in estoques)
