document.addEventListener("DOMContentLoaded", function () {
  const timerDisplay = document.getElementById("timer-display");
  const timerLabel = document.getElementById("timer-label");
  const startBtn = document.getElementById("start-btn");
  const completeForm = document.querySelector('form input[value="complete_pomodoro"]').closest("form");
  const completeBtn = document.getElementById("complete-btn");
  const phaseButtons = document.querySelectorAll(".phase-btn");

  const timerElement = document.querySelector(".timer-card");
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
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
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

  // Phase button click
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

  // Submit "Complete" to backend
  completeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearInterval(timer);
    isRunning = false;
    startBtn.textContent = "Start";

    try {
      const formData = new FormData(completeForm);
      const response = await fetch(window.location.href, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        // Refresh page to update pomodoro state and task counts
        window.location.reload();
      } else {
        alert("Error completing Pomodoro.");
      }
    } catch (err) {
      console.error("Error completing Pomodoro:", err);
    }
  });

  startBtn.addEventListener("click", toggleTimer);
  updateDisplay();
  setActivePhase(currentPhase);
});