document.addEventListener("DOMContentLoaded", () => {
    const greetingEl = document.getElementById("greeting");

    if (greetingEl) {
        const hours = new Date().getHours();
        let timeGreeting = "Welcome";

        if (hours < 12) {
            timeGreeting = "Good morning";
        } else if (hours < 18) {
            timeGreeting = "Good afternoon";
        } else {
            timeGreeting = "Good evening";
        }

        // If the username is stored in a data attribute (recommended)
        const username = greetingEl.getAttribute("data-username") || "";
        greetingEl.textContent = `${timeGreeting}${username ? ", " + username : ""}!`;
    }
});
