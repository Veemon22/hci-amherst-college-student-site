// === Show "Add Event" Modal ===
document.addEventListener("DOMContentLoaded", () => {
    const openAddEventBtn = document.getElementById("open-add-event-modal");
    const addEventModal = document.getElementById("addEventModal");
    const closeAddEventBtn = document.getElementById("close-add-event-modal");

    if (openAddEventBtn && addEventModal) {
        openAddEventBtn.addEventListener("click", () => {
            addEventModal.classList.remove("hidden");
        });
    }

    if (closeAddEventBtn) {
        closeAddEventBtn.addEventListener("click", () => {
            addEventModal.classList.add("hidden");
        });
    }

    // Optional: Close when clicking outside modal content
    window.addEventListener("click", (e) => {
        if (e.target === addEventModal) {
            addEventModal.classList.add("hidden");
        }
    });
});

// === Show Event Details Modal ===
function showEventModal(element) {
    const title = element.getAttribute("data-title");
    const time = element.getAttribute("data-time");
    const description = element.getAttribute("data-description");

    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-time").textContent = time;
    document.getElementById("modal-description").textContent = description;

    document.getElementById("eventModal").classList.remove("hidden");
}

// === Close Event Details Modal ===
function closeModal() {
    document.getElementById("eventModal").classList.add("hidden");
}
