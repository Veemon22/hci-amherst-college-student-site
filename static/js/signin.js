function showPopup() {
    const popup = document.getElementById("error-popup");
    popup.classList.add("show");
    setTimeout(() => {
        popup.classList.remove("show");
    }, 3000);
}
