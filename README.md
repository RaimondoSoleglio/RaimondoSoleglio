# GUESS THE MOVIE
#### Video Demo:  <URL HERE>
#### Description: A guessing game about actors and movies, playable both as a single- or multiplayer.

## General initial approach

Given that I have decided to build the app by myself, I have seeked the help of an AI to build, improve and fix the app in the process. The only AI used was ChatGPT, of which I took advantage to explore the new Canvas functionality that had just been implemented when I started my project.
Occasionally I have asked also the duck debugger directly inside VS Code.

The initial plan was much bigger and complex than what it turned out to be - I will talk about this in the section about [Potential improvements](#potential-improvements-and-additional-funcionalities)

The starting point is the whole Finance project from CS50 course. I didn't need any of the code relative to logging in, but I used most of the structure of the Flask app and Templates and I have built upon it.

## The game dynamics

The app starts with an index page where the rules of the game are explained and some thanks given.

On the start page you pick how many players will play (from 1 to 4), their names, and a timer which determines the difficulty of the game.

The game starts with a randomly picked actor (from a pre-populated list of famous actors) and the player needs to guess a movie where they acted. If they guess right, the app will pick from the same movie another actor, among the 5 most popular in that movie, according to TMDb (whose API is used to retrieve data), and the game moves on. The actor and movie guessed are stored in the database so they don't reappear again later in the game. If a player cannot guess the movie, the same actor is proposed to the next player. If for a whole round (i.e.: all the active players) the movie is not guessed, then the app will pick aother random famous actor from the pre-populated list.

In a multiplayer mode, within a whole round each player has only one guess: once a player has tried to guess (either right or wrong) then they pass the keyboard to the next player. Each player has 3 lives, if they lose them they are out of the game. The first player is slightly in advantage, because the game always starts (or restarts after a whole round of wrong guesses) with a famous actor.

The multiplayer mode can end both with a winner or with no winners. In fact, in order for a player to win, a whole round has to be completed. For example, if at a final round out of 3 players the first 2 have lost all their lives and Player 3 has still one left, Player 3 still will have to answer correctly in order to win: if all players have 0 lives at the end of the round, there are no winners.

In single-player mode, there is a counter. At the end of the game, the app will tell you how many guesses were correct and the timer difficulty you have picked for this session.

## Purpose of each file

[app.py](app.py) is the main file with the Flask app.
After importing the necessary 

In [populate db](populate%20db.py) is a pre-populated list of famous actors and their IDs on TMDb. The usefulness of having a separate file for this is that the list can be modified or enhanced easily at any time.

game_database.db is a sqlite3 database tracking all the data.
It contains the following tables:
* starting_actors: fed with the pre-populated list of famous actors
* sessions: to keep track of multiple sessions of players at the same time; it stores data about the number of players and the timer difficulty;
* players: for each specific session, stores IDs, names and lives for the players
* actors: keeps track of the guessed actors to avoid they get picked twice by the the app
* movies: same as above, but for the movies

JS files:
[scriptMain.js](/static/scriptMain.js) handles the dynamic query and selection of the movies;

## Thoughts about the game, difficulties, solutions

## Potential improvements and additional funcionalities
Here
