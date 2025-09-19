document.addEventListener('DOMContentLoaded', function () {
    // Para a tela de preenchimento do colaborador (JÁ EXISTE)
    const canvasColab = document.getElementById('signature-pad-colab');
    if (canvasColab) {
        // ... todo o código do signaturePadColab que já tínhamos ...
        const signaturePadColab = new SignaturePad(canvasColab, {
            backgroundColor: 'rgb(255, 255, 255)'
        });
        const clearButtonColab = document.getElementById('clear-colab');
        const checklistForm = document.getElementById('checklistForm');
        const hiddenSignatureColab = document.getElementById('assinatura_colaborador');
        const hiddenRespostas = document.getElementById('respostas');
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
            perguntas.forEach((p, index) => {
                const perguntaTexto = p.querySelector('label').innerText;
                const respostaInput = p.querySelector('input[type=radio]:checked');
                if (!respostaInput) {
                    allAnswered = false;
                } else {
                    respostasArray.push({
                        pergunta: perguntaTexto,
                        resposta: respostaInput.value
                    });
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

    // Para a tela de validação do gestor (NOVO BLOCO DE CÓDIGO)
    const canvasGestor = document.getElementById('signature-pad-gestor');
    if (canvasGestor) {
        const signaturePadGestor = new SignaturePad(canvasGestor, {
            backgroundColor: 'rgb(255, 255, 255)'
        });
        
        const clearButtonGestor = document.getElementById('clear-gestor');
        const validationForm = document.getElementById('validationForm');
        const hiddenSignatureGestor = document.getElementById('assinatura_gestor');

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