/*
document.addEventListener("DOMContentLoaded", () => {
    const timerElement = document.getElementById("timer");

    let timerCounter = parseInt(timerElement.dataset.timer, 10);
    console.log(timerCounter);
    const interval = setInterval(() => {
        if (timerCounter <= 1) {
            clearInterval(interval);
            // go to EndOfTurn route?
        }

        timerCounter = timerCounter - 1;
        timerElement.innerText = timerCounter + "s";
    }, 1000);
});
*/

document.addEventListener("DOMContentLoaded", () => {
    const timerElement = document.getElementById("timer");
    let timerCounter = parseInt(timerElement.dataset.timer, 10); // Get timer value from data attribute
    const sessionId = "{{ session_id }}"; // Pass session ID from Jinja

    function updateTimerDisplay() {
        timerElement.textContent = `${timerCounter}s`;
    }

    function handleTimerEnd() {
        // Send an AJAX request to update lives and move to the next player
        fetch("/timer_end", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ session_id: sessionId }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Failed to update player status.");
                }
                return response.json();
            })
            .then((data) => {
                // Update UI with the new player and lives
                if (data.game_over) {
                    alert("Game Over! Reloading...");
                    window.location.href = "/end";
                } else {
                    timerCounter = data.timer; // Reset timer
                    updateTimerDisplay();
                    alert(`Next player: ${data.next_player.name} (${data.next_player.lives} lives)`);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An error occurred. Please try again.");
            });
    }

    function startCountdown() {
        const interval = setInterval(() => {
            if (timerCounter > 0) {
                timerCounter--;
                updateTimerDisplay();
            } else {
                clearInterval(interval);
                handleTimerEnd();
            }
        }, 1000);
    }

    // Start the timer
    startCountdown();
});


