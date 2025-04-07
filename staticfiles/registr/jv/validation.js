document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');
    const usernameError = document.getElementById('usernameError');
    if (errorParam === 'true') {
        usernameError.textContent = 'Проверьте данные';
}

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Отменяем отправку формы по умолчанию

    const username = document.getElementById('username');
    const password = document.getElementById('password');

    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');

    // Очистка всех ошибок перед проверкой
    clearErrors();

    if (!validateLoginUsername(username.value)) {
        usernameError.textContent = 'Неверный формат логина';
    }

    if (!validateLoginPassword(password.value)) {
        passwordError.textContent = 'Неверный формат пароля';
    }

    // Если все поля валидны, то форма может быть отправлена
    if (validateLoginUsername(username.value) && validateLoginPassword(password.value)) {
        this.submit(); // Отправляем форму, если все в порядке
    }
});
});

document.getElementById('signupForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Отменяем отправку формы по умолчанию

    const usernameSignup = document.getElementById('usernameSignup');
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');

    const usernameSignupError = document.getElementById('usernameSignupError');
    const password1Error = document.getElementById('password1Error');
    const password2Error = document.getElementById('password2Error');

    // Очистка всех ошибок перед проверкой
    clearErrors();

    if (!validateSignupUsername(usernameSignup.value)) {
        usernameSignupError.textContent = 'Имя пользователя должно содержать от 6 до 20 символов';
    }
    if (!hasMinLength(password1.value)) {
        password1Error.textContent = 'Проверьте длину пароля (не менее 8 символов)';
    }
    if (!hasLetter(password1.value)) {
        password1Error.textContent = 'В пароле должна быть хотя бы одна буква';
    }
    if (!hasDigit(password1.value)) {
        password1Error.textContent = 'В пароле должна быть хотя бы одна цифра';
    }
    if (!hasUppercaseLetter(password1.value)) {
        password1Error.textContent = 'В пароле должна быть хотя бы одна заглавная буква';
    }
    if (!isSimplePassword(password1.value)) {
        password1Error.textContent = 'Пароль слишком простой';
    }
    if (!hasValidCharacters(password1.value)) {
        password1Error.textContent = 'Пароль содержит недопустимые символы';
    }
    if (!validateConfirmPassword(password1.value, password2.value)) {
        password2Error.textContent = 'Пароли должны совпадать';
    }
    if (!validateSignupUsernameNull(usernameSignup.value.trim() === "")) {
        usernameSignupError.textContent = "Пожалуйста, введите имя пользователя.";
    }

    if (!validateSignupPasswordNull(password1.value.trim() === "")) {
        password1Error.textContent = "Пожалуйста, введите пароль.";
    }

    if (!validateSignupPassword2Null(password2.value.trim() === "")) {
        password2Error.textContent = "Пожалуйста, подтвердите пароль.";
    }

    // Если все поля валидны, то форма может быть отправлена
    if (validateSignupUsername(usernameSignup.value) &&
        validateSignupPassword(password1.value) &&
        validateConfirmPassword(password1.value, password2.value)
    ) {
        this.submit(); // Отправляем форму, если все в порядке
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const errornameParam = urlParams.get('errorname');
    const usernameSignupError = document.getElementById('usernameSignupError');
    if (errornameParam === 'true') {
        usernameSignupError.textContent = 'Имя уже занято';
}});
// Функция очистки всех ошибок
function clearErrors() {
    document.querySelectorAll('.error').forEach(error => error.textContent = '');
}

// Валидация имени пользователя для входа
function validateLoginUsername(value) {
    return value.trim().length > 0;
}

// Валидация пароля для входа
function validateLoginPassword(value) {
    return value.trim().length > 0;
}

// Валидация имени пользователя для регистрации
function validateSignupUsername(value) {
    return value.length >= 6 && value.length <= 20;
}
function validateSignupPasswordNull(value) {
    return value.trim().length > 0;
}
function validateSignupUsernameNull(value) {
    return value.trim().length > 0;}
function validateSignupPassword2Null(value) {
    return value.trim().length > 0;}
// Валидация пароля для регистрации
function validateSignupPassword(value) {
//    const regex = /^(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
//    return regex.test(value);
    return (
        hasUppercaseLetter(password1.value) &&
        hasDigit(password1.value) &&
        hasMinLength(password1.value) &&
        hasValidCharacters(password1.value) &&
        hasLetter(password1.value) &&
        isSimplePassword (password1.value)
    );
}

// Валидация подтверждения пароля
function validateConfirmPassword(password, confirmPassword) {
    return password === confirmPassword;
}
// Функция для проверки наличия хотя бы одной заглавной буквы
function hasUppercaseLetter(password) {
    return /[A-Z]/.test(password);
}
function hasLetter(password) {
    return /[a-zA-Z]/.test(password);
}
// Функция для проверки наличия хотя бы одной цифры
function hasDigit(password) {
    return /\d/.test(password);
}

// Функция для проверки минимальной длины пароля (не менее 8 символов)
function hasMinLength(password) {
    return password.length >= 8;
}

// Функция для проверки допустимых символов (латинские буквы и цифры)
function hasValidCharacters(password) {
    return /^[a-zA-Z\d]+$/.test(password);
}

async function getSimplePasswords() {
    try {
        const response = await fetch('simple_passwords.txt');
        const text = await response.text();
        return text.split('\n').filter(Boolean); // Преобразуем текст в массив строк, удаляя пустые элементы
    } catch (error) {
        console.error('Ошибка при чтении файла:', error);
        return [];
    }
}
async function isSimplePassword(password) {
    const simplePasswords = await getSimplePasswords(); // Получаем список простых паролей
    const lowerCasePassword = password.toLowerCase(); // Приводим пароль к нижнему регистру
    return simplePasswords.some(simplePassword => simplePassword.toLowerCase() === lowerCasePassword); // Проверяем, совпадает ли пароль с одним из простых паролей
}