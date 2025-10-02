// Reutiliza a função de fetch autenticado do dashboard.js
// Em um projeto maior, isso ficaria em um arquivo utilitário.
async function fetchWithAuth(url, options = {}) {
    const token = getToken();
    if (!token) { window.location.href = '/login'; return; }
    const headers = { ...options.headers, 'Authorization': `Bearer ${token}` };
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) { logout(); }
    return response;
}

document.addEventListener('DOMContentLoaded', async () => {
    if (!getToken()) { window.location.href = '/login'; return; }

    // Inicializa o pad de assinatura
    const canvas = document.getElementById('signature-pad');
    const signaturePad = new SignaturePad(canvas);
    document.getElementById('clear-signature').addEventListener('click', () => signaturePad.clear());

    // Pega o identificador da URL
    const pathParts = window.location.pathname.split('/');
    const identifier = pathParts[pathParts.length - 1];

    let equipmentId = null; // Armazenará o ID numérico do equipamento para o envio

    // 1. Busca dados do equipamento
    try {
        const response = await fetchWithAuth(`${API_URL}/equipments/by_identifier/${identifier}`);
        if (!response.ok) throw new Error("Equipamento não encontrado.");

        const equipment = await response.json();
        equipmentId = equipment.id; // Salva o ID
        document.getElementById('equipment-name').textContent = `Checklist para: ${equipment.name}`;
        document.getElementById('equipment-details').textContent = `Setor: ${equipment.sector.name} | Local: ${equipment.location}`;

        // 2. Monta o formulário de perguntas
        renderQuestions();
    } catch (error) {
        document.getElementById('equipment-name').textContent = "Erro";
        document.getElementById('equipment-details').textContent = error.message;
    }

    // 3. Lida com a submissão do formulário
    const form = document.getElementById('checklist-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (signaturePad.isEmpty()) {
            alert("Por favor, forneça sua assinatura.");
            return;
        }

        // Coleta os dados do formulário
        const responses = [];
        const questionElements = document.querySelectorAll('.question-item');
        questionElements.forEach((q, index) => {
            const questionText = q.querySelector('label').textContent;
            const answer = q.querySelector('input[type="radio"]:checked')?.value;
            const comment = q.querySelector('textarea').value;
            if(answer) {
                responses.push({ question: questionText, answer: answer, comment: comment });
            }
        });

        const payload = {
            equipment_id: equipmentId,
            collaborator_signature: signaturePad.toDataURL(),
            responses: responses
        };

        // Envia para a API
        const feedbackEl = document.getElementById('form-feedback');
        try {
            const submitResponse = await fetchWithAuth(`${API_URL}/checklists/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!submitResponse.ok) {
                const errorData = await submitResponse.json();
                throw new Error(errorData.detail || "Falha ao enviar o checklist.");
            }

            feedbackEl.innerHTML = `<div class="alert alert-success">Checklist enviado com sucesso! Redirecionando...</div>`;
            setTimeout(() => window.location.href = '/', 2000); // Volta para o dashboard

        } catch (error) {
            feedbackEl.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });
});


function renderQuestions() {
    // Em um sistema real, estas perguntas viriam de uma chamada à API.
    // Por simplicidade, vamos defini-las aqui.
    const questions = [
        "O equipamento está limpo e em bom estado de conservação?",
        "Os dispositivos de parada de emergência estão acessíveis e operantes?",
        "As proteções de partes móveis estão intactas e em seus devidos lugares?",
        "Há vazamentos de óleo, água ou outros fluidos?",
        "A iluminação da área de trabalho é adequada?",
        "Os painéis elétricos estão fechados e sem fios expostos?"
    ];

    const container = document.getElementById('questions-container');
    container.innerHTML = ''; // Limpa o container
    const answerOptions = ["Sim", "Nao", "Parcial", "NSP"];
    const answerLabels = { "Sim": "Sim", "Nao": "Não", "Parcial": "Parcial", "NSP": "N/A" };

    questions.forEach((q, index) => {
        const questionId = `q${index}`;
        const radioButtonsHtml = answerOptions.map(opt => `
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="${questionId}" id="${questionId}-${opt}" value="${opt}" required>
                <label class="form-check-label" for="${questionId}-${opt}">${answerLabels[opt]}</label>
            </div>
        `).join('');

        const questionHtml = `
            <div class="mb-4 p-3 border rounded question-item">
                <label class="form-label fw-bold">${q}</label>
                <div class="mb-2">
                    ${radioButtonsHtml}
                </div>
                <textarea class="form-control" rows="1" placeholder="Adicionar comentário (opcional)..."></textarea>
            </div>
        `;
        container.innerHTML += questionHtml;
    });
}