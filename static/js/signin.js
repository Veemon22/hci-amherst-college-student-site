function showPopup(show) {
    if (show) {
        const popup = document.getElementById('error-popup');
        popup.style.display = 'block';

        setTimeout(() => {
            popup.style.display = 'none';
        }, 3000);
    }
}