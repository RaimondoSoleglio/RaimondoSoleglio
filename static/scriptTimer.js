document.addEventListener("DOMContentLoaded", () => {
    const timerElement = document.getElementById("timer");

    let timerCounter = {{ timer }};
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
