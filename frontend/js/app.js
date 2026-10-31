/**
 * Livraria Mackenzie — Frontend SPA Desacoplado (Cliente-Servidor)
 * Consome a API REST via fetch() com payload JSON.
 */

// Configuração da URL base da API
const PRODUCTION_BACKEND_URL = "https://mack-livraria-api-eduardo-g8a4czche9babbbt.brazilsouth-01.azurewebsites.net/api/v1";

const STORAGE_KEY_API = "MACKENZIE_LIVRARIA_API_URL";
let API_BASE_URL = localStorage.getItem(STORAGE_KEY_API) || (
    // Se estiver em localhost/dev local usa a porta local, senão aponta automaticamente para a API de produção da Azure
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? (window.location.origin.includes("http") ? `${window.location.origin}/api/v1` : "http://localhost:5000/api/v1")
        : PRODUCTION_BACKEND_URL
);

// Estado da Aplicação
let currentBooks = [];
let currentReservations = [];
let activeModalBook = null;
let searchDebounceTimer = null;

// Elementos do DOM
const apiStatusDot = document.getElementById("apiStatusDot");
const apiStatusText = document.getElementById("apiStatusText");
const apiUrlInput = document.getElementById("apiUrlInput");
const btnSalvarApi = document.getElementById("btnSalvarApi");

const searchInput = document.getElementById("searchInput");
const btnLimparBusca = document.getElementById("btnLimparBusca");
const searchMeta = document.getElementById("searchMeta");
const booksGrid = document.getElementById("booksGrid");

const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanes = document.querySelectorAll(".tab-pane");
const reservasCounter = document.getElementById("reservasCounter");
const reservasTableBody = document.getElementById("reservasTableBody");
const reservasEmpty = document.getElementById("reservasEmpty");
const btnAtualizarReservas = document.getElementById("btnAtualizarReservas");

const modalReserva = document.getElementById("modalReserva");
const modalBookTitle = document.getElementById("modalBookTitle");
const modalBookAuthor = document.getElementById("modalBookAuthor");
const modalBookIsbn = document.getElementById("modalBookIsbn");
const modalBookPrice = document.getElementById("modalBookPrice");
const selectUnidade = document.getElementById("selectUnidade");
const modalStockLocation = document.getElementById("modalStockLocation");
const locationText = document.getElementById("locationText");
const modalBtnClose = document.getElementById("modalBtnClose");
const modalBtnCancel = document.getElementById("modalBtnCancel");
const modalBtnConfirm = document.getElementById("modalBtnConfirm");

// Inicialização
document.addEventListener("DOMContentLoaded", () => {
    apiUrlInput.value = API_BASE_URL;
    setupEventListeners();
    testApiHealth();
    loadBooks();
    loadReservations();
});

function setupEventListeners() {
    // Configuração de API
    btnSalvarApi.addEventListener("click", () => {
        const url = apiUrlInput.value.trim().replace(/\/+$/, "");
        if (url) {
            API_BASE_URL = url;
            localStorage.setItem(STORAGE_KEY_API, url);
            showToast("URL da API atualizada!", "success");
            testApiHealth();
            loadBooks();
            loadReservations();
        }
    });

    // Abas
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            tabButtons.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(tabId).classList.add("active");

            if (tabId === "tab-reservas") {
                loadReservations();
            }
        });
    });

    // Busca com debounce
    searchInput.addEventListener("input", (e) => {
        const val = e.target.value.trim();
        btnLimparBusca.classList.toggle("hidden", val.length === 0);
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            loadBooks(val);
        }, 300);
    });

    btnLimparBusca.addEventListener("click", () => {
        searchInput.value = "";
        btnLimparBusca.classList.add("hidden");
        loadBooks("");
    });

    btnAtualizarReservas.addEventListener("click", loadReservations);

    // Modal
    modalBtnClose.addEventListener("click", closeModal);
    modalBtnCancel.addEventListener("click", closeModal);
    modalReserva.addEventListener("click", (e) => {
        if (e.target === modalReserva) closeModal();
    });

    selectUnidade.addEventListener("change", () => {
        const selVal = selectUnidade.value;
        if (!selVal || !activeModalBook) {
            modalStockLocation.classList.add("hidden");
            return;
        }
        const branch = activeModalBook.estoques.find(e => e.unidade === selVal);
        if (branch) {
            modalStockLocation.classList.remove("hidden");
            locationText.textContent = `${branch.localizacao_formatada} (${branch.quantidade} disponíveis)`;
        }
    });

    modalBtnConfirm.addEventListener("click", handleConfirmReservation);
}

// 1. Checagem de Saúde da API
async function testApiHealth() {
    apiStatusDot.className = "status-indicator";
    apiStatusText.textContent = "Conectando...";
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        if (res.ok) {
            const data = await res.json();
            apiStatusDot.classList.add("online");
            apiStatusText.textContent = `Online (${data.service})`;
        } else {
            throw new Error(`Status ${res.status}`);
        }
    } catch (err) {
        apiStatusDot.classList.add("offline");
        apiStatusText.textContent = "API Desconectada";
    }
}

// 2. Carregar Catálogo de Livros (GET /api/v1/livros)
async function loadBooks(query = "") {
    searchMeta.textContent = "Buscando títulos na API...";
    try {
        const url = query ? `${API_BASE_URL}/livros?q=${encodeURIComponent(query)}` : `${API_BASE_URL}/livros`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Erro ao consultar catálogo na API.");

        const json = await res.json();
        currentBooks = json.data || [];
        renderBooksGrid(currentBooks, query);
    } catch (err) {
        searchMeta.textContent = `Falha ao carregar: ${err.message}`;
        booksGrid.innerHTML = `
            <div class="empty-state">
                <p>Não foi possível carregar os livros da API REST.</p>
                <button class="btn btn-primary btn-sm" onclick="loadBooks()">Tentar Novamente</button>
            </div>
        `;
    }
}

function renderBooksGrid(books, query) {
    if (query) {
        searchMeta.textContent = `Encontrado(s) ${books.length} resultado(s) para "${query}"`;
    } else {
        searchMeta.textContent = `Exibindo todos os ${books.length} títulos cadastrados`;
    }

    if (books.length === 0) {
        booksGrid.innerHTML = `
            <div class="empty-state">
                <p>Nenhum livro encontrado.</p>
            </div>
        `;
        return;
    }

    booksGrid.innerHTML = books.map(book => {
        const hasStock = book.total_exemplares > 0;
        const estoquesHtml = book.estoques.map(est => `
            <div class="branch-row">
                <span>${est.unidade}:</span>
                <span class="branch-qty ${est.quantidade > 0 ? 'has-stock' : 'no-stock'}">
                    ${est.quantidade > 0 ? `${est.quantidade} exemplares` : 'Esgotado'}
                </span>
            </div>
        `).join("");

        return `
            <article class="book-card" data-isbn="${book.isbn}">
                <div class="card-top">
                    <span class="card-isbn">ISBN ${book.isbn}</span>
                    <span class="badge ${hasStock ? 'badge-success' : 'badge-danger'}">
                        ${hasStock ? `${book.total_exemplares} em estoque` : 'Esgotado'}
                    </span>
                </div>
                <h3 class="card-title">${escapeHtml(book.titulo)}</h3>
                <p class="card-author">Autor: <strong>${escapeHtml(book.autor)}</strong></p>
                <div class="card-price">${book.preco_formatado}</div>

                <div class="branches-box">
                    <div class="branches-title">Estoque por Filial</div>
                    ${estoquesHtml}
                </div>

                <div class="card-actions">
                    <button 
                        class="btn btn-block ${hasStock ? 'btn-primary' : 'btn-secondary'}" 
                        ${!hasStock ? 'disabled' : ''}
                        onclick="openReservationModal('${book.isbn}')"
                    >
                        ${hasStock ? 'Reservar Exemplar' : 'Indisponível no Momento'}
                    </button>
                </div>
            </article>
        `;
    }).join("");
}

// 3. Modal de Reserva
window.openReservationModal = function(isbn) {
    const book = currentBooks.find(b => b.isbn === isbn);
    if (!book) return;
    activeModalBook = book;

    modalBookTitle.textContent = book.titulo;
    modalBookAuthor.textContent = `Por ${book.autor}`;
    modalBookIsbn.textContent = `ISBN: ${book.isbn}`;
    modalBookPrice.textContent = book.preco_formatado;

    // Popula filiais com estoque > 0
    selectUnidade.innerHTML = '<option value="">Selecione uma filial com estoque...</option>';
    const disponiveis = book.estoques.filter(e => e.quantidade > 0);
    disponiveis.forEach(est => {
        const opt = document.createElement("option");
        opt.value = est.unidade;
        opt.textContent = `${est.unidade} (${est.quantidade} disp.)`;
        selectUnidade.appendChild(opt);
    });

    modalStockLocation.classList.add("hidden");
    locationText.textContent = "";

    modalReserva.classList.remove("hidden");
};

function closeModal() {
    modalReserva.classList.add("hidden");
    activeModalBook = null;
}

// 4. Confirmar Reserva (POST /api/v1/reservas)
async function handleConfirmReservation() {
    if (!activeModalBook) return;
    const unidade = selectUnidade.value;
    if (!unidade) {
        showToast("Por favor, selecione uma filial para retirada.", "error");
        return;
    }

    modalBtnConfirm.disabled = true;
    modalBtnConfirm.textContent = "Processando...";

    try {
        const res = await fetch(`${API_BASE_URL}/reservas`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                isbn: activeModalBook.isbn,
                unidade: unidade,
            }),
        });

        const json = await res.json();
        if (!res.ok) {
            throw new Error(json.error || "Erro ao realizar reserva.");
        }

        showToast(`Reserva ${json.data.codigo} gerada com sucesso na filial ${unidade}!`, "success");
        closeModal();
        await loadBooks(searchInput.value.trim());
        await loadReservations();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        modalBtnConfirm.disabled = false;
        modalBtnConfirm.textContent = "Confirmar Reserva";
    }
}

// 5. Carregar Reservas (GET /api/v1/reservas)
async function loadReservations() {
    try {
        const res = await fetch(`${API_BASE_URL}/reservas`);
        if (!res.ok) throw new Error("Erro ao consultar reservas na API.");
        const json = await res.json();
        currentReservations = json.data || [];
        reservasCounter.textContent = currentReservations.filter(r => r.status === 'Ativa').length;
        renderReservationsTable(currentReservations);
    } catch (err) {
        reservasCounter.textContent = "!";
    }
}

function renderReservationsTable(reservas) {
    if (reservas.length === 0) {
        reservasTableBody.innerHTML = "";
        reservasEmpty.classList.remove("hidden");
        return;
    }

    reservasEmpty.classList.add("hidden");
    reservasTableBody.innerHTML = reservas.map(r => {
        const isAtiva = r.status === "Ativa";
        return `
            <tr>
                <td class="font-mono font-bold">${r.codigo}</td>
                <td>${escapeHtml(r.titulo)}</td>
                <td class="font-mono text-muted">${r.isbn}</td>
                <td>${escapeHtml(r.unidade)}</td>
                <td>
                    <span class="badge ${isAtiva ? 'badge-success' : 'badge-neutral'}">
                        ${isAtiva ? '● Ativa' : '✕ Cancelada'}
                    </span>
                </td>
                <td>
                    ${isAtiva ? `
                        <button class="btn btn-sm btn-danger" onclick="cancelReservation('${r.codigo}', '${r.unidade}')">
                            Cancelar Reserva
                        </button>
                    ` : `
                        <span class="text-muted" style="font-size:0.8rem">Exemplar devolvido</span>
                    `}
                </td>
            </tr>
        `;
    }).join("");
}

// 6. Cancelar Reserva (POST /api/v1/reservas/{codigo}/cancelar)
window.cancelReservation = async function(codigo, unidade) {
    if (!confirm(`Deseja cancelar a reserva ${codigo}? O exemplar será automaticamente devolvido ao estoque da unidade ${unidade}.`)) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/reservas/${codigo}/cancelar`, {
            method: "POST",
        });

        const json = await res.json();
        if (!res.ok) {
            throw new Error(json.error || "Erro ao cancelar reserva.");
        }

        showToast(`Reserva ${codigo} cancelada! Exemplar devolvido ao estoque da filial ${unidade}.`, "success");
        await loadReservations();
        await loadBooks(searchInput.value.trim());
    } catch (err) {
        showToast(err.message, "error");
    }
};

// Toast Notifications
function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, m => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[m]);
}
