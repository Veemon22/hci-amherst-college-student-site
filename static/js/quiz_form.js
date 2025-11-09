let questionIndex = document.querySelectorAll('.question-block').length;
const questionsContainer = document.getElementById('questions-container');
const addQuestionBtn = document.getElementById('add-question-btn');
const addResultBtn = document.getElementById('add-result-btn');
const resultsContainer = document.getElementById('results-container');

// Add new question
addQuestionBtn.addEventListener('click', () => {
    const qDiv = document.createElement('div');
    qDiv.classList.add('question-block');
    qDiv.dataset.index = questionIndex;
    qDiv.innerHTML = `
        <h3>Question ${questionIndex + 1}</h3>
        <textarea name="question_text[]" placeholder="Question text" required></textarea>
        <input type="text" name="question_image[]" placeholder="Question image URL">
        <div class="options-container"></div>
        <button type="button" class="add-option-btn">Add Option</button>
        <button type="button" class="delete-question-btn">Delete Question</button>
    `;
    questionsContainer.appendChild(qDiv);
    questionIndex++;
});

// Add option inside a question
questionsContainer.addEventListener('click', e => {
    const qBlock = e.target.closest('.question-block');
    const idx = qBlock ? qBlock.dataset.index : null;

    if (e.target.classList.contains('add-option-btn') && idx !== null) {
        const optionsContainer = qBlock.querySelector('.options-container');
        const oDiv = document.createElement('div');
        oDiv.classList.add('option-block');
        oDiv.innerHTML = `
            <input type="text" name="option_text_${idx}[]" placeholder="Option text" required>
            <input type="number" name="option_points_${idx}[]" placeholder="Points">
            <label>Correct? <input type="checkbox" name="option_correct_${idx}[]" value="true"></label>
            <button type="button" class="delete-option-btn">Delete Option</button>
        `;
        optionsContainer.appendChild(oDiv);
    }

    if (e.target.classList.contains('delete-option-btn')) {
        const oBlock = e.target.closest('.option-block');
        oBlock.remove();
    }

    if (e.target.classList.contains('delete-question-btn')) {
        const qBlock = e.target.closest('.question-block');
        qBlock.remove();
    }
});

// Add new result block
addResultBtn.addEventListener('click', () => {
    const rDiv = document.createElement('div');
    rDiv.classList.add('result-block');
    rDiv.innerHTML = `
        <input type="number" name="result_min[]" placeholder="Min points" required>
        <input type="number" name="result_max[]" placeholder="Max points" required>
        <input type="text" name="result_text[]" placeholder="Result text" required>
        <button type="button" class="delete-result-btn">Delete Result</button>
    `;
    resultsContainer.appendChild(rDiv);
});

// Delete existing result
resultsContainer.addEventListener('click', e => {
    if (e.target.classList.contains('delete-result-btn')) {
        const rBlock = e.target.closest('.result-block');
        rBlock.remove();
    }
});
