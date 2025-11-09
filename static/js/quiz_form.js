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
    `;
    questionsContainer.appendChild(qDiv);
    questionIndex++;
});

// Add option
questionsContainer.addEventListener('click', e => {
    if (e.target.classList.contains('add-option-btn')) {
        const qBlock = e.target.closest('.question-block');
        const idx = qBlock.dataset.index;
        const optionsContainer = qBlock.querySelector('.options-container');
        if (optionsContainer.children.length >= 4) return alert("Max 4 options");

        const oDiv = document.createElement('div');
        oDiv.classList.add('option-block');
        oDiv.innerHTML = `
            <input type="text" name="option_text_${idx}[]" placeholder="Option text" required>
            <input type="number" name="option_points_${idx}[]" placeholder="Points" value="1">
            <label>Correct? <input type="checkbox" name="option_correct_${idx}[]" value="true"></label>
        `;
        optionsContainer.appendChild(oDiv);

        updateValidation();
    }
});

// Add result range
addResultBtn.addEventListener('click', () => {
    const rDiv = document.createElement('div');
    rDiv.classList.add('result-block');
    rDiv.innerHTML = `
        <input type="number" name="result_min[]" placeholder="Min points" required>
        <input type="number" name="result_max[]" placeholder="Max points" required>
        <input type="text" name="result_text[]" placeholder="Result text" required>
    `;
    resultsContainer.appendChild(rDiv);

    updateValidation();
});

// Toggle correct checkboxes for subjective quizzes
function toggleCorrectCheckboxes() {
    const quizType = document.getElementById('quiz_type').value;
    document.querySelectorAll('.option-block').forEach(opt => {
        const correctLabel = opt.querySelector('label');
        if (correctLabel && correctLabel.textContent.includes('Correct?')) {
            const checkbox = correctLabel.querySelector('input[type="checkbox"]');
            correctLabel.style.display = (quizType === 'objective') ? 'inline-block' : 'none';
            if (quizType !== 'objective' && checkbox) checkbox.checked = false;
        }
    });
}

// Validation & tooltip
function updateValidation() {
    const questions = document.querySelectorAll('.question-block');
    const results = document.querySelectorAll('.result-block');
    const saveBtn = document.getElementById('save-quiz-btn');
    const publishBtn = document.getElementById('publish-quiz-btn');

    let valid = true;
    let message = '';

    // Check if there are no questions
    if (questions.length === 0) {
        valid = false;
        message = "Add at least one question to save or publish the quiz.";
    }

    // Check if there are no result ranges
    if (valid && results.length === 0) {
        valid = false;
        message = "Add at least one result range to save or publish the quiz.";
    }

    // Validate existing questions
    if (valid) {
        questions.forEach((q, idx) => {
            const options = q.querySelectorAll('.option-block');
            if (options.length < 2) { valid = false; message = `Question ${idx + 1} has less than 2 options.`; }
            if (options.length > 4) { valid = false; message = `Question ${idx + 1} has more than 4 options.`; }

            const quizType = document.getElementById('quiz_type').value;
            if (quizType === 'objective') {
                const hasCorrect = Array.from(options).some(opt => {
                    const checkbox = opt.querySelector('input[type="checkbox"]');
                    return checkbox ? checkbox.checked : false;
                });
                if (!hasCorrect) { valid = false; message = `Question ${idx + 1} must have at least one correct option.`; }
            }
        });
    }

    // Validate result ranges
    if (valid) {
        const ranges = [];
        results.forEach((r, idx) => {
            const min = parseInt(r.querySelector('input[name="result_min[]"]').value || 0);
            const max = parseInt(r.querySelector('input[name="result_max[]"]').value || 0);
            if (min > max) { valid = false; message = `Result range ${idx + 1} has min > max.`; }
            ranges.push({min, max});
        });

        ranges.sort((a,b) => a.min - b.min);
        for (let i = 0; i < ranges.length - 1; i++) {
            if (ranges[i].max >= ranges[i+1].min) { valid = false; message = `Result ranges ${i+1} and ${i+2} overlap.`; }
        }
    }

    // --- Update Save button ---
    if (!valid) {
        saveBtn.disabled = true;
        saveBtn.classList.add('tooltip');
        let tip = saveBtn.querySelector('.tooltiptext');
        if (!tip) {
            tip = document.createElement('span');
            tip.className = 'tooltiptext';
            saveBtn.appendChild(tip);
        }
        tip.textContent = message;
    } else {
        saveBtn.disabled = false;
        saveBtn.classList.remove('tooltip');
        const tip = saveBtn.querySelector('.tooltiptext');
        if (tip) tip.remove();
    }

    // --- Update Publish button ---
    if (publishBtn) {
        if (!valid) {
            publishBtn.disabled = true;
            publishBtn.classList.add('tooltip');
            let tip = publishBtn.querySelector('.tooltiptext');
            if (!tip) {
                tip = document.createElement('span');
                tip.className = 'tooltiptext';
                publishBtn.appendChild(tip);
            }
            tip.textContent = message;
        } else {
            publishBtn.disabled = false;
            publishBtn.classList.remove('tooltip');
            const tip = publishBtn.querySelector('.tooltiptext');
            if (tip) tip.remove();
        }
    }
}


// Delete question / option / result (frontend + backend)
document.addEventListener('click', async e => {
    // Delete question
    if (e.target.classList.contains('delete-question-btn')) {
        const qBlock = e.target.closest('.question-block');
        const qIdInput = qBlock.querySelector('input[name^="question_id_"]');
        const questionId = qIdInput ? qIdInput.value : null;

        if (questionId) {
            const res = await fetch(`/quiz/question/${questionId}/delete`, { method: 'POST' });
            if (!res.ok) return alert('Failed to delete question');
        }

        qBlock.remove();
        updateValidation();
    }

    // Delete option
    if (e.target.classList.contains('delete-option-btn')) {
        const oBlock = e.target.closest('.option-block');
        const qBlock = e.target.closest('.question-block');

        const optionIdInput = oBlock.querySelector('input[name^="option_id_"]');
        const optionId = optionIdInput ? optionIdInput.value : null;

        if (optionId) {
            const res = await fetch(`/quiz/option/${optionId}/delete`, { method: 'POST' });
            if (!res.ok) return alert('Failed to delete option');
        }

        oBlock.remove();
        updateValidation();
    }

    // Delete result
    if (e.target.classList.contains('delete-result-btn')) {
        const rBlock = e.target.closest('.result-block');
        const resultIdInput = rBlock.querySelector('input[name^="result_id_"]');
        const resultId = resultIdInput ? resultIdInput.value : null;

        if (resultId) {
            const res = await fetch(`/quiz/result/${resultId}/delete`, { method: 'POST' });
            if (!res.ok) return alert('Failed to delete result');
        }

        rBlock.remove();
        updateValidation();
    }
});

// Event listeners
document.getElementById('quiz-form').addEventListener('input', updateValidation);
document.getElementById('quiz_type').addEventListener('change', () => {
    toggleCorrectCheckboxes();
    updateValidation();
});

// Initial run
toggleCorrectCheckboxes();
updateValidation();
