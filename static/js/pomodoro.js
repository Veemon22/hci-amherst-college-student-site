document.addEventListener('DOMContentLoaded', () => {
    const timerDisplay = document.getElementById('timer-display');
    const startBtn = document.getElementById('start-btn');
    const timerLabel = document.getElementById('timer-label');

    // Pull durations from data attributes
    const pomodoroEl = document.querySelector('.pomodoro-timer');
    let workMinutes = parseInt(pomodoroEl.dataset.work);
    let shortBreak = parseInt(pomodoroEl.dataset.shortBreak);
    let longBreak = parseInt(pomodoroEl.dataset.longBreak);

    let timeLeft = workMinutes * 60;
    let timerInterval = null;
    let isWork = true;

    // Update timer display
    function updateDisplay() {
        let minutes = Math.floor(timeLeft / 60).toString().padStart(2, '0');
        let seconds = (timeLeft % 60).toString().padStart(2, '0');
        timerDisplay.textContent = `${minutes}:${seconds}`;
    }

    // Switch session type (work/break)
    function switchSession() {
        if (isWork) {
            timerLabel.textContent = "Short Break";
            timeLeft = shortBreak * 60;
        } else {
            timerLabel.textContent = "Work";
            timeLeft = workMinutes * 60;
        }
        isWork = !isWork;
        updateDisplay();
    }

    // Start the timer
    function startTimer() {
        if (timerInterval) return; // Already running
        timerInterval = setInterval(() => {
            timeLeft--;
            updateDisplay();
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                timerInterval = null;
                switchSession();
            }
        }, 1000);
    }

    // Optional: stop timer function
    function stopTimer() {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    // Event listener
    startBtn.addEventListener('click', startTimer);

    // Initialize display
    updateDisplay();
});
