document.addEventListener('DOMContentLoaded', function() {
    // 1. Hanapin ang password input field
    const passwordInput = document.querySelector('input[type="password"]');

    if (passwordInput) {
        // 2. Lagyan ng ID para madaling i-target kung wala pa
        if (!passwordInput.id) passwordInput.id = 'id_password';

        // 3. Gawin ang Eye Icon element
        const eyeIcon = document.createElement('i');
        eyeIcon.className = 'bi bi-eye';
        
        // 4. I-style ang Eye Icon para pumasok sa loob ng input box
        eyeIcon.style.cssText = `
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            color: #666;
            z-index: 100;
            font-size: 1.2rem;
        `;

        // 5. Gawin ang wrapper para hindi magkahiwalay ang input at eye
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.width = '100%';

        // 6. Ipasok sa DOM
        passwordInput.parentNode.insertBefore(wrapper, passwordInput);
        wrapper.appendChild(passwordInput);
        wrapper.appendChild(eyeIcon);

        // 7. Toggle Function
        eyeIcon.addEventListener('click', function() {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                passwordInput.type = 'password';
                this.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    }
});