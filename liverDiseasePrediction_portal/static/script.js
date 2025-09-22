// Update slider value dynamically
function updateValue(elementId, value) {
    document.getElementById(elementId).textContent = value;
}

// Reset form and hide result
function resetForm() {
    document.getElementById('manualForm').reset();
    updateValue('ageValue', 45);
    updateValue('bmiValue', 25);
    updateValue('alcoholValue', 5);
    updateValue('activityValue', 3);
    updateValue('liverTestValue', 40);

    document.getElementById('manualResult').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Handle manual form submission
document.getElementById('manualForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch('/predict_manual', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const manualResultDiv = document.getElementById('manualResult');
        const diseaseStatus = document.getElementById('diseaseStatus');
        const diseaseDescription = document.getElementById('diseaseDescription');

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        if (data.prediction === 1) {
            diseaseStatus.textContent = 'Present';
            diseaseStatus.className = 'disease-present';
            diseaseDescription.textContent =
                'Based on the provided data, this patient has liver disease.';
        } else {
            diseaseStatus.textContent = 'Not Present';
            diseaseStatus.className = 'disease-absent';
            diseaseDescription.textContent =
                'Based on the provided data, this patient does not have liver disease.';
        }

        manualResultDiv.style.display = 'block';
        manualResultDiv.scrollIntoView({ behavior: 'smooth' });
    })
    .catch(err => {
        alert('Error predicting disease: ' + err);
    });
});
