document.addEventListener('DOMContentLoaded', function() {
    // 1. Hanapin lahat ng toggle spans (Current, New, at Re-enter)
    const toggles = document.querySelectorAll('.toggle-password');

    toggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            // 2. Hanapin ang tamang input field na katabi ng clinick na icon
            const container = this.closest('.input-group');
            const passwordInput = container.querySelector('input');
            const icon = this.querySelector('i');

            // 3. Toggle Function: Palitan ang type at icon class
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    });
});