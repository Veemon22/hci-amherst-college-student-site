document.addEventListener("DOMContentLoaded", function () {
  const timerDisplay = document.getElementById("timer-display");
  const timerLabel = document.getElementById("timer-label");
  const startBtn = document.getElementById("start-btn");
  const completeBtn = document.getElementById("complete-btn");
  const phaseButtons = document.querySelectorAll(".phase-btn");

  const timerElement = document.querySelector(".pomodoro-timer");
  const WORK = parseInt(timerElement.dataset.work) * 60;
  const SHORT = parseInt(timerElement.dataset.shortBreak) * 60;
  const LONG = parseInt(timerElement.dataset.longBreak) * 60;
  let currentPhase = timerElement.dataset.currentType;

  let timeLeft = getDuration(currentPhase);
  let isRunning = false;
  let timer;

  function getDuration(phase) {
    return phase === "work" ? WORK : phase === "short_break" ? SHORT : LONG;
  }

  function formatTime(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? "0" + s : s}`;
  }

  function updateDisplay() {
    timerDisplay.textContent = formatTime(timeLeft);
    timerLabel.textContent = currentPhase.replace("_", " ").toUpperCase();
    completeBtn.textContent =
      currentPhase === "work" ? "Complete Work" : "Complete Break";
  }

  function setActivePhase(phase) {
    phaseButtons.forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.phase === phase);
    });
  }

  function toggleTimer() {
    if (!isRunning) {
      isRunning = true;
      startBtn.textContent = "Pause";
      timer = setInterval(() => {
        timeLeft--;
        updateDisplay();
        if (timeLeft <= 0) {
          clearInterval(timer);
          isRunning = false;
          startBtn.textContent = "Start";
          alert(`${currentPhase.replace("_", " ")} complete!`);
        }
      }, 1000);
    } else {
      clearInterval(timer);
      isRunning = false;
      startBtn.textContent = "Resume";
    }
  }

  phaseButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      clearInterval(timer);
      isRunning = false;
      startBtn.textContent = "Start";
      currentPhase = btn.dataset.phase;
      timeLeft = getDuration(currentPhase);
      setActivePhase(currentPhase);
      updateDisplay();
    });
  });

  startBtn.addEventListener("click", toggleTimer);
  updateDisplay();
  setActivePhase(currentPhase);
});
