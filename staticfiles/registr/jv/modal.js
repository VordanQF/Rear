document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById("modal");
    const closeModal = document.getElementById("close-modal-span");
    const openModalBtn = document.getElementById("open-modal-btn");
    const signupForm = document.getElementById("signupForm");
    const usernameSignup = document.getElementById('usernameSignup');
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');

    const usernameSignupError = document.getElementById('usernameSignupError');
    const password1Error = document.getElementById('password1Error');
    const password2Error = document.getElementById('password2Error');
    const firstName = document.getElementById('first_name');
    const lastName = document.getElementById('last_name');
    const city = document.getElementById('city');
    const phone = document.getElementById('phone_number');


    const firstNameError = document.getElementById('firstNameError');
    const lastNameError = document.getElementById('lastNameError');
    const cityError = document.getElementById('cityError');
    const phoneError = document.getElementById('phoneError');


    const submitModalBtn = document.getElementById("submit-form-btn");

    // Убедитесь, что модальное окно скрыто при загрузке страницы
    modal.style.display = "none";

    // Функции для проверки на пустые значения
    function validateNotEmpty(value) {
        return value.trim().length > 0;
    }

    // Проверка основных полей (до открытия модального окна)
    function areAllFieldsFilled() {
        let allFilled = true;

        if (!validateNotEmpty(usernameSignup.value)) {
            usernameSignupError.textContent = "Пожалуйста, введите имя пользователя.";
            allFilled = false;
        } else {
            usernameSignupError.textContent = "";
        }

        if (!validateNotEmpty(password1.value)) {
            password1Error.textContent = "Пожалуйста, введите пароль.";
            allFilled = false;
        } else {
            password1Error.textContent = "";
        }

        if (!validateNotEmpty(password2.value)) {
            password2Error.textContent = "Пожалуйста, подтвердите пароль.";
            allFilled = false;
        } else {
            password2Error.textContent = "";
        }

        return allFilled;
    }

    // Проверка модальных полей (имя, фамилия и т.д.)
    function areModalFieldsFilled() {
        let allFilled = true;

        // Сброс ошибок
        firstNameError.textContent = "";
        lastNameError.textContent = "";
        cityError.textContent = "";
        phoneError.textContent = "";


        if (!validateNotEmpty(firstName.value)) {
            firstNameError.textContent = "Пожалуйста, введите имя.";
            allFilled = false;
        }
        if (!validateNotEmpty(lastName.value)) {
            lastNameError.textContent = "Пожалуйста, введите фамилию.";
            allFilled = false;
        }
        if (!validateNotEmpty(city.value)) {
            cityError.textContent = "Пожалуйста, укажите город.";
            allFilled = false;
        }
        if (!validateNotEmpty(phone.value)) {
            phoneError.textContent = "Введите номер телефона.";
            allFilled = false;
        }
        const phonePattern = /^\+7\d{10}$/;
        if (!phonePattern.test(phone.value.trim())) {
            phoneError.textContent = "Введите номер в формате +71234567890";

    allFilled = false;
}
        return allFilled;
    }

    // Нажали на кнопку "Зарегистрироваться" — проверяем поля
    openModalBtn.addEventListener("click", function () {
        if (areAllFieldsFilled()) {
            modal.style.display = "flex";
        }
    });

    // Закрытие модалки
    closeModal.onclick = function () {
        modal.style.display = "none";
    };

    // Закрытие модалки по клику вне окна
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    // Обработка отправки формы из модального окна
    submitModalBtn.addEventListener("click", function (e) {
        e.preventDefault(); // Прерываем стандартную отправку формы

        if (areModalFieldsFilled()) {
            let extraFields = {
                first_name: firstName.value,
                last_name: lastName.value,
                city: city.value,
                role: document.getElementById("role").value,
                phone_number: phone.value,

            };

            for (let key in extraFields) {
                const input = document.createElement("input");
                input.type = "hidden";
                input.name = key;
                input.value = extraFields[key];
                signupForm.appendChild(input);
            }

            modal.style.display = 'none';
            signupForm.submit(); // Отправка формы вручную
        }
    });
});


  function onTelegramAuth(user) {
    fetch("/telegram-login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify(user)
    }).then(res => {
      if (res.ok) {
        window.location.href = "/profile/";
      }
    });
  }

  // CSRF
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }