document.addEventListener("DOMContentLoaded", () => {
    const timerElement = document.getElementById("timer");
    const lightbox = document.getElementById("lightbox");
    const lightboxMessage = document.getElementById("lightbox-message");
    const countdownElement = document.getElementById("countdown");

    let timerCounter = parseInt(timerElement.dataset.timer, 10);
    let interval;
    let isPaused = true;
    let timerHandled = false; // Flag to prevent re-triggering actions


    // Function to start the timer
    function startTimer() {
        clearInterval(interval); // Clear any existing timer
        isPaused = false; // Reset the pause state

        interval = setInterval(() => {
            timerCounter--;
            if (timerCounter <= 0) {
                clearInterval(interval);
                timerElement.innerText = "0s"; // Ensure it displays "0s" before any processing
                setTimeout(() => { // Small delay to ensure UI updates before redirect
                    window.location.href = '/loseLife';
                }, 100);
            }

            timerElement.innerText = `${timerCounter}s`;
        }, 1000);
    }

    // Function to pause the timer
    function pauseTimer() {
        clearInterval(interval);
        isPaused = true;
    }

    // Function to show the lightbox with countdown
    function showLightbox(message) {
        pauseTimer(); // Pause the timer when showing the lightbox
        lightboxMessage.textContent = message;
        countdownElement.textContent = ""; // Reset countdown text
        lightbox.style.display = "flex";

        // Hide actor name
        const actorContainer = document.getElementById("actor-container");
        actorContainer.classList.remove("visible");
        actorContainer.classList.add("hidden");

        // Start the 3-2-1 countdown
        let count = 3;
        countdownElement.textContent = count; // Display "3" immediately
        const countdownInterval = setInterval(() => {
            countdownElement.textContent = count;
            count--;

            if (count < 0) {
                clearInterval(countdownInterval);
                lightbox.style.display = "none"; // Hide the lightbox

                // Show actor name
                actorContainer.classList.remove("hidden");
                actorContainer.classList.add("visible");

                // Auto-focus the input field
                const inputField = document.getElementById("search");
                inputField.disabled = false; // Ensure the field is enabled
                inputField.focus(); // Focus the input field

                startTimer(); // Resume the game timer
            }
        }, 1000);
    }

    // Show the lightbox if there's an initial message
    const message = window.gameData?.message || null; // Fetch dynamic message
    if (message) {
        showLightbox(message); // Trigger the lightbox display
    }
});


