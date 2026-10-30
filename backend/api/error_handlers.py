"""Tratamento centralizado de erros da API REST."""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from backend.domain.exceptions import LivrariaError


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(LivrariaError)
    def handle_livraria_error(error: LivrariaError):
        return jsonify({
            "error": error.message,
            "type": error.__class__.__name__,
            "status": error.status_code,
        }), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({
            "error": error.description,
            "type": error.__class__.__name__,
            "status": error.code or 500,
        }), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        return jsonify({
            "error": "Erro interno no servidor.",
            "detail": str(error),
            "status": 500,
        }), 500
