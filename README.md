# GUESS THE MOVIE
#### Video Demo:  <URL HERE>
#### Description: A guessing game about actors and movies, playable both as a single- or multiplayer.
<br/>

## General initial approach

Given that I have decided to build the app by myself, I have seeked the help of an AI to build, improve and fix the app in the process. The only AI used was ChatGPT, of which I took advantage to explore the new Canvas functionality that had just been implemented when I started my project.
Occasionally I have asked also the duck debugger directly inside VS Code.

The initial plan was much bigger and complex than what it turned out to be - I will talk about this in the section about [Potential improvements](#potential-improvements-and-additional-funcionalities)

The starting point is the whole Finance project from CS50 course. I didn't need any of the code relative to logging in, but I used most of the structure of the Flask app and Templates and I have built upon it.
<br/>
<br/>

## The game dynamics

The app starts with an index page where the rules of the game are explained and some thanks given.

On the start page you pick how many players will play (from 1 to 4), their names, and a timer which determines the difficulty of the game.

The game starts with a randomly picked actor (from a pre-populated list of famous actors) and the player needs to guess a movie where they acted. If they guess right, the app will pick from the same movie another actor, among the 5 most popular in that movie, according to TMDb (whose API is used to retrieve data), and the game moves on. The actor and movie guessed are stored in the database so they don't reappear again later in the game. If a player cannot guess the movie, the same actor is proposed to the next player. If for a whole round (i.e.: all the active players) the movie is not guessed, then the app will pick aother random famous actor from the pre-populated list.

In a multiplayer mode, within a whole round each player has only one guess: once a player has tried to guess (either right or wrong) then they pass the keyboard to the next player. Each player has 3 lives, if they lose them they are out of the game. The first player is slightly in advantage, because the game always starts (or restarts after a whole round of wrong guesses) with a famous actor.

The multiplayer mode can end both with a winner or with no winners. In fact, in order for a player to win, a whole round has to be completed. For example, if at a final round out of 3 players the first 2 have lost all their lives and Player 3 has still one left, Player 3 still will have to answer correctly in order to win: if all players have 0 lives at the end of the round, there are no winners.

In single-player mode, there is a counter. At the end of the game, the app will tell you how many guesses were correct and the timer difficulty you have picked for this session.

## Purpose of each file

[app.py](app.py) is the main file with the Flask app.

After importing the necessary classes and modules and configuring application and session, an API key and game_database.db are stored in variables.

A series of helpers functions follows. Two of them are meant to control that a round stays consistent at every steps by tracking properly the active players. One is meant to take care of picking a random actor.

The routes:
* __home__ It renders the [index.html](/templates/index.html) template
* __start__ When called by GET, it renders the [start.html](/templates/start.html) template. By POST, collects all the data to start the game and redirects to [main.html](/templates/main.html)
* __main__ It's where the main game unfolds.
* __query__ Handles the query for a movie in the search bar on the main.
* __guess__ Invoked by POST once a player picks an answer, redirects to endOfTurn if the answer is correct, to loseLife if the answer is wrong
* __loseLife__ It deducts a life and redirects to _endOfTurn_
* __endOfTurn__ It determines how the game proceeds at the end of a turn. It redirects to main if the game continues, and to _endSolo_ (for single-player mode) or gameover if the game ends
* __endSolo__ It handles the scenario of single-player ending and renders [endSolo.html](/templates/endsolo.html)
* __gameover__ It handles the scenarios of multiplayer endings (no winner or winner) and renders [gameover.html](/templates/gameover.html)

In [populate db](populate%20db.py) is a pre-populated list of famous actors and their IDs on TMDb. The usefulness of having a separate file for this is that the list can be modified or enhanced easily at any time.

game_database.db is a sqlite3 database tracking all the data.
It contains the following tables:
* starting_actors: fed with the pre-populated list of famous actors
* sessions: to keep track of multiple sessions of players at the same time; it stores data about the number of players and the timer difficulty;
* players: for each specific session, stores IDs, names and lives for the players
* actors: keeps track of the guessed actors to avoid they get picked twice by the the app
* movies: same as above, but for the movies

JS files:
[scriptMain.js](/static/scriptMain.js) handles the dynamic query and selection of the movies
[scriptTimer.js](/static/scriptTitmer.js) handles the time a player has to give an answer; it starts only after the end of a countdown warning the player that is their turn
[scriptStart.js](/static/scriptStart.js) takes care that all the data on the start page are inputted properly

[stiles.css](/static/styles.css) contains all the CSS

Templates:
In addition to the templates described above, there is a [layout.html](/templates/layout.html) that lays the structure for all the Jinja templates.
<br/>
<br/>
<br/>

## Thoughts about the game, difficulties, solutions

## Potential improvements and additional funcionalities
Here
