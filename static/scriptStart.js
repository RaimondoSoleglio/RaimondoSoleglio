document.addEventListener("DOMContentLoaded", () => {

    // JavaScript for dynamic form behavior
    const numPlayersDropdown = document.getElementById('num_players');
    const numPlayersButton = document.getElementById('add-number');
    const playerNamesSection = document.getElementById('player-names-section');
    const timerSection = document.getElementById('timer-section');
    const timerDropdown = document.getElementById('timer');
    const playerList = document.getElementById('player-list');
    const playerLabel = document.getElementById('player-label');
    const addPlayerButton = document.getElementById('add-player');
    const playerNameInput = document.getElementById('player_name');
    const submitButton = document.getElementById('submit-button');
    const form = document.getElementById('setup-form')


    let playerNames = [];
    let maxPlayers = 0;

    // Regex for valid player names (alphanumeric, max 10 characters)
    const nameRegex = /^[a-zA-Z0-9]{1,10}$/;

    // Handle number of players selection
    numPlayersButton.addEventListener('click', () => {
        if (numPlayersDropdown.value === "") {
            alert("Insert 1 to 4 players.");
            return;
        }

        maxPlayers = parseInt(numPlayersDropdown.value);
        playerNames = [];
        playerList.innerHTML = ''; // Clear the list
        playerNamesSection.style.display = 'block';
        playerNameInput.focus();
        playerLabel.textContent = 'Player 1 Name:';
        numPlayersDropdown.style.pointerEvents = 'none';
        numPlayersButton.style.display = 'none';
        timerSection.style.display = 'none';
        submitButton.style.display = 'none';
    });

    // Add player names with Enter key, only during player name entry stage
    playerNameInput.addEventListener('keydown', function handleEnterKey(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            addPlayerButton.click();
        }
    });
    // Add player names
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
            playerNameInput.focus();
        } else {
            playerLabel.style.display = 'none';
            playerNameInput.style.visibility = 'none';
            addPlayerButton.style.display = 'none';
            playerNameInput.removeAttribute("required");
            timerSection.style.display = 'inline';
            submitButton.style.display = 'inline';
            timerDropdown.focus();
            console.log(playerNames);
            submitButton.addEventListener('click', () => {
                if (timerDropdown.value === "") {
                    alert("Choose a time difficulty.");
                    return;
                }

            document.getElementsById('player_names').value = JSON.stringify(playerNames);
            })
        }
    });

});
