function showPopup() {
    const popup = document.getElementById('error-popup');
    if (!popup) return;

    popup.classList.add('show');
    setTimeout(() => {
        popup.classList.remove('show');
    }, 3000); 
}

document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.querySelector('input[name="username"]');
    if (usernameInput) {
        usernameInput.focus();
    }
});
