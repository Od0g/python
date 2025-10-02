// Função utilitária para fazer requisições autenticadas
async function fetchWithAuth(url, options = {}) {
    const token = getToken();
    // Se não houver token, esta função não faz nada, a verificação principal está no DOMContentLoaded
    if (!token) return; 

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) { // Token inválido ou expirado
        logout();
    }

    return response;
}

// Função principal que executa quando a página do dashboard carrega
document.addEventListener('DOMContentLoaded', async () => {
    const token = getToken();
    if (!token) {
        window.location.href = '/login'; // Se não há token, vai para o login
        return;
    }

    // Mostra o botão de logout que está no base.html
    const logoutButton = document.getElementById('logout-button');
    if(logoutButton) logoutButton.classList.remove('d-none');

    // Busca os dados do usuário logado
    const response = await fetchWithAuth(`/users/me/`); // Rota para buscar dados do usuário
    
    if (response && response.ok) {
        const user = await response.json();
        document.getElementById('welcome-message').textContent = `Bem-vindo, ${user.full_name}!`;
        document.getElementById('role-message').textContent = `Seu perfil é: ${user.role}`;

        // ===== LÓGICA DE EXIBIÇÃO ATUALIZADA =====
        if (user.role === 'colaborador') {
            document.getElementById('collaborator-section').classList.remove('d-none');
        } 
        
        if (user.role === 'gestor') {
            document.getElementById('manager-section').classList.remove('d-none');
            loadPendingChecklists();
        } 
        
        if (user.role === 'administrador') {
            // Um admin vê tanto a seção do gestor quanto a sua própria
            document.getElementById('manager-section').classList.remove('d-none');
            document.getElementById('admin-section').classList.remove('d-none');
            loadPendingChecklists();
        }
        
    } else {
        // Se a chamada falhar, exibe uma mensagem de erro
        document.getElementById('welcome-message').textContent = 'Erro ao carregar dados do usuário.';
    }
});

// Função para carregar os checklists pendentes do gestor
async function loadPendingChecklists() {
    const response = await fetchWithAuth(`/checklists/pending`);
    if (response && response.ok) {
        const checklists = await response.json();
        const listElement = document.getElementById('pending-checklists-list');
        listElement.innerHTML = ''; // Limpa a lista

        if (checklists.length === 0) {
            listElement.innerHTML = '<p class="text-muted">Nenhum checklist pendente.</p>';
            return;
        }

        checklists.forEach(c => {
            const item = document.createElement('a');
            // Corrigido para usar a rota de validação correta
            item.href = `/validate/${c.id}`; 
            item.className = 'list-group-item list-group-item-action';
            item.innerHTML = `
                <strong>Equipamento:</strong> ${c.equipment.name} <br>
                <strong>Colaborador:</strong> ${c.collaborator.full_name} <br>
                <strong>Data:</strong> ${new Date(c.created_at).toLocaleString('pt-BR')}
            `;
            listElement.appendChild(item);
        });
    }
}