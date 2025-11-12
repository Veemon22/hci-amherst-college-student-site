let questionIndex = document.querySelectorAll('.question-block').length;
const questionsContainer = document.getElementById('questions-container');
const addQuestionBtn = document.getElementById('add-question-btn');
const addResultBtn = document.getElementById('add-result-btn');
const resultsContainer = document.getElementById('results-container');

// --- Add question ---
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

// --- Add option ---
questionsContainer.addEventListener('click', e => {
    const qBlock = e.target.closest('.question-block');
    if (!qBlock) return;
    const idx = qBlock.dataset.index;
    const optionsContainer = qBlock.querySelector('.options-container');

    if (e.target.classList.contains('add-option-btn')) {
        if (optionsContainer.children.length >= 4) return alert("Max 4 options");

        const oDiv = document.createElement('div');
        oDiv.classList.add('option-block');
        oDiv.innerHTML = `
            <input type="text" name="option_text_${idx}[]" placeholder="Option text" required>
            <input type="number" name="option_points_${idx}[]" placeholder="Points" value="1">
            <label class="correct-label">Correct? <input type="checkbox" name="option_correct_${idx}[]" value="true"></label>
        `;
        optionsContainer.appendChild(oDiv);

        // Attach checkbox change listener to toggle points visibility
        const checkbox = oDiv.querySelector('input[type="checkbox"]');
        const pointsInput = oDiv.querySelector(`input[name="option_points_${idx}[]"]`);
        checkbox.addEventListener('change', () => {
            pointsInput.style.display = checkbox.checked ? 'inline-block' : 'none';
        });

        updateValidation();
        toggleCorrectCheckboxes(); // ensure points visibility matches quiz type
    }
});

// --- Add result range ---
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

// --- Toggle correct checkboxes and points visibility ---
function toggleCorrectCheckboxes() {
    const quizType = document.getElementById('quiz_type').value;

    document.querySelectorAll('.option-block').forEach(opt => {
        const correctLabel = opt.querySelector('label');
        if (correctLabel && correctLabel.textContent && correctLabel.textContent.includes('Correct?')) {
            const checkbox = correctLabel.querySelector('input[type="checkbox"]');
            if (quizType === 'objective') {
                correctLabel.style.display = 'inline-block';
                if (checkbox) {
                    opt.querySelector('input[type="number"]').style.display = checkbox.checked ? 'inline-block' : 'none';
                }
            } else { // subjective
                correctLabel.style.display = 'none';
                if (checkbox) checkbox.checked = false;
                const pointsInput = opt.querySelector('input[type="number"]');
                if (pointsInput) pointsInput.style.display = 'inline-block';
            }
        } else {
            // If there is no label or checkbox, just make sure points input is visible
            const pointsInput = opt.querySelector('input[type="number"]');
            if (pointsInput) pointsInput.style.display = 'inline-block';
        }
    });
}

// --- Validation & tooltip ---
function updateValidation() {
    const questions = document.querySelectorAll('.question-block');
    const saveBtn = document.getElementById('save-quiz-btn');
    const publishBtn = document.getElementById('publish-quiz-btn');

    let valid = true;
    let message = '';

    // Validate questions
    if (questions.length === 0) {
        valid = false;
        message = "You must add at least one question.";
    } else {
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
    const results = document.querySelectorAll('.result-block');
    if (results.length === 0) {
        valid = false;
        message = "You must add at least one result range.";
    } else {
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

    // --- Save button tooltip ---
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

    // --- Publish button tooltip (if exists) ---
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

// --- Event listeners ---
document.getElementById('quiz-form').addEventListener('input', updateValidation);
document.getElementById('quiz_type').addEventListener('change', () => {
    toggleCorrectCheckboxes();
    updateValidation();
});

// --- Initial run ---
toggleCorrectCheckboxes();
updateValidation();
