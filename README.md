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

The game dynamics are very simple. On the start page you pick how many players will play (from 1 to 4), their names, and a timer which determines the difficulty of the game.

The game starts with a randomly picked actor (from a pre-populated list of famous actors) and the player needs to guess a movie where they acted. If they guess right, the app will pick from the same movie another actor, among the 5 most popular in that movie, according to TMDb (whose API is used to retrieve data), and the game moves on. The actor and movie guessed are stored in the database so they don't reappear again later in the game.

In a multiplayer mode, within a whole round each player has only one guess: once a player has tried to guess (either right or wrong) then they pass the keyboard to the next player. Each player has 3 lives, if they lose them they are out of the game. The first player is slightly in advantage insofaras


## Purpose of each file

## Thoughts about the game, difficulties, solutions

## Potential improvements and additional funcionalities
Here
