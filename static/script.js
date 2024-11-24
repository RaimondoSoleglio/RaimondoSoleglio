document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("search"); // The input field
    const suggestionBox = document.getElementById("results"); // The suggestion box
    const hiddenField = document.getElementById("selected_movie_id"); // Hidden input for movie ID
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



    // for the start.html

    // JavaScript for dynamic form behavior
    const numPlayersDropdown = document.getElementById('num_players');
    const playerNamesSection = document.getElementById('player-names-section');
    const timerSection = document.getElementById('timer-section');
    const timerDropdown = document.getElementById('timer');
    const playerList = document.getElementById('player-list');
    const playerLabel = document.getElementById('player-label');
    const addPlayerButton = document.getElementById('add-player');
    const playerNameInput = document.getElementById('player_name');
    const submitButton = document.getElementById('submit-button');

    let playerNames = [];
    let maxPlayers = 0;

    // Regex for valid player names (alphanumeric, max 10 characters)
    const nameRegex = /^[a-zA-Z0-9]{1,10}$/;

    // Handle number of players selection
    numPlayersDropdown.addEventListener('change', () => {
        maxPlayers = parseInt(numPlayersDropdown.value);
        playerNames = [];
        playerList.innerHTML = ''; // Clear the list
        playerNamesSection.style.display = 'block';
        playerNameInput.setAttribute('required', 'required');
        playerLabel.textContent = 'Player 1 Name:';
        timerSection.style.display = 'none';
        submitButton.style.display = 'none';
    });

    // Add player names
    playerNameInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            addPlayerButton.click();
        }
    });

        addPlayerButton.addEventListener('click', () => {
            const playerName = playerNameInput.value.trim();
            if (!nameRegex.test(playerName)) {
                alert("Invalid name! Use only letters or numbers, and ensure it's 1-10 characters long.");
                return;
            }

            playerNames.push(playerName);
            const listItem = document.createElement('li');
            listItem.textContent = playerName;
            listItem.className = 'list-group-item';
            playerList.appendChild(listItem);

            playerNameInput.value = '';
            if (playerNames.length < maxPlayers) {
                playerLabel.textContent = `Player ${playerNames.length + 1} Name:`;
            } else {
                playerLabel.style.display = 'none';
                playerNameInput.style.display = 'none';
                playerNameInput.removeAttribute('required');
                addPlayerButton.style.display = 'none';
                timerSection.style.display = 'inline';
            }
        });

        // Enter button appears after Timer selection

        timerDropdown.addEventListener('change', () => {
            submitButton.style.display = 'inline';
        });
    }
});
