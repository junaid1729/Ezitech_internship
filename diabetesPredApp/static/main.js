document.addEventListener('DOMContentLoaded', function() {

    // Tab switching
    const csvTab = document.getElementById('csv-tab');
    const manualTab = document.getElementById('manual-tab');
    const csvForm = document.getElementById('csvForm');
    const manualForm = document.getElementById('manualForm');

    csvTab.addEventListener('click', () => {
        csvTab.classList.add('active');
        manualTab.classList.remove('active');
        csvForm.classList.remove('d-none');
        manualForm.classList.add('d-none');
        document.getElementById('resultsContainer').innerHTML = '';
    });

    manualTab.addEventListener('click', () => {
        manualTab.classList.add('active');
        csvTab.classList.remove('active');
        manualForm.classList.remove('d-none');
        csvForm.classList.add('d-none');
        document.getElementById('resultsContainer').innerHTML = '';
    });

    function round2(num){ return Math.round(num*100)/100; }

    function submitForm(form) {
        form.addEventListener('submit', function(e){
            e.preventDefault();
            const resultsDiv = document.getElementById('resultsContainer');
            resultsDiv.innerHTML = '<div class="text-center my-3"><div class="spinner-border text-primary" role="status"></div></div>';

            const formData = new FormData(form);
            fetch('/predict', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if(data.error){
                    resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    return;
                }

                resultsDiv.innerHTML = '';
                data.forEach((patient, i) => {
                    const card = document.createElement('div');
                    card.className = 'card p-3';
                    let html = `<h6>Patient ${i+1}</h6><div class="row">`;
                    Object.keys(patient).forEach(k => {
                        if(k !== 'Diagnosis_Result') {
                            let val = round2(patient[k]);
                            html += `<div class="col-md-2"><strong>${k}</strong>: ${val}</div>`;
                        }
                    });
                    html += `</div>`;
                    html += `<p class="mt-2">Diagnosis Result: <span class="badge bg-${patient.Diagnosis_Result==='Diabetic'?'danger':patient.Diagnosis_Result==='Prediabetic'?'warning':'success'}">${patient.Diagnosis_Result}</span></p>`;
                    card.innerHTML = html;
                    resultsDiv.appendChild(card);
                });

            }).catch(err=>{
                resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${err}</div>`;
            });
        });
    }

    submitForm(csvForm);
    submitForm(manualForm);
});
