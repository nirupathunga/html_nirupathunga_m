function startUSSD() {
    const surveyId = document.getElementById('surveyId').value;
    if (surveyId) window.location.href = `/ussd?surveyId=${surveyId}`;
}

function generateQR() {
    const surveyId = document.getElementById('qrSurveyId').value;
    if (!surveyId || !/^\d+$/.test(surveyId)) {
        document.getElementById('qrMessage').textContent = 'Enter a valid Survey ID (numbers only).';
        document.getElementById('qrMessage').className = 'text-center mt-2 text-lg text-red-500';
        return;
    }
    fetch(`/generate_qr/${surveyId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('qrMessage').textContent = data.error;
                document.getElementById('qrMessage').className = 'text-center mt-2 text-lg text-red-500';
            } else {
                document.getElementById('qrMessage').textContent = 'QR Code Generated!';
                document.getElementById('qrMessage').className = 'text-center mt-2 text-lg text-green-600';
                document.getElementById('qrImage').src = `/static/qr/${data.qr_path.split('/static/qr/')[1]}`;
                document.getElementById('qrContainer').classList.remove('hidden');
            }
        });
}

document.querySelectorAll('input[type="text"]').forEach(input => {
    input.addEventListener('input', function() {
        const button = this.nextElementSibling;
        if (button && button.tagName === 'BUTTON') {
            button.disabled = !this.value;
        }
    });
});
