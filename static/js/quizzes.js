document.addEventListener("DOMContentLoaded", () => {
    const quizCards = document.querySelectorAll(".quiz-card");

    quizCards.forEach(card => {
        const publishBtn = card.querySelector('form button[type="submit"].tooltip');
        if (!publishBtn) return; // skip published/unpublished buttons

        // Extract quiz data from DOM (you may need to add data attributes if needed)
        const quizId = publishBtn.dataset.quizId;

        // For simplicity, we rely on the server providing the quiz questions/options/results in a JSON dataset
        // For example: <div class="quiz-card" data-questions='[...]' data-results='[...]'>
        const questionsData = JSON.parse(card.dataset.questions || "[]");
        const resultsData = JSON.parse(card.dataset.results || "[]");
        const quizType = card.dataset.quizType || "objective";

        let reason = null;

        if (questionsData.length === 0) {
            reason = "Quiz has no questions.";
        } else if (resultsData.length === 0) {
            reason = "Quiz has no result ranges.";
        } else {
            // Check questions
            for (let i = 0; i < questionsData.length; i++) {
                const q = questionsData[i];
                if (!q.options || q.options.length < 2) {
                    reason = `Question ${i + 1} has fewer than 2 options.`;
                    break;
                }
                if (q.options.length > 4) {
                    reason = `Question ${i + 1} has more than 4 options.`;
                    break;
                }
                if (quizType === "objective" && !q.options.some(o => o.is_correct)) {
                    reason = `Question ${i + 1} has no correct option.`;
                    break;
                }
            }

            // Check result ranges
            if (!reason) {
                const sortedRanges = resultsData
                    .map(r => ({ min: parseInt(r.min), max: parseInt(r.max) }))
                    .sort((a, b) => a.min - b.min);
                for (let i = 0; i < sortedRanges.length - 1; i++) {
                    if (sortedRanges[i].max >= sortedRanges[i + 1].min) {
                        reason = `Result ranges ${i + 1} and ${i + 2} overlap.`;
                        break;
                    }
                }
            }
        }

        if (reason) {
            publishBtn.disabled = true;
            const tooltip = publishBtn.querySelector(".tooltiptext");
            if (tooltip) tooltip.textContent = reason;
        } else {
            publishBtn.disabled = false;
            const tooltip = publishBtn.querySelector(".tooltiptext");
            if (tooltip) tooltip.textContent = "Ready to publish!";
        }
    });
});
