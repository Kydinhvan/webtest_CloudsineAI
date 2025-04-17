// Modern JavaScript enhancements for the check file app

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.querySelector('#file');
    const fileInfoDisplay = document.querySelector('#file-info');
    const uploadButton = document.querySelector('button[type="submit"]');
    const card = document.querySelector('.card');

    // === File Selection ===
    fileInput?.addEventListener('change', () => {
        const file = fileInput.files[0];
        const maxFileSizeMB = 16;
        const maxSize = maxFileSizeMB * 1024 * 1024;

        if (!file) return;

        // Validation
        if (file.size > maxSize) {
            alert(`File too large! Max allowed size is ${maxFileSizeMB}MB.`);
            fileInput.value = '';
            fileInfoDisplay.textContent = '';
            return;
        }

        // Display file name + size in UI
        const sizeKB = (file.size / 1024).toFixed(1);
        fileInfoDisplay.textContent = `Selected: ${file.name} (${sizeKB} KB)`;
        fileInfoDisplay.style.color = '#0077cc';
    });

    // === Scan Button Animation ===
    uploadButton?.addEventListener('click', () => {
        uploadButton.classList.add('uploading');
        uploadButton.innerText = 'Scanning...';
        setTimeout(() => {
            uploadButton.classList.remove('uploading');
            uploadButton.innerText = 'Scan File';
        }, 3000); // Mock animation delay
    });

    // === Apply "scan complete" animation ===
    if (card?.dataset?.status === 'complete') {
        card.classList.add('scan-complete');
    }

    // === Custom Tooltip Implementation ===
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            const tip = document.createElement('div');
            tip.className = 'custom-tooltip';
            tip.innerText = el.getAttribute('data-tooltip');
            document.body.appendChild(tip);

            const rect = el.getBoundingClientRect();
            tip.style.left = `${rect.left + window.scrollX}px`;
            tip.style.top = `${rect.top + window.scrollY - 30}px`;
        });

        el.addEventListener('mouseleave', () => {
            document.querySelectorAll('.custom-tooltip').forEach(tip => tip.remove());
        });
    });
});
