"""Fábrica da API REST (Backend da Arquitetura Cliente-Servidor)."""

import os
from typing import Optional
from flask import Flask, Response, request

from backend.repositories.catalogo_repo import CatalogoRepository
from backend.repositories.estoque_repo import EstoqueRepository
from backend.repositories.reserva_repo import ReservaRepository
from backend.services.livraria_service import LivrariaService
from backend.services.reserva_service import ReservaService
from backend.api.routes import api_bp
from backend.api.error_handlers import register_error_handlers


def create_api_app(
    catalogo_repo: Optional[CatalogoRepository] = None,
    estoque_repo: Optional[EstoqueRepository] = None,
    reserva_repo: Optional[ReservaRepository] = None,
) -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

    c_repo = catalogo_repo or CatalogoRepository()
    e_repo = estoque_repo or EstoqueRepository()
    r_repo = reserva_repo or ReservaRepository()

    app.config["CATALOGO_REPO"] = c_repo
    app.config["ESTOQUE_REPO"] = e_repo
    app.config["RESERVA_REPO"] = r_repo

    app.config["LIVRARIA_SERVICE"] = LivrariaService(c_repo, e_repo)
    app.config["RESERVA_SERVICE"] = ReservaService(r_repo, c_repo, e_repo)

    # Configuração nativa de CORS para clientes web desacoplados (SPAs)
    @app.after_request
    def apply_cors_headers(response: Response) -> Response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        return response

    @app.before_request
    def handle_cors_preflight():
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            return response

    # Registro de rotas e tratadores de erro
    app.register_blueprint(api_bp)
    register_error_handlers(app)

    return app


app = create_api_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
