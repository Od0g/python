//const API_URL = 'http://127.0.0.1:8000'; // URL base da nossa API

// Função para salvar o token
function saveToken(token) {
    localStorage.setItem('accessToken', token);
}

// Função para obter o token
function getToken() {
    return localStorage.getItem('accessToken');
}

// Função para fazer logout
function logout() {
    localStorage.removeItem('accessToken');
    window.location.href = '/login'; // Redireciona para a página de login
}

// Anexa o evento de logout ao botão na navbar
const logoutButton = document.getElementById('logout-button');
if (logoutButton) {
    logoutButton.addEventListener('click', logout);
}

// Lógica do formulário de login
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Impede o recarregamento da página

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorAlert = document.getElementById('error-alert');

        try {
            const response = await fetch(`/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ username, password })
            });

            if (!response.ok) {
                throw new Error('Usuário ou senha inválidos.');
            }

            const data = await response.json();
            saveToken(data.access_token);
            window.location.href = '/'; // Redireciona para o dashboard

        } catch (error) {
            errorAlert.textContent = error.message;
            errorAlert.classList.remove('d-none');
        }
    });
}