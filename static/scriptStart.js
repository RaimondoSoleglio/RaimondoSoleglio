document.addEventListener("DOMContentLoaded", () => {

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
            addPlayerButton.style.display = 'none';
            timerSection.style.display = 'inline';
        }
    });

    // Enter button appears after Timer selection

    timerDropdown.addEventListener('change', () => {
        submitButton.style.display = 'inline';
    })
});
