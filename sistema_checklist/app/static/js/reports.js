// Funções utilitárias devem ser compartilhadas
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('accessToken');
    if (!token) { window.location.href = '/login'; return; }
    const headers = { ...options.headers, 'Authorization': `Bearer ${token}` };
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) { localStorage.removeItem('accessToken'); window.location.href = '/login'; }
    return response;
}

// Função para construir a URL com os filtros
function buildQueryString() {
    const filters = {
        start_date: document.getElementById('start_date').value,
        end_date: document.getElementById('end_date').value,
        sector_id: document.getElementById('sector_id').value,
    };
    const params = new URLSearchParams();
    for (const key in filters) {
        if (filters[key]) {
            params.append(key, filters[key]);
        }
    }
    return params.toString();
}

document.addEventListener('DOMContentLoaded', async () => {
    // Popula o dropdown de setores
    const sectorSelect = document.getElementById('sector_id');
    const sectorsRes = await fetchWithAuth(`${API_URL}/sectors/`);
    if (sectorsRes.ok) {
        const sectors = await sectorsRes.json();
        sectors.forEach(s => {
            const option = new Option(s.name, s.id);
            sectorSelect.add(option);
        });
    }

    // Evento para gerar o relatório na tela
    const form = document.getElementById('filters-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const queryString = buildQueryString();
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.innerHTML = '<p>Carregando...</p>';

        const res = await fetchWithAuth(`${API_URL}/reports/checklists?${queryString}`);
        if (res.ok) {
            const checklists = await res.json();
            if (checklists.length === 0) {
                resultsContainer.innerHTML = '<p class="text-muted">Nenhum resultado encontrado.</p>';
                document.getElementById('export-buttons').classList.add('d-none');
                return;
            }

            // Monta a tabela HTML com os resultados
            let table = '<table class="table table-striped table-sm"><thead><tr><th>Data</th><th>Equipamento</th><th>Colaborador</th><th>Status</th><th>Ações</th></tr></thead><tbody>';
            checklists.forEach(c => {
                table += `<tr>
                    <td>${new Date(c.created_at).toLocaleString('pt-BR')}</td>
                    <td>${c.equipment.name}</td>
                    <td>${c.collaborator.full_name}</td>
                    <td><span class="badge bg-${c.status === 'VALIDADO' ? 'success' : 'warning'}">${c.status}</span></td>
                    <td><a href="/validate/${c.id}" class="btn btn-sm btn-info">Ver</a></td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultsContainer.innerHTML = table;
            document.getElementById('export-buttons').classList.remove('d-none');
        } else {
            resultsContainer.innerHTML = '<p class="text-danger">Erro ao carregar relatório.</p>';
        }
    });

    // Eventos para os botões de exportação
    document.getElementById('export-csv').addEventListener('click', () => {
        const queryString = buildQueryString();
        window.location.href = `${API_URL}/reports/checklists/export?format=csv&${queryString}&token=${localStorage.getItem('accessToken')}`; // Adicionando token na URL para simplicidade (não ideal para produção)
    });
    document.getElementById('export-xlsx').addEventListener('click', () => {
        const queryString = buildQueryString();
        window.location.href = `${API_URL}/reports/checklists/export?format=xlsx&${queryString}&token=${localStorage.getItem('accessToken')}`;
    });
    // Nota: Passar o token na URL não é a prática mais segura. Em um sistema de produção,
    // o ideal seria que o clique no botão fizesse um fetch com o header de autorização
    // e, em seguida, usasse a resposta (blob) para iniciar o download no navegador.
    // Por simplicidade do tutorial, a URL é suficiente.
});