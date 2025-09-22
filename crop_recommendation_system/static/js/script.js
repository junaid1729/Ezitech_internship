document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('cropForm');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
    submitBtn.disabled = true;

    const formData = new FormData(form);

    fetch('/predict', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        document.getElementById('resultText').textContent = data.result;
        document.getElementById('resultCard').classList.add('show');
        document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        alert(data.error || "An error occurred. Please try again.");
      }
    })
    .catch(err => {
      console.error(err);
      alert("An error occurred while connecting to the server.");
    })
    .finally(() => {
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;
    });
  });

  // Input validation
  document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('input', function() {
      if (this.validity.rangeOverflow) {
        this.setCustomValidity(`Value should be less than or equal to ${this.max}`);
      } else if (this.validity.rangeUnderflow) {
        this.setCustomValidity(`Value should be greater than or equal to ${this.min}`);
      } else {
        this.setCustomValidity('');
      }
    });
  });
});
