from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, abort, url_for
from flask_session import Session
import requests, random, json, uuid

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# My TMDb API key
TMDB_API_KEY = "b0ae1057e51208e1713059117208de90"

# Temporary in-memory database
db = SQL("sqlite:///game_database.db")

# Helper functions
def reset_active_players(session_id):
    players = db.execute("SELECT id, name, lives, active FROM players WHERE session_id = ?", session_id)
    db.commit()  # Ensure the update is committed
    new_active_players = [player for player in players if player["active"] != 0]
    session['round_active'] = len(new_active_players)
    return new_active_players

def get_active_players(session_id):
    players = db.execute("SELECT id, name, lives, active FROM players WHERE session_id = ?", session_id)
    db.commit()  # Ensure the update is committed
    return [player for player in players]

'''
def update_active_players_during_session(session_id):
    active_players = get_active_players_during_session(session_id)
    session['active_players'] = active_players

def update_active_players(session_id):
    active_players = get_active_players(session_id)
    session['active_players'] = active_players
    session['round_active'] = len(active_players)
'''

def get_random_actor():
    # Retrieve session_id
    session_id = session.get('session_id')

    first_actor = db.execute("SELECT name, id FROM starting_actors WHERE id NOT IN (SELECT actor_id FROM actors WHERE session_id = ?)", session_id)

    # Randomly pick an actor from the filtered list
    if not first_actor:
        first_actor = db.execute("SELECT name, id FROM starting_actors")
    selected_actor = random.choice(first_actor)

    # Add actor to the temporary database
    db.execute("INSERT INTO actors (name, actor_id, session_id) VALUES (?, ?, ?)", selected_actor["name"], selected_actor["id"], session_id)
    db.commit()  # Ensure the update is committed

    return selected_actor["name"]

# Copied form CS50 pset - does this work?
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# index
@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")

# start
@app.route("/start", methods=["GET", "POST"])
def start():
    session_id = session.get("session_id")
    if session_id:
        db.execute("DELETE FROM actors WHERE session_id = ?", session_id)
        db.execute("DELETE FROM movies WHERE session_id = ?", session_id)
        db.execute("DELETE FROM players WHERE session_id = ?", session_id)
        db.execute("DELETE FROM sessions WHERE session_id = ?", session_id)
        db.commit()  # Ensure the update is committed

        session.clear()

    if request.method == "POST":
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

        # Get number of players
        num_players = int(request.form.get('num_players', 0))
        if num_players < 1 or num_players > 4:
            flash("Number of players must be between 1 and 4.")
            return redirect("/start")

        # Get player names
        try:
            player_names = json.loads(request.form.get('player_names'))
        except (TypeError, json.JSONDecodeError):
            flash("Invalid player names format.")
            return redirect("/start")

        if len(player_names) != num_players:
            flash("Please enter names for all players.")
            return redirect("/start")

        # Validate each player's name
        for name in player_names:
            if not name.isalnum() or len(name) > 10:
                flash("Player names must be alphanumeric and up to 10 characters long.")
            if player_names.count(name) > 1:
                flash("Player names must be unique.")
                return redirect("/start")

        # Get timer value
        timer = request.form.get('timer')
        if not timer or int(timer) not in [15, 30, 45, 60]:
            flash("Please select a valid timer value.")
            return redirect("/start")
        timer = int(timer)

        lives = [3] * num_players  # Initial lives for players

        # Save game settings in session
        session['num_players'] = num_players
        session['player_names'] = player_names
        session['timer'] = timer
        session['round_active'] = 0  # Initialise at the start of a new game
        session['current_player_index'] = 0
        session['wrong_answer'] = False  # To calculate single player score


        # Metadata in database
        db.execute("INSERT INTO sessions (session_id, num_players, timer) VALUES (?, ?, ?)", session_id, num_players, timer)
        db.commit()  # Ensure the update is committed

        # Insert players into database
        for name in player_names:
            db.execute("INSERT INTO players (session_id, name, lives, active) VALUES (?, ?, ?, ?)", session_id, name, 3, 1)
            db.commit()  # Ensure the update is committed

        # Initialise session['active_players']
        session['active_players'] = get_active_players(session_id)
        session['round_active'] = num_players
        print("BEFORE ANYTHING: ", session['active_players'])

        # Reset session database
        session.pop('current_actor', None)
        return redirect("/main")

    return render_template("start.html")

# main
@app.route("/main")
def main():
    session_id = session.get('session_id')
    if not session_id:
        return redirect("/start")  # Redirect if no session

    # Reset life deduction marker for the next round
    session['life_deducted'] = False

    # Players for front-end visualisation
    players = db.execute("SELECT id, name, lives FROM players WHERE session_id = ?", session_id)
    db.commit()  # Ensure the update is committed
    if not players:
        flash("No players found!")
        return redirect("/start")  # Redirect if no players found

    active_players = session.get('active_players')

    # Update current player index and fetch current player
    if session['num_players'] == 1:
        if active_players == []:
            return redirect("/endSolo")
        current_player = active_players[0]
    else:
        current_player = active_players[session['current_player_index']] # retrieve the right player
    session['current_player_id'] = current_player['id']                  # store their id in session - now we know that specific "c_p_id" is playing

    print("AT THE START OF MAIN: ", active_players, "Currnet Player Index: ", session['current_player_index'], "Current player ID: ", session['current_player_id'])

    # Get a random actor if none has been set
    current_actor = session.get('current_actor') or get_random_actor()
    session['current_actor'] = current_actor

    message = f"{current_player['name']}, ready?"

    return render_template("main.html", actor=current_actor, players=players, message=message, current_player=current_player, timer=session.get("timer"))

# query route
@app.route("/query", methods=["GET"])
def query():
    session_id = session.get('session_id')
    if not session_id:
        return redirect("/start")  # Redirect if no session is active

    query = request.args.get('q')
    if not query:
        return jsonify([])

    # Call TMDb Search Movies API
    response = requests.get(
        f"https://api.themoviedb.org/3/search/movie",
        params={
            "api_key": TMDB_API_KEY,
            "query": query,
            "include_adult": "false"
        }
    )

    # Parse the JSON response from TMDb
    data = response.json()

    # Get up to 10 movie titles from the results
    movies = []
    for movie in data.get('results', [])[:10]:
        title = movie['title']
        original_title = movie['original_title']
        year = movie['release_date'][:4]  # Extract year from release_date

        # Check if the original_title differs from the title
        if original_title != title:
            updated_title = f"{title} ({year}) [{original_title}]"
        else:
            updated_title = f"{title} ({year})"

        # Add the movie info including title and movie ID
        movies.append({
            "title": updated_title,
            "id": movie["id"]
        })

    # Extract movie IDs already guessed
    guessed_movie_ids = {row['movie_id'] for row in db.execute("SELECT movie_id FROM movies WHERE session_id = ?", session_id)}
    # Update results to filter out movies already guessed
    unique_movies = [movie for movie in movies if movie['id'] not in guessed_movie_ids]
    return jsonify(unique_movies)


@app.route("/guess", methods=["POST"])
def guess():
    session_id = session.get('session_id')

    if not session_id:
        return redirect("/start")  # Redirect if no session is active

    selected_movie = request.form.get('movie_query')
    movie_id = request.form.get('movie_id')  # Movie ID (e.g., 123)

     # Validate inputs
    if not selected_movie or not movie_id:
        flash("Invalid input. Please select a movie.")
        return redirect("/main")

    if not movie_id.isdigit():
        flash("Invalid movie selection.")
        return redirect("/main")

    movie_id = int(movie_id)  # Safely cast to integer after validation

    current_actor = session.get('current_actor')

    # Validate the guess by checking if the actor is in the movie’s cast
    cast_response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/credits",
        params={"api_key": TMDB_API_KEY}
    )
    cast_data = cast_response.json().get("cast", [])

    # Check if current_actor is in the movie cast
    if any(actor['name'] == current_actor for actor in cast_data):
        # Add movie to the session database
        db.execute("INSERT INTO movies (title, movie_id, session_id) VALUES (?, ?, ?)", selected_movie, movie_id, session_id)
        db.commit()  # Ensure the update is committed
        session['actor_attempts'] = 0  # Reset the round counter

        # Find the list of already picked actors in the temp actors table
        used_actors = {actor['name'] for actor in db.execute("SELECT name FROM actors WHERE session_id = ?", session_id)}

        # Shuffle the list of top 5 main cast members so to randomise the choice
        top_cast = cast_data[:5]
        random.shuffle(top_cast)

        # Try to pick a new actor from the top 5 main cast members
        new_actor = None
        for actor in top_cast:  # Try from main cast (first 5 actors)
            if actor['name'] not in used_actors:
                new_actor = actor['name']
                break

        # If all 5 main actors are used, pick from the rest of the cast
        if not new_actor:
            for actor in cast_data[5:]:  # From the 6th actor onward
                if actor['name'] not in used_actors:
                    new_actor = actor['name']
                    break

        # If no new actor is found (very unlikely), return an error or message
        if not new_actor:
            new_actor = get_random_actor()

        # Add the new actor to the temporary actors table in the database
        db.execute("INSERT INTO actors (name, actor_id, session_id) VALUES (?, ?, ?)", new_actor, actor['id'], session_id)
        db.commit()  # Ensure the update is committed

        # Update the session with the new actor
        session['current_actor'] = new_actor

        return redirect("/endOfTurn")

    else:
        return redirect("/loseLife")

@app.route("/loseLife")
def loseLife():
    session_id = session.get('session_id')
    session['actor_attempts'] = session.get('actor_attempts', 0) + 1  # Increment wrong guesses
    session['wrong_answer'] = True

    # Avoid multiple life deductions in quick succession
    if session.get('life_deducted', False):
        return redirect("/main")

    db.execute("UPDATE players SET lives = lives - 1 WHERE session_id = ? AND id = ?", session_id, session['current_player_id'])
    db.commit()  # Ensure the update is committed

    session['life_deducted'] = True  # Mark that a life has been deducted
    print("IN LOSELIFE: session['active_players']", session['active_players'], "Current Player Index: ", session['current_player_index'], "Current player ID: ", session['current_player_id'])

    return redirect("/endOfTurn")

@app.route("/endOfTurn")
def endOfTurn():
    session_id = session.get('session_id')

    '''
    current_player = db.execute("SELECT id, name, lives, active FROM players WHERE session_id = ? AND id = ?", session_id, session['current_player_id"])
    print(current_player)
    current_player_index = session.get("current_player_index", 0)
    print(current_player_index)
    active_players = get_active_players_during_session(session_id)
    print(active_players)
    '''

    active_players = session.get('active_players')
    current_player = active_players[session['current_player_index']]
    print("AT THE START OF ENOFTURN: ", active_players, "Currnet Player Index: ", session['current_player_index'], "Current player ID: ", session['current_player_id'])


    # Check if all players guessed wrong for the current actor
    if session['actor_attempts'] >= len(active_players):
        # Pick a new actor
        session['current_actor'] = get_random_actor()
        session['actor_attempts'] = 0  # Reset attempts for the new actor

    # Deduct correct guesses in single-player mode
    if session['num_players'] == 1:
        if session['wrong_answer'] == False:
            session['correct_guesses'] = max(0, session.get('correct_guesses', 0) + 1)
            print("CORRECT? ", session['correct_guesses'])
        session['wrong_answer'] = False # Reset for single player score

        if active_players[0]['lives'] <= 0:  # Player has no lives left (maybe I need to change this to zero lives for player)
            return redirect("/endSolo")

    session['round_active'] -= 1    # a whole new thing from here:

    # Handle multiplayer game ending
    if session['num_players'] > 1:
        if session['round_active'] == 0:
            # Check game-ending conditions after a full round
            if len(active_players) == 1:
                winner = active_players[0]['name']
                return redirect(f"/gameover?winner={winner}")  # Implement gameover route for multiplayer

            elif len(active_players) == 0:
                return redirect("/gameover")  # No winner case

            elif len(active_players) > 1:
                active_players = reset_active_players(session_id)     # reset active_players
                session['current_player_index'] = 0
                session['round_active'] = len(active_players)
                print("reset session number is ", session['round_active'])
                print("END OF TURN AT THE START OF NEW CYCLE: ", active_players, "Currnet Player Index: ", session['current_player_index'], "Current player ID: ", session['current_player_id'])


        else:
            current_player_index = session.get('current_player_index')
            session['current_player_index'] = (current_player_index + 1) % len(active_players)   # advance player by 1
            print("END OF TURN DURING CYCLE: ", active_players, "Currnet Player Index: ", session['current_player_index'], "Current player ID: ", session['current_player_id'])


    return redirect("/main")

@app.route("/endSolo")
def endSolo():
    session_id = session.get('session_id')

    if session['num_players'] != 1:
        return redirect("/start")

    # Calculate score and configuration
    correct_guesses = session.get('correct_guesses', 0)
    initial_timer = session.get('timer', 0)

    # Render end screen with score and configuration details
    return render_template(
        "endSolo.html",
        correct_guesses=correct_guesses,
        initial_timer=initial_timer
    )

@app.route("/gameover")
def gameover():
    session_id = session.get('session_id')
    winner = request.args.get('winner')  # Pass winner name as a query parameter if needed

    if winner:
        return render_template("gameover.html", message=f"{winner} is the winner!")
    return render_template("gameover.html", message="All players are out of lives! No winner.")


