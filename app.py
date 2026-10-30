"""Servidor unificado para desenvolvimento local e deploy simultâneo.

Disponibiliza:
- API REST em: /api/v1/*
- Frontend SPA desacoplado em: / (arquivos estáticos em frontend/)
"""

import os
from flask import send_from_directory
from backend.app import create_api_app

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

app = create_api_app()


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_frontend(path: str):
    """Serve a aplicação frontend desacoplada."""
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Livraria Mackenzie Cliente-Servidor rodando em http://localhost:{port}")
    print(f"API REST: http://localhost:{port}/api/v1/health")
    app.run(host="0.0.0.0", port=port, debug=True)
