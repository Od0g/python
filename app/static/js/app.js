// Função para redimensionar o canvas para preencher o container, mantendo a qualidade
function resizeCanvas(canvas) {
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext("2d").scale(ratio, ratio);
}

document.addEventListener('DOMContentLoaded', function () {

    // Para a tela de preenchimento do colaborador
    const canvasColab = document.getElementById('signature-pad-colab');
    if (canvasColab) {
        resizeCanvas(canvasColab); // AJUSTE AQUI
        const signaturePadColab = new SignaturePad(canvasColab, {
            backgroundColor: 'rgb(255, 255, 255)'
        });
        
        // O resto do código do colaborador continua igual...
        const clearButtonColab = document.getElementById('clear-colab');
        const checklistForm = document.getElementById('checklistForm');
        // ... (etc)
    }

    // Para a tela de validação do gestor
    const canvasGestor = document.getElementById('signature-pad-gestor');
    if (canvasGestor) {
        resizeCanvas(canvasGestor); // AJUSTE AQUI
        const signaturePadGestor = new SignaturePad(canvasGestor, {
            backgroundColor: 'rgb(255, 255, 255)'
        });
        
        // O resto do código do gestor continua igual...
        const clearButtonGestor = document.getElementById('clear-gestor');
        const validationForm = document.getElementById('validationForm');
        // ... (etc)
    }

    // Código completo dos event listeners (sem alterações)
    if (canvasColab) {
        const clearButtonColab = document.getElementById('clear-colab');
        const checklistForm = document.getElementById('checklistForm');
        const hiddenSignatureColab = document.getElementById('assinatura_colaborador');
        const hiddenRespostas = document.getElementById('respostas');
        const signaturePadColab = new SignaturePad(canvasColab);

        clearButtonColab.addEventListener('click', function (event) {
            event.preventDefault();
            signaturePadColab.clear();
        });

        checklistForm.addEventListener('submit', function (event) {
            if (signaturePadColab.isEmpty()) {
                alert("Por favor, forneça sua assinatura.");
                event.preventDefault();
                return;
            }
            const perguntas = document.querySelectorAll('.pergunta-item');
            const respostasArray = [];
            let allAnswered = true;
            perguntas.forEach((p) => {
                const perguntaTexto = p.querySelector('label').innerText;
                const respostaInput = p.querySelector('input[type=radio]:checked');
                if (!respostaInput) { allAnswered = false; } 
                else {
                    respostasArray.push({ pergunta: perguntaTexto, resposta: respostaInput.value });
                }
            });
            if (!allAnswered) {
                alert("Por favor, responda todas as perguntas.");
                event.preventDefault();
                return;
            }
            hiddenSignatureColab.value = signaturePadColab.toDataURL('image/png');
            hiddenRespostas.value = JSON.stringify(respostasArray);
        });
    }

    if(canvasGestor) {
        const clearButtonGestor = document.getElementById('clear-gestor');
        const validationForm = document.getElementById('validationForm');
        const hiddenSignatureGestor = document.getElementById('assinatura_gestor');
        const signaturePadGestor = new SignaturePad(canvasGestor);

        clearButtonGestor.addEventListener('click', function (event) {
            event.preventDefault();
            signaturePadGestor.clear();
        });

        validationForm.addEventListener('submit', function(event) {
             if (signaturePadGestor.isEmpty()) {
                alert("Por favor, forneça sua assinatura para validar.");
                event.preventDefault();
                return;
            }
            hiddenSignatureGestor.value = signaturePadGestor.toDataURL('image/png');
        });
    }
});