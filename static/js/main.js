const registerForm = document.querySelector('.container-r');
const loginForm = document.querySelector('.container-l');

const registerLink = document.getElementById('register-link');
const loginLink = document.getElementById('login-link');

// При відкритті сторінки
registerForm.style.display = 'block';
loginForm.style.display = 'none';

// Показати реєстрацію
registerLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerForm.style.display = 'block';
    loginForm.style.display = 'none';
});

// Показати вхід
loginLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerForm.style.display = 'none';
    loginForm.style.display = 'block';
});