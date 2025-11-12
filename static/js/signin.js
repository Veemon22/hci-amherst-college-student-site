function showPopup() {
    const popup = document.getElementById('error-popup');
    if (!popup) return;

    popup.classList.add('show');
    setTimeout(() => {
        popup.classList.remove('show');
    }, 3000); // Hide after 3 seconds
}

// Optional: you can also add extra UX enhancements here, e.g., focus input on load
document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.querySelector('input[name="username"]');
    if (usernameInput) {
        usernameInput.focus();
    }
});
