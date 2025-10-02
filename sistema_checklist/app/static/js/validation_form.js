// Funções utilitárias (podem ser movidas para um arquivo global)
async function fetchWithAuth(url, options = {}) {
    const token = getToken();
    if (!token) { window.location.href = '/login'; return; }
    const headers = { ...options.headers, 'Authorization': `Bearer ${token}` };
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) { logout(); }
    return response;
}
function getToken() { return localStorage.getItem('accessToken'); }
function logout() {
    localStorage.removeItem('accessToken');
    window.location.href = '/login';
}

document.addEventListener('DOMContentLoaded', async () => {
    if (!getToken()) { window.location.href = '/login'; return; }

    const loadingState = document.getElementById('loading-state');
    const contentState = document.getElementById('checklist-content');

    // Pega o ID do checklist da URL
    const pathParts = window.location.pathname.split('/');
    const checklistId = pathParts[pathParts.length - 1];

    try {
        // 1. Busca os dados do checklist na API
        const response = await fetchWithAuth(`${API_URL}/checklists/${checklistId}`);
        if (!response.ok) {
            throw new Error("Checklist não encontrado ou você não tem permissão para vê-lo.");
        }
        const checklist = await response.json();

        // 2. Preenche a página com os dados
        document.getElementById('info-equipment').textContent = checklist.equipment.name;
        document.getElementById('info-location').textContent = `${checklist.equipment.sector.name} / ${checklist.equipment.location}`;
        document.getElementById('info-collaborator').textContent = checklist.collaborator.full_name;
        document.getElementById('info-date').textContent = new Date(checklist.created_at).toLocaleString('pt-BR');
        
        // Exibe a assinatura do colaborador
        document.getElementById('collaborator-signature').src = checklist.collaborator_signature;

        // Renderiza as respostas
        const responsesContainer = document.getElementById('responses-container');
        responsesContainer.innerHTML = checklist.responses.map(r => `
            <div class="p-2 border-bottom">
                <p class="mb-1"><strong>${r.question}</strong></p>
                <p class="mb-1"><strong>Resposta:</strong> ${r.answer}</p>
                ${r.comment ? `<p class="mb-0 text-muted"><em>Comentário: ${r.comment}</em></p>` : ''}
            </div>
        `).join('');
        
        // Mostra o conteúdo e esconde o "carregando"
        loadingState.classList.add('d-none');
        contentState.classList.remove('d-none');

    } catch (error) {
        loadingState.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }

    // 3. Configura o pad de assinatura do gestor
    const canvas = document.getElementById('manager-signature-pad');
    const signaturePad = new SignaturePad(canvas);
    document.getElementById('clear-signature').addEventListener('click', () => signaturePad.clear());

    // 4. Lida com o envio do formulário de validação
    const validationForm = document.getElementById('validation-form');
    validationForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (signaturePad.isEmpty()) {
            alert("Por favor, forneça sua assinatura para validar.");
            return;
        }

        const payload = {
            manager_signature: signaturePad.toDataURL()
        };
        const feedbackEl = document.getElementById('form-feedback');

        try {
            const validateResponse = await fetchWithAuth(`${API_URL}/checklists/${checklistId}/validate`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!validateResponse.ok) {
                const errorData = await validateResponse.json();
                throw new Error(errorData.detail || "Falha ao validar o checklist.");
            }

            feedbackEl.innerHTML = `<div class="alert alert-success">Checklist validado com sucesso! Redirecionando...</div>`;
            setTimeout(() => window.location.href = '/', 2000); // Volta para o dashboard

        } catch (error) {
            feedbackEl.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });
});