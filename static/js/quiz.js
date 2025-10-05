let currentQuestion = 0;
let totalPoints = 0;

// Show initial question
document.getElementById('progress').classList.remove('hidden');
loadQuestion(currentQuestion);

function loadQuestion(index) {
    const question = quizData.questions[index];

    // Update progress
    document.getElementById('current-question').textContent = index + 1;

    // Question text
    document.getElementById('question-text').textContent = question.question;

    // Question image
    const qImage = document.getElementById('question-image');
    if (question.image) {
        qImage.src = `/static/${question.image}`;
        qImage.classList.remove('hidden');
    } else {
        qImage.classList.add('hidden');
    }

    // Options
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = ''; // clear previous
    question.options.forEach(option => {
        const btn = document.createElement('button');
        btn.textContent = option.text;
        btn.classList.add('option-btn');
        btn.onclick = () => handleAnswer(option.points);
        optionsContainer.appendChild(btn);
    });
}

function handleAnswer(points) {
    totalPoints += points;
    currentQuestion++;

    if (currentQuestion < quizData.questions.length) {
        loadQuestion(currentQuestion);
    } else {
        showResult();
    }
}

function showResult() {
    // Hide question section
    document.getElementById('question-section').classList.add('hidden');
    document.getElementById('progress').classList.add('hidden');

    // Show result section
    const resultContainer = document.getElementById('result-container');
    resultContainer.classList.remove('hidden');

    // Determine result based on points
    let result;
    for (let r of quizData.results) {
        if (totalPoints >= r.min_points && totalPoints <= r.max_points) {
            result = r;
            break;
        }
    }

    document.getElementById('result-title').textContent = result.text;

    // Optional: result image if included
    const rImage = document.getElementById('result-image');
    if (result.image) {
        rImage.src = `/static/${result.image}`;
        rImage.classList.remove('hidden');
    } else {
        rImage.classList.add('hidden');
    }
}
