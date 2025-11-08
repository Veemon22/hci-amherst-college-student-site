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

    window.addEventListener("click", (e) => {
        if (e.target === addEventModal) {
            addEventModal.classList.add("hidden");
        }
    });

    // --- Sync Confirmation Modal ---
    const syncModal = document.getElementById("syncConfirmModal");
    const openSyncBtn = document.getElementById("open-sync-all-modal");
    const closeSyncBtn = document.getElementById("close-sync-modal");
    const cancelSyncBtn = document.getElementById("cancel-sync-btn");

    if (openSyncBtn && syncModal) {
        openSyncBtn.addEventListener("click", () => {
            syncModal.classList.remove("hidden");
        });
    }

    if (closeSyncBtn) {
        closeSyncBtn.addEventListener("click", () => {
            syncModal.classList.add("hidden");
        });
    }

    if (cancelSyncBtn) {
        cancelSyncBtn.addEventListener("click", () => {
            syncModal.classList.add("hidden");
        });
    }

    // Close modal if clicking outside of it
    window.addEventListener("click", (e) => {
        if (e.target === syncModal) {
            syncModal.classList.add("hidden");
        }
    });
});

function showEventModal(element) {
    const title = element.getAttribute("data-title");
    const time = element.getAttribute("data-time");
    const description = element.getAttribute("data-description");

    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-time").textContent = time;
    document.getElementById("modal-description").textContent = description;

    document.getElementById("eventModal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("eventModal").classList.add("hidden");
}
