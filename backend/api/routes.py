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


# -------------------------------------------------------------
# Exercício 10.2: Endpoints REST de Usuários (SQL PostgreSQL)
# -------------------------------------------------------------

@api_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    service = current_app.config.get("USUARIO_SERVICE")
    if not service:
        return jsonify({"error": "Serviço de usuários não configurado."}), 500
    usuarios = [u.to_dict() for u in service.listar_usuarios()]
    return jsonify({
        "data": usuarios,
        "count": len(usuarios),
        "database": "SQL PostgreSQL (Usuários)",
    }), 200


@api_bp.route("/usuarios/<identificador>", methods=["GET"])
def obter_usuario(identificador: str):
    service = current_app.config.get("USUARIO_SERVICE")
    if not service:
        return jsonify({"error": "Serviço de usuários não configurado."}), 500
    usuario = service.obter_usuario_por_id_ou_tia(identificador)
    if not usuario:
        return jsonify({"error": f"Usuário '{identificador}' não encontrado."}), 404
    return jsonify({"data": usuario.to_dict()}), 200


@api_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    service = current_app.config.get("USUARIO_SERVICE")
    if not service:
        return jsonify({"error": "Serviço de usuários não configurado."}), 500
    dados = request.get_json(silent=True)
    if not dados or not isinstance(dados, dict):
        raise DadosInvalidosError("Envie um payload JSON contendo 'nome', 'email' e 'tia'.")

    nome = dados.get("nome")
    email = dados.get("email")
    tia = dados.get("tia")
    tipo = dados.get("tipo", "Aluno")

    if not nome or not email or not tia:
        raise DadosInvalidosError("Os campos 'nome', 'email' e 'tia' são obrigatórios.")

    try:
        usuario = service.cadastrar_usuario(str(nome), str(email), str(tia), str(tipo))
        return jsonify({
            "message": f"Usuário {usuario.nome} (TIA: {usuario.tia}) cadastrado com sucesso!",
            "data": usuario.to_dict(),
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


# -------------------------------------------------------------
# Status dos Bancos de Dados (Laboratório 10 - NoSQL e SQL)
# -------------------------------------------------------------

@api_bp.route("/database/status", methods=["GET"])
def status_bancos():
    catalogo_repo = current_app.config["CATALOGO_REPO"]
    usuario_repo = current_app.config.get("USUARIO_REPO")

    total_livros = len(catalogo_repo.listar_todos())
    total_usuarios = len(usuario_repo.listar_todos()) if usuario_repo else 0

    return jsonify({
        "status": "online",
        "laboratorio": "Laboratório 10 - Bancos de Dados em Arquitetura de Software",
        "nosql_database": {
            "tipo": "Azure Cosmos DB for MongoDB (NoSQL)",
            "finalidade": "Catálogo de Livros (Exercício 10.1)",
            "conexao": getattr(catalogo_repo, "tipo_banco", "Ativo"),
            "total_livros_cadastrados": total_livros,
            "status_requisito_10_livros": "Aprovado (>= 10)" if total_livros >= 10 else "Pendente",
        },
        "sql_database": {
            "tipo": "Azure Database for PostgreSQL (SQL)",
            "finalidade": "Registro de Informações de Usuários (Exercício 10.2)",
            "conexao": getattr(usuario_repo, "tipo_banco", "Ativo") if usuario_repo else "N/A",
            "total_usuarios_cadastrados": total_usuarios,
            "status_requisito_4_usuarios": "Aprovado (>= 4)" if total_usuarios >= 4 else "Pendente",
        }
    }), 200

