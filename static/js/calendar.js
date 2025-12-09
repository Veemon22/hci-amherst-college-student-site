document.addEventListener("DOMContentLoaded", () => {
    // --- All-day event checkbox logic for ADD modal ---
    const isAllDayCheckbox = document.getElementById('is-all-day-checkbox');
    const timeInputContainer = document.getElementById('time-input-container');
    const timeInput = document.getElementById('time-input');

    if (isAllDayCheckbox && timeInputContainer && timeInput) {
        isAllDayCheckbox.addEventListener('change', () => {
            if (isAllDayCheckbox.checked) {
                timeInputContainer.style.display = 'none';
                timeInput.removeAttribute('required');
            } else {
                timeInputContainer.style.display = 'block';
                timeInput.setAttribute('required', 'required');
            }
        });
    }

    // --- All-day event checkbox logic for EDIT modal ---
    const modalIsAllDayCheckbox = document.getElementById('modal-is-all-day-checkbox');
    const modalTimeContainer = document.getElementById('modal-time-container');
    const modalTimeInput = document.getElementById('modal-time-input');

    if (modalIsAllDayCheckbox && modalTimeContainer && modalTimeInput) {
        modalIsAllDayCheckbox.addEventListener('change', () => {
            if (modalIsAllDayCheckbox.checked) {
                modalTimeContainer.style.display = 'none';
            } else {
                modalTimeContainer.style.display = 'block';
            }
        });
    }

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

    const modalTitleInput = document.getElementById("modal-title-input");

    const modalDescriptionInput = document.getElementById("modal-description-input");

    // --- Day Overview Modal Elements ---
    const dayOverviewModal = document.getElementById("dayOverviewModal");
    const closeDayOverviewBtn = document.getElementById("close-day-overview-modal");
    const dayOverviewTitle = document.getElementById("day-overview-title");
    const dayOverviewEvents = document.getElementById("day-overview-events");
    const addEventFromDayBtn = document.getElementById("add-event-from-day");
    let selectedDay = null;

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
            const isAllDay = modalIsAllDayCheckbox.checked;

            if (!eventId && !gcalId) return;

            const form = document.createElement("form");
            form.method = "POST";
            form.action = "/edit_event";

            form.appendChild(createHiddenInput("event_id", eventId));
            form.appendChild(createHiddenInput("gcal_id", gcalId));
            form.appendChild(createHiddenInput("title", newTitle));
            if (!isAllDay && newTime){
                form.appendChild(createHiddenInput("time", newTime));
            }
            form.appendChild(createHiddenInput("description", newDescription));
            if (isAllDay){
                form.appendChild(createHiddenInput("is_all_day", isAllDay ? "on" : ""));
            }
            
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

    // --- Day Overview Modal Logic ---
    // Make day cells clickable
    document.querySelectorAll('.calendar-table td:not(.empty-day)').forEach(cell => {
        const dayNumber = cell.querySelector('.day-number');
        if (dayNumber) {
            dayNumber.style.cursor = 'pointer';
            dayNumber.style.textDecoration = 'underline';
            
            dayNumber.addEventListener('click', (e) => {
                e.stopPropagation();
                const day = parseInt(dayNumber.textContent);
                showDayOverview(day, cell);
            });
        }
    });

    function showDayOverview(day, cell) {
        selectedDay = day;
        
        const headerText = document.querySelector('.calendar-header h2').textContent;
        const [month, year] = headerText.split('/');
        
        dayOverviewTitle.textContent = `Events for ${month}/${day}/${year}`;
        
        const events = cell.querySelectorAll('.event');
        
        dayOverviewEvents.innerHTML = '';
        
        if (events.length === 0) {
            dayOverviewEvents.innerHTML = '<div class="no-events-message">No events scheduled for this day</div>';
        } else {
            events.forEach(event => {
                const eventDiv = document.createElement('div');
                eventDiv.className = 'day-event-item';
                
                const title = event.getAttribute('data-title');
                const time = event.getAttribute('data-time');
                const description = event.getAttribute('data-description');
                
                eventDiv.innerHTML = `
                    <div class="day-event-time">${time}</div>
                    <div class="day-event-title">${title}</div>
                    <div class="day-event-description">${description}</div>
                `;
                
                eventDiv.addEventListener('click', () => {
                    dayOverviewModal.classList.add('hidden');
                    showEventModal(event);
                });
                
                dayOverviewEvents.appendChild(eventDiv);
            });
        }
        
        dayOverviewModal.classList.remove('hidden');
    }

    if (closeDayOverviewBtn) {
        closeDayOverviewBtn.addEventListener('click', () => {
            dayOverviewModal.classList.add('hidden');
        });
    }

    if (addEventFromDayBtn) {
        addEventFromDayBtn.addEventListener('click', () => {
            dayOverviewModal.classList.add('hidden');
            
            const headerText = document.querySelector('.calendar-header h2').textContent;
            const [month, year] = headerText.split('/');
            const dateString = `${year}-${month.padStart(2, '0')}-${selectedDay.toString().padStart(2, '0')}`;
            
            document.querySelector('#add-event-form input[name="date"]').value = dateString;
            addEventModal.classList.remove('hidden');
        });
    }

    window.addEventListener('click', (e) => {
        if (e.target === dayOverviewModal) {
            dayOverviewModal.classList.add('hidden');
        }
    });
});

function showEventModal(element) {
    const title = element.getAttribute("data-title");
    const time = element.getAttribute("data-time");
    const description = element.getAttribute("data-description");
    const eventId = element.getAttribute("data-id") || "";
    const gcalId = element.getAttribute("data-gcal-id") || "";
    const isAllDay = element.getAttribute("data-is-all-day") === "True";

    document.getElementById("modal-title-input").value = title;
    document.getElementById("modal-description-input").value = description;

    const modalIsAllDayCheckbox = document.getElementById("modal-is-all-day-checkbox");
    const modalTimeContainer = document.getElementById("modal-time-container");
    const modalTimeInput = document.getElementById("modal-time-input");

    if (isAllDay) {
        modalIsAllDayCheckbox.checked = true;
        modalTimeContainer.style.display = 'none';
        modalTimeInput.value = '';
    } else {
        modalIsAllDayCheckbox.checked = false;
        modalTimeContainer.style.display = 'block';
        modalTimeInput.value = convertTimeToInputFormat(time);
    }

    document.getElementById("modal-event-id").value = eventId;
    document.getElementById("modal-gcal-id").value = gcalId;

    document.getElementById("eventModal").classList.remove("hidden");
}

function convertTimeToInputFormat(timeStr) {
    if (timeStr === "All Day") return "";
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