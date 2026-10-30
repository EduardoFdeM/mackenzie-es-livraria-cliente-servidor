"""Testes dos endpoints de reservas da API REST."""

import pytest
from backend.app import create_api_app


@pytest.fixture
def client():
    app = create_api_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_api_criar_e_cancelar_reserva_com_estorno(client):
    # Saldo inicial de Clean Code em Paulista
    res_antes = client.get("/api/v1/livros/9780132350884")
    estoque_paulista_antes = next(
        e["quantidade"] for e in res_antes.get_json()["data"]["estoques"] if e["unidade"] == "Paulista"
    )
    assert estoque_paulista_antes == 1

    # 1. Cria reserva
    res_post = client.post(
        "/api/v1/reservas",
        json={"isbn": "9780132350884", "unidade": "Paulista"},
    )
    assert res_post.status_code == 201
    reserva = res_post.get_json()["data"]
    assert reserva["codigo"] == "RES-0001"
    assert reserva["status"] == "Ativa"

    # Saldo deve ter decrementado para 0
    res_durante = client.get("/api/v1/livros/9780132350884")
    estoque_paulista_durante = next(
        e["quantidade"] for e in res_durante.get_json()["data"]["estoques"] if e["unidade"] == "Paulista"
    )
    assert estoque_paulista_durante == 0

    # 2. Cancelar reserva
    res_cancel = client.post("/api/v1/reservas/RES-0001/cancelar")
    assert res_cancel.status_code == 200
    reserva_cancelada = res_cancel.get_json()["data"]
    assert reserva_cancelada["status"] == "Cancelada"

    # Saldo deve ter sido estornado para 1
    res_depois = client.get("/api/v1/livros/9780132350884")
    estoque_paulista_depois = next(
        e["quantidade"] for e in res_depois.get_json()["data"]["estoques"] if e["unidade"] == "Paulista"
    )
    assert estoque_paulista_depois == 1


def test_api_criar_reserva_sem_estoque_retorna_409(client):
    # Pinheiros possui 0 unidades
    res = client.post(
        "/api/v1/reservas",
        json={"isbn": "9780132350884", "unidade": "Pinheiros"},
    )
    assert res.status_code == 409
    assert "Não há exemplares disponíveis" in res.get_json()["error"]


def test_api_criar_reserva_dados_invalidos_retorna_400(client):
    res = client.post("/api/v1/reservas", json={"isbn": "123"})
    assert res.status_code == 400


def test_api_cancelar_reserva_dupla_retorna_409(client):
    client.post("/api/v1/reservas", json={"isbn": "9780132350884", "unidade": "Paulista"})
    client.post("/api/v1/reservas/RES-0001/cancelar")

    res_duplo = client.post("/api/v1/reservas/RES-0001/cancelar")
    assert res_duplo.status_code == 409
    assert "já foi cancelada" in res_duplo.get_json()["error"]


def test_api_cancelar_reserva_inexistente_retorna_404(client):
    res = client.post("/api/v1/reservas/RES-9999/cancelar")
    assert res.status_code == 404
