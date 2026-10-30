"""Rotas REST da API da Livraria Mackenzie."""

from flask import Blueprint, current_app, jsonify, request
from backend.domain.exceptions import DadosInvalidosError

api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@api_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Livraria Mackenzie REST API",
        "version": "1.0.0",
        "architecture": "Cliente-Servidor (Laboratório 8)",
    }), 200


@api_bp.route("/livros", methods=["GET"])
def listar_livros():
    service = current_app.config["LIVRARIA_SERVICE"]
    termo = request.args.get("q", "").strip() or None
    livros = service.listar_livros(termo=termo)
    return jsonify({
        "data": livros,
        "count": len(livros),
        "filtro": termo,
    }), 200


@api_bp.route("/livros/<isbn>", methods=["GET"])
def obter_livro(isbn: str):
    service = current_app.config["LIVRARIA_SERVICE"]
    livro = service.obter_livro(isbn)
    return jsonify({"data": livro}), 200


@api_bp.route("/livros/<isbn>/estoque", methods=["GET"])
def obter_estoque_livro(isbn: str):
    service = current_app.config["LIVRARIA_SERVICE"]
    estoques = service.obter_estoques(isbn)
    return jsonify({"data": estoques, "count": len(estoques)}), 200


@api_bp.route("/reservas", methods=["GET"])
def listar_reservas():
    service = current_app.config["RESERVA_SERVICE"]
    reservas = service.listar_reservas()
    return jsonify({"data": reservas, "count": len(reservas)}), 200


@api_bp.route("/reservas/<codigo>", methods=["GET"])
def obter_reserva(codigo: str):
    service = current_app.config["RESERVA_SERVICE"]
    reserva = service.obter_reserva(codigo)
    return jsonify({"data": reserva}), 200


@api_bp.route("/reservas", methods=["POST"])
def criar_reserva():
    service = current_app.config["RESERVA_SERVICE"]
    raw_json = request.get_json(silent=True)
    if raw_json is not None:
        if not isinstance(raw_json, dict):
            raise DadosInvalidosError("Corpo da requisição deve ser um objeto JSON contendo 'isbn' e 'unidade'.")
        payload = raw_json
    else:
        payload = request.form

    if not payload:
        raise DadosInvalidosError("Corpo da requisição deve ser JSON estruturado contendo 'isbn' e 'unidade'.")

    isbn = payload.get("isbn")
    unidade = payload.get("unidade")

    if not isbn or not unidade:
        raise DadosInvalidosError("Os campos 'isbn' e 'unidade' são obrigatórios.")

    reserva = service.criar_reserva(isbn=str(isbn).strip(), unidade=str(unidade).strip())
    return jsonify({
        "message": f"Reserva {reserva['codigo']} criada com sucesso!",
        "data": reserva,
    }), 201


@api_bp.route("/reservas/<codigo>/cancelar", methods=["POST"])
def cancelar_reserva(codigo: str):
    service = current_app.config["RESERVA_SERVICE"]
    reserva = service.cancelar_reserva(codigo)
    return jsonify({
        "message": f"Reserva {reserva['codigo']} cancelada com sucesso! Exemplar devolvido ao estoque da unidade {reserva['unidade']}.",
        "data": reserva,
    }), 200
