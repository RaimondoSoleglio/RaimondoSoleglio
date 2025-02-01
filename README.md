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

## Potential improvements and additional funcionalities

The initial idea for the game was much more extensive - and thinking so big from the start was of course a typical rookie mistake. But now that a foundation is laid, those functionalities I had in mind in the first place could be nice additions.

It could be nice for example to introduce the following:

1. Instead of just guessing actors from movies, the game could be structured as a chain. For example: App picks actor 1 -> Player 1 picks movie 1 with actor 1 -> Player 2 picks actor 2 from movie 1 -> Plaeyr 3 picks movie 2 with actor 2 and so on... The players could decide which style of game they want to play.

2. There could be an option at start that allows you to insert more categories to guess. For example in the chain explained in 1. we could add directors and the app could randomly ask the players for either one category or another to guess.

3. At the very begininning I had imagined the game completely customisable. For example, for added difficulty or vice-versa to make it easier in some cases, players could pick just a range of years in which the movies have been produced, or just a geographical area, or spoken in a certain language.

4. It would be nice to add more design elements to the front-end. Maybe pictures associated with actors? Or at least the option to do so? Hearts emojis to show the number of lives? There was for example a red flash appearing for the wrong answer at some point, but I got it lost in the hundreds of changes I have made to the code.

5. Sounds would possibly also add to enjoyment of the game.


## Thoughts about the game, difficulties, solutions

I will keep this section short, but I took some notes in a diary as I was encountering difficulties and changing the direction of my work to adapt. This has been very useful to understand how it's better to build up from the small to the big, instead of imagining already the final product in mind the whole time. I hope this can help me or others to be aware of this sort of traps.

Some of the notes.

> I managed to reduce the whole database to 1.67gB
Still quite big, I hope it can still work.
But definitely more manageable than the 7 gb one I had at start.
>I created a joint table where the regions are limited to US, GB, FR, IT, ES
Where the movies are NOT shorts
And the year of release is at least 1931.

Here I was basicaly attempting to build my own specific database, instead of using an API!!! This was not only an incredibly silly approach, but it also brought me into unexpected places that wasted a lot of my time. For example I started to test and study Oracle cloud and many other things related to databases and database hosting.

While all this was very interesting and nice to explore, it slowed down my project, which was the ultimate thing I should have focused on, and it overwhelmed me to the point I had to rethink the whole approach. My frustration was quite clear in another later note. 😅

> I have signed up for a free account on Oracle Cloud to host my database.
Now the big problem is: I can't use CS50 library to connect to it and probably I need to learn a whole new world of stuff to make this work OUCH!

Days later, I finally decide to test the API approach and, at the same time, I am looking for a place that it can then host my app. That's when I decide to go for Render. Render, like many other similar services, in its free tier, does not offer constant servicing and the app sins down after inactivity - which means sometimes it takes a couple of minutes to restart when someone goes there. I am still very happy with my first test of my own app online, and the link to take a look at it directly on the web is [here](https://raimondosoleglio.onrender.com)

>After deciding to simplify the project to its basics, I have also attempted to find the right place where I could host the Flask app (and for the moment I have found that Render could be a good place)
>
>Plus: I was wondering if I could use an API instead of building my own database and use that to dynamically show the title "as the user is typing them", mimicking what David did in one of the CS50 lessons. And it seems that through TMDB API this is quite easy to implement.

Once I changed my approach, I have started to finally move on and build properly my app, thinking of details like "How the app should pick an actor?", "How the selection in the query should work? Could a user use both the mouse or just the keyboard? Would be useful to autoselect the search bar for keyboard-only users?". Also, by analysing David's code for the Finance pset, I started to explore better the choices related to security.

> Things I managed to do:
>
>   - Adding randomness to pick from the first 5 actors in a cast
>   - Moving to the number 6 on in a cast if all the main 5 actors have been picked
>   - Adding original title to the movie when it's not the same as english (Nikita)
>   - Movie does not appear in the query if it's already been previously chosen
>   - You can select movies with arrows
>
> Learnt more about session[]
>
>REMEMBER THIS:
>
> Security Considerations:
>
>    - Before: With signed cookies, the session data is stored on the client side and only the cookie is sent to the server. The session data is encrypted and signed with your SECRET_KEY, so it cannot be tampered with by the user.
>    - After: When using the filesystem, the session data is stored on the server, which is more secure because it is not visible to the client. However, you must ensure the server's filesystem is secure to prevent unauthorized access to session data. Flask will automatically generate session files in a directory (usually /tmp by default) on the server. Make sure that directory has the correct permissions and isn't publicly accessible.

Finally, one of the major hurdles was to build a fair and functional multiplayer flow. As long as the choice would limit to 2 players, it would have been quite easy. But introducing the idea of up to 4 player and fairer game dynamics where a whole round needs to finish for the surviving player to win, I have given myself a lot of work to do. This is where GPT, which has been of fundamental help along the whole process, wasn't anymore able to give the right help.

Too many files and too many variables to consider. But this is where the final and most important teaching comes up. Forced to look for solutions myself, now that I had the whole structure in front of my eyes, I finally started to learn better how the whole machine I had put up works, and found simpler and more effective solutions that brought me to a satisfying end of the project.
