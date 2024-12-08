from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, abort
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

# To pick a random actor at start
def get_random_actor():
    # Retrieve session_id
    session_id = session.get("session_id")

    first_actor = db.execute("SELECT name, id FROM starting_actors WHERE id NOT IN (SELECT actor_id FROM actors WHERE session_id = ?)", session_id)

    # Randomly pick an actor from the filtered list
    if not first_actor:
        first_actor = db.execute("SELECT name, id FROM starting_actors")
    selected_actor = random.choice(first_actor)

    # Add actor to the temporary database
    db.execute("INSERT INTO actors (name, actor_id, session_id) VALUES (?, ?, ?)", selected_actor["name"], selected_actor["id"], session_id)

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

@app.route("/start", methods=["GET", "POST"])
def start():
    session_id = session.get("session_id")
    if session_id:
        db.execute("DELETE FROM actors WHERE session_id = ?", session_id)
        db.execute("DELETE FROM movies WHERE session_id = ?", session_id)
        db.execute("DELETE FROM players WHERE session_id = ?", session_id)
        db.execute("DELETE FROM sessions WHERE session_id = ?", session_id)

        session.clear()

    if request.method == "POST":
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

        # Get number of players
        num_players = int(request.form.get("num_players", 0))
        if num_players < 1 or num_players > 4:
            flash("Number of players must be between 1 and 4.")
            return redirect("/start")

        # Get player names
        try:
            player_names = json.loads(request.form.get("player_names"))
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
                return redirect("/start")

        # Get timer value
        timer = request.form.get("timer")
        if not timer or int(timer) not in [15, 30, 45, 60]:
            flash("Please select a valid timer value.")
            return redirect("/start")
        timer = int(timer)

        lives = [3] * num_players  # Initial lives for players

        # Save game settings in session
        session["num_players"] = num_players
        session["player_names"] = player_names
        session["timer"] = timer
        session["lives"] = lives  # Initialize lives for each player

        print(session) # Debug

        # Metadata in database
        db.execute("INSERT INTO sessions (session_id, num_players, timer) VALUES (?, ?, ?)",
                   session_id, num_players, timer)

        # Insert players into database
        for name in player_names:
            db.execute("INSERT INTO players (session_id, name, lives) VALUES (?, ?, ?)", session_id, name, 3)

        # Reset session database
        session.pop("current_actor", None)
        # Clear old data tied to this session_id if any
        db.execute("DELETE FROM actors WHERE session_id = ?", session_id)
        db.execute("DELETE FROM movies WHERE session_id = ?", session_id)

        return redirect("/main")

    return render_template("start.html")

# main
@app.route("/main")
def main():
    session_id = session.get("session_id")
    if not session_id:
        return redirect("/start")  # Redirect if no session

    # Fetch player data
    players = db.execute("SELECT id, name, lives FROM players WHERE session_id = ?", session_id)
    if not players:
        flash("No players found!")
        return redirect("/start")  # Redirect if no players found

    print(players) # Debug

    # BIG CHANGES FROM HERE ---

    # Filter active players
    active_players = [player for player in players if player["lives"] > 0]
    if not active_players:
        flash("Game Over! No players left.")
        return redirect("/end")

    print(active_players)

    # Cycle through players
    current_player_index = session.get("current_player_index", 0) % len(active_players)
    current_player = active_players[current_player_index]

    session["current_player_index"] = (current_player_index + 1) % len(active_players)
    flash(f"{current_player['name']} ready?")
    session["current_player_id"] = current_player["id"]

    # --- TO HERE

    # Get a random actor if none has been set
    current_actor = session.get("current_actor") or get_random_actor()
    session["current_actor"] = current_actor

    print(current_actor)
    print(session)

    # --- also: if the player has no lives left:
    for player in players:
        if len(players) > 1 and player["lives"] <= 0:
            flash(f"Sorry {player['name']}, your adventure ends here!")

    if len(players) == 1 and len(active_players) == 1 and active_players[0]["lives"] <= 0:
        correct_guesses = db.execute("SELECT COUNT(*) FROM movies WHERE session_id = ?", session_id)[0]["COUNT(*)"]
        flash(f"With {session.get('timer')} seconds, you guessed {correct_guesses} movies correctly!")
        return redirect("/end")

    # --- Multiplayer:
    if len(players) > 1 and len(active_players) == 1:
        flash(f"Game Over! {active_players[0]['name']} is the winner!")
        return redirect("/end")

    return render_template("main.html", actor=current_actor, players=players, timer=session.get("timer"))

# query route
@app.route("/query", methods=["GET"])
def query():
    session_id = session.get("session_id")
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
    for movie in data.get("results", [])[:10]:
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
    guessed_movie_ids = {row["movie_id"] for row in db.execute("SELECT movie_id FROM movies WHERE session_id = ?", session_id)}
    # Update results to filter out movies already guessed
    unique_movies = [movie for movie in movies if movie["id"] not in guessed_movie_ids]
    return jsonify(unique_movies)


@app.route("/guess", methods=["POST"])
def guess():
    session_id = session.get("session_id")
    if not session_id:
        return redirect("/start")  # Redirect if no session is active

    selected_movie = request.form.get("movie_query")
    movie_id = request.form.get("movie_id")  # Movie ID (e.g., 123)
    current_actor = session.get("current_actor")

     # Validate the input
    if not movie_id:
        return redirect("/wrong")  # Ensure `movie_id` is provided

    # Validate the guess by checking if the actor is in the movie’s cast
    cast_response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/credits",
        params={"api_key": TMDB_API_KEY}
    )
    cast_data = cast_response.json().get("cast", [])

    # Check if current_actor is in the movie cast
    if any(actor["name"] == current_actor for actor in cast_data):
        # Add movie to the session database
        db.execute("INSERT INTO movies (title, movie_id, session_id) VALUES (?, ?, ?)", selected_movie, movie_id, session_id)

        # Find the list of already picked actors in the temp actors table
        used_actors = {actor["name"] for actor in db.execute("SELECT name FROM actors WHERE session_id = ?", session_id)}
        flash("Correct! Next player's turn.")

        # Shuffle the list of top 5 main cast members so to randomise the choice
        top_cast = cast_data[:5]
        random.shuffle(top_cast)

        # Try to pick a new actor from the top 5 main cast members
        new_actor = None
        for actor in top_cast:  # Try from main cast (first 5 actors)
            if actor["name"] not in used_actors:
                new_actor = actor["name"]
                break

        # If all 5 main actors are used, pick from the rest of the cast
        if not new_actor:
            for actor in cast_data[5:]:  # From the 6th actor onward
                if actor["name"] not in used_actors:
                    new_actor = actor["name"]
                    break

        # If no new actor is found (very unlikely), return an error or message
        if not new_actor:
            new_actor = get_random_actor()

        # Add the new actor to the temporary actors table in the database
        db.execute("INSERT INTO actors (name, actor_id, session_id) VALUES (?, ?, ?)", new_actor, actor["id"], session_id)

        # Update the session with the new actor
        session["current_actor"] = new_actor
        return redirect("/main")

    else:
        db.execute("UPDATE players SET lives = lives - 1 WHERE id = ?", session["current_player_id"])
        flash("Nope, sorry! You lost a life.")
        return redirect("/main")

@app.route("/end")
def end_session():
    session_id = session.get("session_id")
    if session_id:
        db.execute("DELETE FROM actors WHERE session_id = ?", session_id)
        db.execute("DELETE FROM movies WHERE session_id = ?", session_id)
        db.execute("DELETE FROM players WHERE session_id = ?", session_id)
        db.execute("DELETE FROM sessions WHERE session_id = ?", session_id)

        session.clear()
    return redirect("/")

@app.route("/end_turn", methods=["POST"])
def end_turn():
    session_id = session.get("session_id")
    player_id = session.get("current_player_id")
    db.execute("UPDATE players SET lives = lives - 1 WHERE id = ?", player_id)
    flash("Time over! You lost a life.")
    return "", 200


