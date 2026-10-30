"""Testes de integração ponta a ponta do cliente-servidor."""

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_frontend_static_serving(client):
    # Teste de carregamento do index.html da SPA
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "Livraria Mackenzie" in res_index.text
    assert "Frontend SPA Desacoplado" in res_index.text

    # Teste de assets CSS e JS
    res_css = client.get("/css/styles.css")
    assert res_css.status_code == 200
    assert "--primary" in res_css.text

    res_js = client.get("/js/app.js")
    assert res_js.status_code == 200
    assert "API_BASE_URL" in res_js.text


def test_api_via_servidor_unificado(client):
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.get_json()["status"] == "healthy"


def test_api_rota_inexistente_retorna_json_404(client):
    res_404 = client.get("/api/v1/rota_inexistente")
    assert res_404.status_code == 404
    assert res_404.content_type == "application/json"
    data = res_404.get_json()
    assert data["status"] == 404
    assert "não encontrado" in data["error"]


def test_standalone_backend_module_import():
    # Valida que o módulo backend e app funcionam perfeitamente
    from backend.app import create_api_app
    app_standalone = create_api_app()
    assert app_standalone is not None
