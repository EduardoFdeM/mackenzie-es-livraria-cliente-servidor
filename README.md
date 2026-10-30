# Livraria Mackenzie — Arquitetura Cliente-Servidor (Exercícios 8.5 e 8.6)

Projeto desenvolvido para a disciplina de **Engenharia de Software** (Laboratório 8: Microsserviços e Nanosserviços — Prof. Dr. Rodrigo Juliani).

---

## 1. Objetivos dos Exercícios

- **Exercício 8.5**: Implementar (ou refatorar) o MVP da Livraria Mackenzie adotando estritamente a **Arquitetura Cliente-Servidor**, com separação física entre o Backend (API REST em Flask retornando JSON) e o Frontend (SPA moderna desacoplada em JavaScript ES6/HTML5/CSS3).
- **Exercício 8.6**: Configurar e preparar o projeto para **Deploy em Nuvem** com links independentes para o backend e para o frontend (Render, Vercel, Docker).

---

## 2. Padrão Arquitetural Cliente-Servidor Implementado

A solução separa claramente as responsabilidades de cliente e servidor através de uma barreira de rede baseada em HTTP/HTTPS e JSON:

```
┌────────────────────────────────────────────────────────────────────────┐
│             CAMADA CLIENTE (Frontend - SPA / Web Browser)              │
│  - Single Page Application (HTML5, CSS3, JavaScript ES6+)              │
│  - Gerenciamento de Estado no Cliente e Debounce de Busca              │
│  - Interface Reativa para Reserva e Cancelamento                       │
│  - Cliente HTTP nativo (Fetch API assíncrono com JSON)                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    │ Requisições HTTP (GET / POST)
                                    │ Respostas application/json
                                    │ Suporte a CORS
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│            CAMADA SERVIDORA (Backend - Flask REST API)                 │
│  - API Gateway / Endpoints REST (/api/v1/livros, /api/v1/reservas)     │
│  - Middleware Nativo de CORS (Preflight OPTIONS & Access-Control)      │
│  - Camada de Serviços (LivrariaService, ReservaService)               │
│  - Camada de Domínio & Exceções (Livro, EstoqueUnidade, Reserva)       │
│  - Persistência em Repositórios Isolados                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     CAMADA DE DADOS & PERSISTÊNCIA                     │
│  - Catálogo de Livros, Estoques das Filiais (Higienópolis, Paulista)  │
│  - Histórico de Reservas e Códigos Sequenciais                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Contrato da API REST (OpenAPI / Endpoints)

| Método | Endpoint | Descrição | Status Sucesso | Status Erro |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | Health check da API | `200 OK` | - |
| `GET` | `/api/v1/livros` | Lista todos os livros ou filtra por `?q=termo` | `200 OK` | - |
| `GET` | `/api/v1/livros/<isbn>` | Detalhes do livro e filiais | `200 OK` | `404 Not Found` |
| `GET` | `/api/v1/livros/<isbn>/estoque` | Consulta saldo e localização por filial | `200 OK` | `404 Not Found` |
| `GET` | `/api/v1/reservas` | Lista todas as reservas | `200 OK` | - |
| `GET` | `/api/v1/reservas/<codigo>` | Consulta dados de uma reserva | `200 OK` | `404 Not Found` |
| `POST` | `/api/v1/reservas` | Cria uma reserva (`{"isbn": "...", "unidade": "..."}`) | `201 Created` | `400 / 409` |
| `POST` | `/api/v1/reservas/<codigo>/cancelar` | Cancela reserva e devolve exemplar ao estoque | `200 OK` | `404 / 409` |

### Exemplo de Payload para Criação de Reserva:
```json
POST /api/v1/reservas
Content-Type: application/json

{
  "isbn": "9780132350884",
  "unidade": "Paulista"
}
```

### Resposta de Sucesso:
```json
{
  "message": "Reserva RES-0001 criada com sucesso!",
  "data": {
    "codigo": "RES-0001",
    "isbn": "9780132350884",
    "titulo": "Clean Code",
    "unidade": "Paulista",
    "status": "Ativa"
  }
}
```

---

## 4. Estrutura do Repositório

```
mackenzie-es-livraria-cliente-servidor/
├── app.py                      # Servidor unificado (API + SPA para dev e demo)
├── requirements.txt            # Dependências (Flask, gunicorn, pytest)
├── Dockerfile                  # Container unificado
├── Procfile                    # Procfile para deploy
├── render.yaml                 # Blueprint multi-serviço (Backend Web + Frontend Static)
├── .gitignore
├── README.md                   # Documentação arquitetural
├── backend/                    # Servidor REST API isolado
│   ├── app.py                  # Fábrica da API REST e CORS
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Procfile
│   ├── domain/                 # Entidades, exceções e to_dict
│   │   ├── exceptions.py
│   │   └── models.py
│   ├── repositories/           # Catálogo, Estoque e Reservas
│   │   ├── catalogo_repo.py
│   │   ├── estoque_repo.py
│   │   └── reserva_repo.py
│   ├── services/               # LivrariaService e ReservaService
│   │   ├── livraria_service.py
│   │   └── reserva_service.py
│   └── api/                    # Endpoints e tratamento de erros
│       ├── routes.py
│       └── error_handlers.py
├── frontend/                   # Aplicação SPA independente (Web Client)
│   ├── index.html              # Interface do usuário
│   ├── css/
│   │   └── styles.css          # Estilos modernos e responsivos
│   ├── js/
│   │   └── app.js              # Lógica reativa consumindo a API REST
│   ├── Dockerfile              # Container Nginx para frontend isolado
│   └── vercel.json             # Configuração para deploy direto na Vercel
└── tests/                      # Bateria de testes automatizados com pytest
    ├── test_api_livros.py
    ├── test_api_reservas.py
    └── test_cliente_servidor_integration.py
```

---

## 5. Como Executar Localmente

### Opção A — Servidor Unificado (Mais Simples)
Executa a API REST e serve os arquivos do frontend estático em um único comando:
```bash
cd mackenzie-es-livraria-cliente-servidor
pip install -r requirements.txt
python app.py
```
Acesse:
- **Frontend SPA**: `http://localhost:5000`
- **Backend API**: `http://localhost:5000/api/v1/health`

### Opção B — Execução Física Desacoplada (Backend e Frontend Separados)
Demonstra a independência física dos dois componentes da arquitetura:

**1. Terminal 1 (Backend REST API):**
```bash
python backend/app.py
# Rodando em http://localhost:5000
```

**2. Terminal 2 (Frontend SPA Estático):**
```bash
python -m http.server 3000 --directory frontend
# Rodando em http://localhost:3000
```
Abra o navegador em `http://localhost:3000`. O frontend se comunica via CORS com `http://localhost:5000/api/v1`.

---

## 6. Como Executar os Testes

```bash
pytest -v
```
Testa todos os endpoints da API, requisições CORS, preflight OPTIONS, códigos de erro HTTP (400, 404, 409), estorno de estoque em cancelamentos e entrega de arquivos estáticos.

---

## 7. Instruções de Deploy (Exercício 8.6)

O arquivo `render.yaml` já está preparado com a declaração de **ambos os serviços**:

1. **Deploy no Render (Backend + Frontend)**:
   - Conecte o repositório no Render através de **Blueprints**.
   - O Render criará automaticamente:
     - `livraria-mackenzie-api`: Web Service Python para a API REST.
     - `livraria-mackenzie-frontend`: Static Site para a interface SPA.
2. **Deploy do Frontend na Vercel**:
   - Conecte o repositório na [Vercel](https://vercel.com).
   - Configure **Root Directory** como `frontend`.
   - A Vercel utilizará o arquivo `frontend/vercel.json` e fornecerá uma URL pública (ex.: `https://livraria-mackenzie.vercel.app`).
   - No topo do frontend, basta colar a URL do seu backend no campo **Servidor Backend (REST API)** e clicar em **Conectar**.
