"""Pacote de API REST."""
from .routes import api_bp
from .error_handlers import register_error_handlers

__all__ = ["api_bp", "register_error_handlers"]
