// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const canvasFuncionario = document.getElementById('signatureFuncionarioCanvas');
    const signaturePadFuncionario = new SignaturePad(canvasFuncionario);
    const clearButtonFuncionario = document.getElementById('clearFuncionarioSignature');
    const signatureDataInputFuncionario = document.getElementById('assinatura_funcionario_data');
    const nomeFuncionarioInput = document.getElementById('nome_funcionario_assinatura');

    const canvasGestor = document.getElementById('signatureGestorCanvas');
    const signaturePadGestor = new SignaturePad(canvasGestor);
    const clearButtonGestor = document.getElementById('clearGestorSignature');
    const signatureDataInputGestor = document.getElementById('assinatura_gestor_data');
    const nomeGestorInput = document.getElementById('nome_gestor_assinatura');

    const form = document.querySelector('form');

    // Função para redimensionar ambos os canvases
    function resizeCanvases() {
        const ratio = Math.max(window.devicePixelRatio || 1, 1);

        canvasFuncionario.width = canvasFuncionario.offsetWidth * ratio;
        canvasFuncionario.height = canvasFuncionario.offsetHeight * ratio;
        canvasFuncionario.getContext("2d").scale(ratio, ratio);
        signaturePadFuncionario.clear();

        canvasGestor.width = canvasGestor.offsetWidth * ratio;
        canvasGestor.height = canvasGestor.offsetHeight * ratio;
        canvasGestor.getContext("2d").scale(ratio, ratio);
        signaturePadGestor.clear();
    }

    window.addEventListener('resize', resizeCanvases);
    resizeCanvases(); // Chama no carregamento inicial

    clearButtonFuncionario.addEventListener('click', function() {
        signaturePadFuncionario.clear();
    });

    clearButtonGestor.addEventListener('click', function() {
        signaturePadGestor.clear();
    });

    form.addEventListener('submit', function(event) {
        let hasError = false;

        // Validação e captura da assinatura do Funcionário
        if (!signaturePadFuncionario.isEmpty()) {
            signatureDataInputFuncionario.value = signaturePadFuncionario.toDataURL();
        } else {
            signatureDataInputFuncionario.value = '';
            alert('Por favor, o funcionário deve assinar antes de enviar o checklist.');
            nomeFuncionarioInput.focus();
            hasError = true;
        }

        // Validação e captura da assinatura do Gestor
        if (!signaturePadGestor.isEmpty()) {
            signatureDataInputGestor.value = signaturePadGestor.toDataURL();
        } else {
            signatureDataInputGestor.value = '';
            alert('Por favor, o gestor deve assinar antes de enviar o checklist.');
            nomeGestorInput.focus();
            hasError = true;
        }

        if (hasError) {
            event.preventDefault(); // Impede o envio do formulário se houver erro
        }
    });
});