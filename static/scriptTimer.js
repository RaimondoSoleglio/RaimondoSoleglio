document.addEventListener("DOMContentLoaded", () => {
    const timerElement = document.getElementById("timer");
    const lightbox = document.getElementById("lightbox");
    const lightboxMessage = document.getElementById("lightbox-message");
    const countdownElement = document.getElementById("countdown");

    let timerCounter = parseInt(timerElement.dataset.timer, 10);
    let interval;
    let isPaused = true;

    // Function to start the timer
    function startTimer() {
        isPaused = false;

        interval = setInterval(() => {
            if (timerCounter <= 1) {
                clearInterval(interval);
                showLightbox("Time over! You lost a life. Ready?");
                return;
            }

            timerCounter--;
            timerElement.innerText = timerCounter + "s";
        }, 1000);
    }

    // Function to pause the timer
    function pauseTimer() {
        clearInterval(interval);
        isPaused = true;
    }

    // Function to show the lightbox with countdown
    function showLightbox(message) {
        pauseTimer();
        lightboxMessage.textContent = message;
        countdownElement.textContent = ""; // Reset the countdown text
        lightbox.style.display = "flex";

        // Start the 3-2-1 countdown
        let count = 3;
        const countdownInterval = setInterval(() => {
            countdownElement.textContent = count;
            count--;

            if (count < 0) {
                clearInterval(countdownInterval);
                lightbox.style.display = "none"; // Hide the lightbox
                startTimer(); // Resume the game timer
            }
        }, 1000);
    }

    // Initial lightbox for player readiness
    showLightbox("Bob ready?");
});
