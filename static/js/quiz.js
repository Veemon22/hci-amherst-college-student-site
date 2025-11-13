let currentQuestion = 1;
let totalPoints = 0;

// Get quiz ID from body attribute
const quizContainer = document.getElementById('quiz-container');
const quizId = quizContainer.dataset.quizId;

// Calculate total possible points directly from DOM
let totalPossiblePoints = 0;
document.querySelectorAll('.question-block').forEach(q => {
    const optionPoints = Array.from(q.querySelectorAll('.option-btn')).map(
        o => parseInt(o.dataset.points) || 0
    );
    totalPossiblePoints += Math.max(...optionPoints);
});

const totalQuestions = document.querySelectorAll('.question-block').length;
const resultRanges = Array.from(document.querySelectorAll('#result-data div')).map(div => ({
    min: parseInt(div.dataset.min),
    max: parseInt(div.dataset.max),
    text: div.dataset.text,
    image: div.dataset.image
}));

function showQuestion(index) {
    document.querySelectorAll('.question-block').forEach((block, i) => {
        block.classList.toggle('hidden', i + 1 !== index);
    });
    document.getElementById('current-question').textContent = index;
}

document.querySelectorAll('.option-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        totalPoints += parseInt(btn.dataset.points);
        if (currentQuestion < totalQuestions) {
            currentQuestion++;
            showQuestion(currentQuestion);
        } else {
            showResult();
        }
    });
});

function showResult() {
    document.getElementById('question-section').classList.add('hidden');
    document.getElementById('progress').classList.add('hidden');

    const resultContainer = document.getElementById('result-container');
    resultContainer.classList.remove('hidden');

    const resultElements = document.querySelectorAll('#result-data div');
    let matchedResult = null;

    resultElements.forEach(r => {
        const min = parseInt(r.dataset.min);
        const max = parseInt(r.dataset.max);
        if (totalPoints >= min && totalPoints <= max) {
            matchedResult = r;
        }
    });

    const resultTitle = document.getElementById('result-title');
    const scoreDisplay = document.getElementById('score-display');
    const resultImage = document.getElementById('result-image');

    // Display user's result
    if (matchedResult) {
        resultTitle.textContent = matchedResult.dataset.text;
        scoreDisplay.textContent = `You scored ${totalPoints} out of ${totalPossiblePoints} points.`;

        if (matchedResult.dataset.image) {
            resultImage.src = `/static/${matchedResult.dataset.image}`;
            resultImage.classList.remove('hidden');
        }
    } else {
        resultTitle.textContent = "No matching result found.";
        scoreDisplay.textContent = `You scored ${totalPoints} out of ${totalPossiblePoints}.`;
    }

    // Show all possible result ranges
    const allResultsList = document.getElementById('all-results-list');
    allResultsList.innerHTML = '';
    resultElements.forEach(r => {
        const li = document.createElement('li');
        li.textContent = `${r.dataset.text} (${r.dataset.min}–${r.dataset.max} points)`;

        // Highlight user’s matched result
        if (matchedResult && r.dataset.text === matchedResult.dataset.text) {
            li.style.fontWeight = 'bold';
            li.style.color = '#5e2a8c';
        }

        allResultsList.appendChild(li);
    });

    // Send result to backend for storage
    if (quizId) {
        fetch(`/quiz/${quizId}/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                score: totalPoints,
                total: totalPossiblePoints,
                result_text: matchedResult ? matchedResult.dataset.text : "No result"
            })
        }).catch(err => console.error("Error submitting result:", err));
    }
}

// Initialize first question
showQuestion(currentQuestion);
