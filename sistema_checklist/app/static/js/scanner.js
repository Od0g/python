document.addEventListener('DOMContentLoaded', () => {
    // Verifica se o usuário está logado antes de tudo
    if (!getToken()) {
        window.location.href = '/login';
        return;
    }

    const statusElement = document.getElementById('scan-status');
    const html5QrCode = new Html5Qrcode("reader");

    const qrCodeSuccessCallback = (decodedText, decodedResult) => {
        // A 'decodedText' é a URL completa, ex: https://seusistema.com/checklist/start/uuid-aqui
        console.log(`Scan result: ${decodedText}`);
        statusElement.innerHTML = `<div class="alert alert-success">QR Code lido com sucesso! Redirecionando...</div>`;

        // Extrai o identificador único (UUID) da URL
        const identifier = decodedText.split('/').pop();

        // Para a câmera após o sucesso
        html5QrCode.stop().then(ignore => {
            // Redireciona para o formulário de checklist
            window.location.href = `/checklist/form/${identifier}`;
        }).catch(err => console.error("Falha ao parar o scanner.", err));
    };

    const config = { fps: 10, qrbox: { width: 250, height: 250 } };

    // Inicia a câmera
    html5QrCode.start({ facingMode: "environment" }, config, qrCodeSuccessCallback)
        .catch(err => {
            statusElement.innerHTML = `<div class="alert alert-danger">Erro ao iniciar a câmera: ${err}</div>`;
        });
});