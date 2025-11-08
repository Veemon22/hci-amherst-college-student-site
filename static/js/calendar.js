document.addEventListener("DOMContentLoaded", () => {
    const openAddEventBtn = document.getElementById("open-add-event-modal");
    const addEventModal = document.getElementById("addEventModal");
    const closeAddEventBtn = document.getElementById("close-add-event-modal");
    const deleteEventBtn = document.getElementById("delete-event-btn");
    const deleteModal = document.getElementById("deleteConfirmModal");
    const closeDeleteBtn = document.getElementById("close-delete-modal");
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
    const deleteEventIdInput = document.getElementById("delete-event-id");
    const deleteGcalIdInput = document.getElementById("delete-gcal-id");
    const deleteConfirmText = document.getElementById("delete-confirm-text");

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

    // Delete Event Button Logic
    if (deleteEventBtn) {
        deleteEventBtn.addEventListener("click", () => {
            const eventId = document.getElementById("modal-event-id").value;
            const gcalId = document.getElementById("modal-gcal-id").value;

            // Determine message based on type
            if (eventId && gcalId) {
                deleteConfirmText.textContent = "This event is synced with Google Calendar. It will be deleted from both. Continue?";
            } else if (eventId) {
                deleteConfirmText.textContent = "This is a guest event. It will be deleted from your calendar. Continue?";
            } else if (gcalId) {
                deleteConfirmText.textContent = "This is a Google Calendar event. It will be deleted from Google Calendar. Continue?";
            } else {
                // No valid ID, do nothing
                return;
            }

            // Set hidden form inputs
            deleteEventIdInput.value = eventId;
            deleteGcalIdInput.value = gcalId;

            // Show modal
            deleteModal.classList.remove("hidden");
        });
    }

    // Close delete modal
    if (closeDeleteBtn) {
        closeDeleteBtn.addEventListener("click", () => {
            deleteModal.classList.add("hidden");
        });
    }
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener("click", () => {
            deleteModal.classList.add("hidden");
        });
    }

    // Clicking outside closes modal
    window.addEventListener("click", (e) => {
        if (e.target === deleteModal) deleteModal.classList.add("hidden");
    });
});

function showEventModal(element) {
    const title = element.getAttribute("data-title");
    const time = element.getAttribute("data-time");
    const description = element.getAttribute("data-description");
    const eventId = element.getAttribute("data-id") || "";
    const gcalId = element.getAttribute("data-gcal-id") || "";

    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-time").textContent = time;
    document.getElementById("modal-description").textContent = description;

    document.getElementById("modal-event-id").value = eventId;
    document.getElementById("modal-gcal-id").value = gcalId;

    document.getElementById("eventModal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("eventModal").classList.add("hidden");
}
