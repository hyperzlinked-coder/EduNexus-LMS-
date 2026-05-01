document.addEventListener('DOMContentLoaded', function() {
    // 1. Find all password inputs on the page
    const passwordInputs = document.querySelectorAll('input[type="password"]');

    passwordInputs.forEach(input => {
        // Create the eye icon wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'input-group';
        
        // Place the wrapper before the input and move the input inside it
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        // Create the eye button
        const button = document.createElement('button');
        button.className = 'btn btn-outline-secondary toggle-password';
        button.type = 'button';
        button.innerHTML = '<i class="bi bi-eye"></i>';
        button.style.borderLeft = 'none'; // Make it look integrated
        
        wrapper.appendChild(button);

        // Toggle Logic
        button.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    });
});