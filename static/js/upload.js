document.addEventListener('DOMContentLoaded', function() {
    const dragArea = document.getElementById('dragArea');
    const fileInputs = document.querySelectorAll('input[type="file"]');
    const form = document.getElementById('uploadForm');

    // Make the file inputs clickable
    fileInputs.forEach(input => {
        const container = input.parentElement;
        container.addEventListener('click', () => {
            input.click();
        });

        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'No file chosen';
            const fileNameSpan = input.nextElementSibling;
            fileNameSpan.textContent = fileName;
        });
    });

    // Drag and drop handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dragArea.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    dragArea.addEventListener('dragenter', function() {
        dragArea.classList.add('dragover');
    });

    dragArea.addEventListener('dragover', function() {
        dragArea.classList.add('dragover');
    });

    dragArea.addEventListener('dragleave', function() {
        dragArea.classList.remove('dragover');
    });

    dragArea.addEventListener('drop', function(e) {
        dragArea.classList.remove('dragover');
        const dt = e.dataTransfer;
        const files = dt.files;

        // Distribute files to inputs
        [...files].forEach(file => {
            if (file.name.toLowerCase().includes('tutor')) {
                const input = document.getElementById('peer_tutors_file');
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                input.files = dataTransfer.files;
                input.nextElementSibling.textContent = file.name;
            } else {
                const input = document.getElementById('students_classes_file');
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                input.files = dataTransfer.files;
                input.nextElementSibling.textContent = file.name;
            }
        });
    });

    // Form submission and confetti
    form.addEventListener('submit', function(e) {
        // Only prevent default if we want to show confetti
        e.preventDefault();
        showConfetti();
        // Submit the form after a brief delay
        setTimeout(() => {
            form.submit();
        }, 1000);
    });
});

function showConfetti() {
    const confetti = new window.JSConfetti();
    confetti.addConfetti({
        confettiColors: [
            '#ffc300', '#ffd60a', '#378ede'
        ],
    });
}