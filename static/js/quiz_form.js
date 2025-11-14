let questionIndex = document.querySelectorAll('.question-block').length;
const questionsContainer = document.getElementById('questions-container');
const addQuestionBtn = document.getElementById('add-question-btn');
const addResultBtn = document.getElementById('add-result-btn');
const resultsContainer = document.getElementById('results-container');

// Add question
addQuestionBtn.addEventListener('click', () => {
    const qDiv = document.createElement('div');
    qDiv.classList.add('question-block');
    qDiv.dataset.index = questionIndex;
    qDiv.innerHTML = `
        <h3>Question ${questionIndex + 1}</h3>
        <input type="text" name="question_text_${questionIndex}" placeholder="Question text" required>
        <input type="file" name="question_image_${questionIndex}" accept="image/*">
        <div class="options-container"></div>
        <button type="button" class="add-option-btn">Add Option</button>
        <button type="button" class="delete-question-btn">Delete Question</button>
    `;
    questionsContainer.appendChild(qDiv);
    questionIndex++;
});

// Add/delete option/question/result
document.addEventListener('click', e => {
    const qBlock = e.target.closest('.question-block');
    const rBlock = e.target.closest('.result-block');

    // Add option
    if (e.target.classList.contains('add-option-btn') && qBlock) {
        const idx = qBlock.dataset.index;
        const optionsContainer = qBlock.querySelector('.options-container');
        if (optionsContainer.children.length >= 4) return alert("Max 4 options");

        const oDiv = document.createElement('div');
        oDiv.classList.add('option-block');
        oDiv.innerHTML = `
            <input type="text" name="option_text_${idx}[]" placeholder="Option text" required>
            <label>Points</label>
            <input type="number" name="option_points_${idx}[]" placeholder="Points" value="1">
            <label class="correct-label">Correct?
                <input type="checkbox" name="option_correct_${idx}[]" value="true">
            </label>
            <button type="button" class="delete-option-btn">Delete Option</button>
        `;
        optionsContainer.appendChild(oDiv);
        toggleCorrectCheckboxes();
        updateValidation();
    }

    // Delete option
    if (e.target.classList.contains('delete-option-btn') && e.target.closest('.option-block')) {
        e.target.closest('.option-block').remove();
        updateValidation();
    }

    // Delete question
    if (e.target.classList.contains('delete-question-btn') && qBlock) {
        qBlock.remove();
        updateValidation();
    }

    // Delete result
    if (e.target.classList.contains('delete-result-btn') && rBlock) {
        rBlock.remove();
        updateValidation();
    }
});

// Add result
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
    updateValidation();
});

// Toggle correct checkboxes and points
function toggleCorrectCheckboxes() {
    const quizType = document.getElementById('quiz_type').value;
    document.querySelectorAll('.option-block').forEach(opt => {
        const checkbox = opt.querySelector('input[type="checkbox"]');
        const pointsInput = opt.querySelector('input[type="number"]');
        const label = opt.querySelector('.correct-label');
        if (quizType === 'objective') {
            if (label) label.style.display = 'inline-block';
            if (checkbox && pointsInput) pointsInput.style.display = checkbox.checked ? 'inline-block' : 'none';
        } else {
            if (label) label.style.display = 'none';
            if (checkbox) checkbox.checked = false;
            if (pointsInput) pointsInput.style.display = 'inline-block';
        }
    });
}

// Dynamically show points on checkbox change
document.addEventListener('change', e => {
    if (e.target.type === 'checkbox' && e.target.closest('.option-block')) {
        const quizType = document.getElementById('quiz_type').value;
        const pointsInput = e.target.closest('.option-block').querySelector('input[type="number"]');
        if (quizType === 'objective') pointsInput.style.display = e.target.checked ? 'inline-block' : 'none';
    }
});

// Validation and hover tooltip for Save/Publish
function updateValidation() {
    const questions = document.querySelectorAll('.question-block');
    const results = document.querySelectorAll('.result-block');

    const saveBtn = document.getElementById('save-quiz-btn');
    const publishBtn = document.getElementById('publish-quiz-btn');

    let valid = true;
    let message = '';

    const quizType = document.getElementById('quiz_type').value;

    // ----------------------------
    // 1. Validate Questions
    // ----------------------------
    if (valid && questions.length === 0) {
        valid = false;
        message = "You must add at least one question.";
    }

    if (valid) {
        questions.forEach((q, idx) => {
            if (!valid) return;

            const options = q.querySelectorAll('.option-block');

            if (options.length < 2) {
                valid = false;
                message = `Question ${idx + 1} has less than 2 options.`;
                return;
            }

            if (options.length > 4) {
                valid = false;
                message = `Question ${idx + 1} has more than 4 options.`;
                return;
            }

            if (quizType === 'objective') {
                const hasCorrect = Array.from(options)
                    .some(opt => opt.querySelector('input[type="checkbox"]')?.checked);

                if (!hasCorrect) {
                    valid = false;
                    message = `Question ${idx + 1} must have at least one correct option.`;
                }
            }
        });
    }

    // ----------------------------
    // 2. Validate Result Ranges
    // ----------------------------
    if (valid && results.length === 0) {
        valid = false;
        message = "You must add at least one result range.";
    }

    if (valid) {
        const ranges = [];

        results.forEach((r, idx) => {
            if (!valid) return;

            const minInput = r.querySelector('input[name="result_min[]"]');
            const maxInput = r.querySelector('input[name="result_max[]"]');

            const min = parseInt(minInput.value);
            const max = parseInt(maxInput.value);

            if (isNaN(min) || isNaN(max)) {
                valid = false;
                message = `Result range ${idx + 1} must have both min and max.`;
                return;
            }

            if (min > max) {
                valid = false;
                message = `Result range ${idx + 1} has min greater than max.`;
                return;
            }

            ranges.push({ min, max, index: idx + 1 });
        });

        // Sort ranges by minimum value
        ranges.sort((a, b) => a.min - b.min);

        // Check for overlaps
        for (let i = 0; i < ranges.length - 1 && valid; i++) {
            const current = ranges[i];
            const next = ranges[i + 1];

            // Overlap occurs if max > next.min (NOT >=)
            if (current.max > next.min) {
                valid = false;
                message = `Result ranges ${current.index} and ${next.index} overlap.`;
            }
        }
    }

    // ----------------------------
    // 3. Apply Button States / Tooltips
    // ----------------------------
    [saveBtn, publishBtn].forEach(btn => {
        if (!btn) return;
        const tip = btn.querySelector('.tooltiptext');

        if (!valid) {
            btn.disabled = true;
            btn.classList.add('tooltip');
            if (tip) tip.textContent = message;
        } else {
            btn.disabled = false;
            btn.classList.remove('tooltip');
            if (tip) tip.textContent = '';
        }
    });
}
