"""Ponto de entrada da Arquitetura Cliente-Servidor da Livraria Mackenzie.

Suporta operação desacoplada automática:
- Quando executado no serviço de API (nome contendo 'api' ou APP_MODE=backend):
  Opera como SERVIDOR BACKEND EXCLUSIVO (apenas JSON REST, sem servir HTML).
- Quando executado no serviço de Front-end (nome contendo 'front' ou APP_MODE=frontend):
  Opera como CLIENTE FRONTEND EXCLUSIVO (apenas SPA estático, consumindo o backend via rede).
- Em ambiente de testes/local unificado:
  Permite execução integrada para conveniência de testes.
"""

import os
from flask import Flask, jsonify, send_from_directory
from backend.app import create_api_app

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
PRODUCTION_API_URL = "https://mack-livraria-api-eduardo-g8a4czche9babbbt.brazilsouth-01.azurewebsites.net/api/v1"

site_name = os.environ.get("WEBSITE_SITE_NAME", "").lower()
app_mode = os.environ.get("APP_MODE", "").lower()

is_backend_only = app_mode == "backend" or ("api" in site_name and "front" not in site_name)
is_frontend_only = app_mode == "frontend" or ("front" in site_name and "api" not in site_name)

if is_frontend_only:
    # Servidor EXCLUSIVO do Front-end (Camada Cliente)
    app = Flask(__name__)

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve_frontend_only(path: str):
        if path.startswith("api/") or path == "api":
            return jsonify({
                "service": "Livraria Mackenzie - Frontend SPA",
                "error": "Este serviço hospeda exclusivamente a Camada Cliente (Front-end SPA). Requisições de dados devem ser feitas no Servidor de Backend (REST API).",
                "backend_url": PRODUCTION_API_URL,
                "status": 404,
            }), 404

        file_path = os.path.join(FRONTEND_DIR, path)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

elif is_backend_only:
    # Servidor EXCLUSIVO do Back-end (Camada Servidora)
    app = create_api_app()

    @app.route("/")
    def serve_backend_info():
        return jsonify({
            "service": "Livraria Mackenzie - Servidor Backend (REST API)",
            "status": "online",
            "architecture": "Cliente-Servidor (Camada Servidora - Backend Puro)",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/v1/health",
                "livros": "/api/v1/livros",
                "detalhes_livro": "/api/v1/livros/<isbn>",
                "estoque_livro": "/api/v1/livros/<isbn>/estoque",
                "reservas": "/api/v1/reservas",
                "cancelar_reserva": "POST /api/v1/reservas/<codigo>/cancelar"
            },
            "note": "Este servidor fornece exclusivamente a API REST JSON. O Front-end desacoplado consome estes endpoints via HTTP/CORS."
        }), 200

else:
    # Modo integrado para testes locais e pytest
    app = create_api_app()

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve_frontend(path: str):
        """Serve a aplicação frontend desacoplada."""
        if path.startswith("api/") or path == "api":
            return jsonify({
                "error": f"Endpoint '/{path}' não encontrado.",
                "status": 404,
            }), 404

        if os.path.exists(os.path.join(FRONTEND_DIR, path)):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Livraria Mackenzie Cliente-Servidor rodando em http://localhost:{port}")
    print(f"API REST: http://localhost:{port}/api/v1/health")
    app.run(host="0.0.0.0", port=port, debug=True)
