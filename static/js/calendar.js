document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggle-add-event');
    const formContainer = document.getElementById('add-event-form-container');

    toggleBtn.addEventListener('click', function() {
        formContainer.classList.toggle('hidden');
    });
});
