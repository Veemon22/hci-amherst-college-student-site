document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.querySelector(".username-menu-toggle");
    const dropdown = document.querySelector(".username-dropdown");

    toggle.addEventListener("click", function(e) {
        dropdown.classList.toggle("show");
    });

    // Optional: close dropdown if clicking outside
    window.addEventListener("click", function(e) {
        if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove("show");
        }
    });
});
