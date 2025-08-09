// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const signatureAreas = document.querySelectorAll('.signature-area');

    if (signatureAreas.length > 0) {
        signatureAreas.forEach(area => {
            const canvas = area.querySelector('.signature-canvas');
            const signaturePad = new SignaturePad(canvas);
            const clearButton = area.querySelector('.clear-signature-btn');
            const signatureDataInput = area.querySelector('.signature-data-input');

            function resizeCanvas() {
                const ratio = Math.max(window.devicePixelRatio || 1, 1);
                canvas.width = canvas.offsetWidth * ratio;
                canvas.height = canvas.offsetHeight * ratio;
                canvas.getContext("2d").scale(ratio, ratio);
                signaturePad.clear();
            }

            window.addEventListener('resize', resizeCanvas);
            resizeCanvas();

            clearButton.addEventListener('click', function() {
                signaturePad.clear();
            });

            const form = document.querySelector('form');
            form.addEventListener('submit', function(event) {
                // Converte a assinatura para Base64 antes de enviar
                if (!signaturePad.isEmpty()) {
                    signatureDataInput.value = signaturePad.toDataURL();
                } else {
                    signatureDataInput.value = '';
                    // Se a assinatura for obrigatória, adicione uma validação aqui
                }
            });
        });
    }
});