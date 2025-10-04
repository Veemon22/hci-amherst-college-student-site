document.getElementById('toggle-add-event').addEventListener('click', function () {
    const formContainer = document.getElementById('add-event-form-container');
    formContainer.classList.toggle('hidden');
});

function showEventModal(element) {
    const title = element.getAttribute('data-title');
    const time = element.getAttribute('data-time');
    const description = element.getAttribute('data-description');

    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-time').textContent = time;
    document.getElementById('modal-description').textContent = description;

    document.getElementById('eventModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('eventModal').classList.add('hidden');
}