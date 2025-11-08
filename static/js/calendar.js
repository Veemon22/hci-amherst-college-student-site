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
    const saveEventBtn = document.getElementById("save-event-btn");

    const modalTitleInput = document.getElementById("modal-title-input"); // New input for editable title
    const modalTimeInput = document.getElementById("modal-time-input");
    const modalDescriptionInput = document.getElementById("modal-description-input");

    // --- Add Event Modal ---
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
        if (e.target === addEventModal) addEventModal.classList.add("hidden");
    });

    // --- Sync Confirmation Modal ---
    const syncModal = document.getElementById("syncConfirmModal");
    const openSyncBtn = document.getElementById("open-sync-all-modal");
    const closeSyncBtn = document.getElementById("close-sync-modal");
    const cancelSyncBtn = document.getElementById("cancel-sync-btn");

    if (openSyncBtn && syncModal) openSyncBtn.addEventListener("click", () => syncModal.classList.remove("hidden"));
    if (closeSyncBtn) closeSyncBtn.addEventListener("click", () => syncModal.classList.add("hidden"));
    if (cancelSyncBtn) cancelSyncBtn.addEventListener("click", () => syncModal.classList.add("hidden"));
    window.addEventListener("click", (e) => {
        if (e.target === syncModal) syncModal.classList.add("hidden");
    });

    // --- Delete Event Button Logic ---
    if (deleteEventBtn) {
        deleteEventBtn.addEventListener("click", () => {
            const eventId = document.getElementById("modal-event-id").value;
            const gcalId = document.getElementById("modal-gcal-id").value;

            if (!eventId && !gcalId) return;

            if (eventId && gcalId) {
                deleteConfirmText.textContent = "This event is synced with Google Calendar. It will be deleted from both. Continue?";
            } else if (eventId) {
                deleteConfirmText.textContent = "This is a guest event. It will be deleted from your calendar. Continue?";
            } else if (gcalId) {
                deleteConfirmText.textContent = "This is a Google Calendar event. It will be deleted from Google Calendar. Continue?";
            }

            deleteEventIdInput.value = eventId;
            deleteGcalIdInput.value = gcalId;

            deleteModal.classList.remove("hidden");
        });
    }

    // --- Save Event Button Logic ---
    if (saveEventBtn) {
        saveEventBtn.addEventListener("click", () => {
            const eventId = document.getElementById("modal-event-id").value;
            const gcalId = document.getElementById("modal-gcal-id").value;
            const newTitle = modalTitleInput.value;
            const newTime = modalTimeInput.value;
            const newDescription = modalDescriptionInput.value;

            if (!eventId && !gcalId) return;

            const form = document.createElement("form");
            form.method = "POST";
            form.action = "/edit_event";

            form.appendChild(createHiddenInput("event_id", eventId));
            form.appendChild(createHiddenInput("gcal_id", gcalId));
            form.appendChild(createHiddenInput("title", newTitle));
            form.appendChild(createHiddenInput("time", newTime));
            form.appendChild(createHiddenInput("description", newDescription));

            document.body.appendChild(form);
            form.submit();
        });
    }

    // --- Import Google Calendar Modal ---
    const importModal = document.getElementById("importGcalModal");
    const openImportBtn = document.getElementById("open-import-gcal-modal");
    const closeImportBtn = document.getElementById("close-import-modal");
    const cancelImportBtn = document.getElementById("cancel-import-btn");

    if (openImportBtn && importModal) {
        openImportBtn.addEventListener("click", () => {
            importModal.classList.remove("hidden");
        });
    }

    if (closeImportBtn) {
        closeImportBtn.addEventListener("click", () => {
            importModal.classList.add("hidden");
        });
    }

    if (cancelImportBtn) {
        cancelImportBtn.addEventListener("click", () => {
            importModal.classList.add("hidden");
        });
    }

    // Close modal if clicking outside of it
    window.addEventListener("click", (e) => {
        if (e.target === importModal) {
            importModal.classList.add("hidden");
        }
    });


    // --- Delete Modal Close Logic ---
    if (closeDeleteBtn) closeDeleteBtn.addEventListener("click", () => deleteModal.classList.add("hidden"));
    if (cancelDeleteBtn) cancelDeleteBtn.addEventListener("click", () => deleteModal.classList.add("hidden"));
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

    document.getElementById("modal-title-input").value = title;
    document.getElementById("modal-time-input").value = convertTimeToInputFormat(time);
    document.getElementById("modal-description-input").value = description;

    document.getElementById("modal-event-id").value = eventId;
    document.getElementById("modal-gcal-id").value = gcalId;

    document.getElementById("eventModal").classList.remove("hidden");
}

function convertTimeToInputFormat(timeStr) {
    const [hourMin, period] = timeStr.split(" ");
    let [hours, minutes] = hourMin.split(":").map(Number);
    if (period === "PM" && hours !== 12) hours += 12;
    if (period === "AM" && hours === 12) hours = 0;
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

function closeModal() {
    document.getElementById("eventModal").classList.add("hidden");
}

function createHiddenInput(name, value) {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = name;
    input.value = value;
    return input;
}
