document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');
    const submitBtn = document.getElementById('submitBtn');
    const authCard = document.getElementById('authCard');
    const errorAlert = document.getElementById('errorAlert');

    // Показ/скрытие пароля
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            this.textContent = type === 'password' ? '👁️' : '🙈';
            passwordInput.focus();
        });
    }

    // Валидация в реальном времени
    function validateField(input, errorEl, validator) {
        if (!input || !errorEl) return;

        input.addEventListener('blur', function() {
            const isValid = validator(this.value);
            toggleError(this, errorEl, !isValid && this.value);
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                const isValid = validator(this.value);
                toggleError(this, errorEl, !isValid && this.value);
            }
        });
    }

    function toggleError(input, errorEl, showError) {
        if (showError) {
            input.classList.add('error');
            errorEl.classList.add('visible');
        } else {
            input.classList.remove('error');
            errorEl.classList.remove('visible');
        }
    }

    // Валидаторы
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const usernameRegex = /^[a-zA-Z0-9_-]{3,}$/;

    validateField(usernameInput, document.getElementById('usernameError'), function(value) {
        return emailRegex.test(value) || usernameRegex.test(value);
    });

    validateField(passwordInput, document.getElementById('passwordError'), function(value) {
        return value.length >= 8;
    });

    // Отправка формы
    if (form) {
        form.addEventListener('submit', async function(e) {
            // Базовая валидация перед отправкой
            let hasErrors = false;

            const usernameValue = usernameInput.value.trim();
            const passwordValue = passwordInput.value;

            if (!usernameValue || !(emailRegex.test(usernameValue) || usernameRegex.test(usernameValue))) {
                toggleError(usernameInput, document.getElementById('usernameError'), true);
                hasErrors = true;
            }

            if (!passwordValue || passwordValue.length < 8) {
                toggleError(passwordInput, document.getElementById('passwordError'), true);
                hasErrors = true;
            }

            if (hasErrors) {
                e.preventDefault();
                if (authCard) {
                    authCard.classList.add('error');
                    setTimeout(() => authCard.classList.remove('error'), 300);
                }
                return;
            }

            // Показываем состояние загрузки
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            // Позволяем форме отправиться стандартным способом
            // (SSR-обработка на бэкенде)
        });
    }

    // Автофокус на поле ввода
    if (usernameInput && !usernameInput.value) {
        usernameInput.focus();
    } else if (passwordInput) {
        passwordInput.focus();
    }

    // Убираем алерт при клике
    if (errorAlert) {
        errorAlert.style.cursor = 'pointer';
        errorAlert.addEventListener('click', function() {
            this.style.opacity = '0';
            setTimeout(() => this.remove(), 200);
        });
    }

    // Обработка клавиши Enter в полях формы
    if (form) {
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    const inputs = Array.from(form.querySelectorAll('.form-control'));
                    const currentIndex = inputs.indexOf(this);
                    if (currentIndex < inputs.length - 1) {
                        inputs[currentIndex + 1].focus();
                        e.preventDefault();
                    }
                }
            });
        });
    }
});