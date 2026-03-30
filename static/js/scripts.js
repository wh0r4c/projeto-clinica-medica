// ── Confirmação de exclusão ───────────────────────────────────────────────────
document.querySelectorAll('.btn-excluir').forEach(btn => {
    btn.addEventListener('click', function (e) {
        const nome = this.dataset.nome || 'este registro';
        if (!confirm(`Tem certeza que deseja excluir "${nome}"?\nEsta ação não pode ser desfeita.`)) {
            e.preventDefault();
        }
    });
});

// ── Indicador de força de senha ───────────────────────────────────────────────
const senhaInput = document.getElementById('senha');
const forcaBar   = document.getElementById('forca-barra');
const forcaLabel = document.getElementById('forca-label');

if (senhaInput && forcaBar) {
    senhaInput.addEventListener('input', function () {
        const val = this.value;
        let forca = 0;
        if (val.length >= 6)             forca++;
        if (val.length >= 10)            forca++;
        if (/[A-Z]/.test(val))           forca++;
        if (/[0-9]/.test(val))           forca++;
        if (/[^A-Za-z0-9]/.test(val))    forca++;

        const cores  = ['', 'bg-danger', 'bg-warning', 'bg-info', 'bg-primary', 'bg-success'];
        const labels = ['', 'Muito fraca', 'Fraca', 'Média', 'Boa', 'Forte'];
        forcaBar.style.width  = (forca * 20) + '%';
        forcaBar.className    = 'progress-bar ' + (cores[forca] || '');
        if (forcaLabel) forcaLabel.textContent = labels[forca] || '';
    });
}

// ── Auto-dismiss nos alerts após 5s ──────────────────────────────────────────
setTimeout(() => {
    document.querySelectorAll('.alert.auto-dismiss').forEach(alert => {
        bootstrap.Alert.getOrCreateInstance(alert).close();
    });
}, 5000);
