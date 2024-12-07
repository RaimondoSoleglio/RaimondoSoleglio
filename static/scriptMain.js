document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("search"); // The input field
    const suggestionBox = document.getElementById("results"); // The suggestion box
    const hiddenField = document.getElementById("selected_movie_id"); // Hidden input for movie ID
    const timerElement = document.getElementById("timer");
    let remainingTime = parseInt(timerElement.dataset.timer);
    let currentIndex = -1; // To track highlighted suggestion

    // Fetch results on input
    inputField.addEventListener("input", () => fetchResults());

    // Handle keyboard navigation
    inputField.addEventListener("keydown", (e) => {
        const suggestions = suggestionBox.querySelectorAll("li");

        if (e.key === "ArrowDown") {
            e.preventDefault();
            currentIndex = (currentIndex + 1) % suggestions.length;
            highlightSuggestion(suggestions, currentIndex);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            currentIndex = (currentIndex - 1 + suggestions.length) % suggestions.length;
            highlightSuggestion(suggestions, currentIndex);
        } else if (e.key === "Enter") {
            e.preventDefault();
            if (currentIndex >= 0 && suggestions[currentIndex]) {
                suggestions[currentIndex].click(); // Trigger the click behavior programmatically
            }
        }
    });

    // Fetch suggestions via AJAX
    function fetchResults() {
        const query = inputField.value.trim();
        if (!query) {
            suggestionBox.innerHTML = ""; // Clear suggestions if input is empty
            return;
        }

        fetch(`/query?q=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((data) => {
                suggestionBox.innerHTML = ""; // Clear previous suggestions
                currentIndex = -1; // Reset the highlighted index

                data.forEach((movie) => {
                    const listItem = document.createElement("li");
                    listItem.textContent = movie.title;
                    listItem.dataset.id = movie.id; // Store the movie ID
                    listItem.classList.add("suggestion");

                    // Behavior when a suggestion is clicked
                    listItem.onclick = () => {
                        inputField.value = movie.title;
                        hiddenField.value = movie.id; // Set the hidden input value
                        suggestionBox.innerHTML = ""; // Clear suggestions
                        document.forms[0].submit(); // Submit the form
                    };

                    suggestionBox.appendChild(listItem);
                });
            });
    }

    // Highlight the currently selected suggestion
    function highlightSuggestion(suggestions, index) {
        suggestions.forEach((item, i) => {
            item.classList.toggle("highlight", i === index);
        });
    }
});
