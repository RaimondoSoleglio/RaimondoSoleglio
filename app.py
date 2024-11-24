from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
import requests, random, json, sqlite3

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

# Copied form CS50 pset - does this work?
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        print("Form submitted")  # Debug statement
        # Get number of players
        num_players = int(request.form.get("num_players", 0))
        if num_players < 1 or num_players > 4:
            flash("Number of players must be between 1 and 4.")
            return redirect("/start")

        # Get player names
        print(request.form.get("player_names"))
        player_names = json.loads(request.form.get("player_names"))
        print(player_names)
        if len(player_names) != num_players:
            flash("Please enter names for all players.")
            return redirect("/start")

        # Validate each player's name
        for name in player_names:
            if not name.isalnum() or len(name) > 10:
                flash("Player names must be alphanumeric and up to 10 characters long.")
                return redirect("/start")

        # Get timer value
        timer = int(request.form.get("timer", 0))
        if timer not in [15, 30, 45, 60]:
            flash("Invalid timer value selected.")
            return redirect("/start")

        # Save game settings in session
        session["num_players"] = num_players
        session["player_names"] = player_names
        session["timer"] = timer
        session["lives"] = [3] * num_players  # Initialize lives for each player


        # Reset session database
        session.pop("current_actor", None)
        db.execute("DELETE FROM actors")
        db.execute("DELETE FROM movies")

        print("Redirecting to /main")  # Debug statement

        return redirect("/main")


    return render_template("start.html")


# To pick a random actor at start
def get_random_actor():

    first_actor = db.execute("SELECT name, id FROM starting_actors")

    # Randomly pick an actor from the filtered list
    selected_actor = random.choice(first_actor)

    print (selected_actor)

    # Add actor to the temporary database
    db.execute("INSERT INTO actors (name, actor_id) VALUES (?, ?)", selected_actor["name"], selected_actor["id"])

    return selected_actor["name"]

# index
@app.route("/")
def index():
    return render_template("index.html")

# main
@app.route("/main")
def main():
    # Get a random actor if none has been set
    current_actor = session.get("current_actor") or get_random_actor()
    session["current_actor"] = current_actor
    return render_template("main.html", actor=current_actor)

# query route
@app.route("/query", methods=["GET"])
def query():
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
    guessed_movie_ids = {row["movie_id"] for row in db.execute("SELECT movie_id FROM movies")}
    # Update results to filter out movies already guessed
    unique_movies = [movie for movie in movies if movie["id"] not in guessed_movie_ids]
    return jsonify(unique_movies)


@app.route("/guess", methods=["POST"])
def guess():
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
        db.execute("INSERT INTO movies (title, movie_id) VALUES (?, ?)", selected_movie, movie_id)

        # Find the list of already picked actors in the temp actors table
        used_actors = {actor["name"] for actor in db.execute("SELECT name FROM actors")}

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
            return redirect("/wrong")

        # Add the new actor to the temporary actors table in the database
        db.execute("INSERT INTO actors (name, actor_id) VALUES (?, ?)", new_actor, actor["id"])

        # Update the session with the new actor
        session["current_actor"] = new_actor
        return redirect("/")
    '''
    if any(actor["name"] == current_actor for actor in cast_data):
        # Add movie to the session database
        db.execute("INSERT INTO movies (title) VALUES (?)", selected_movie)

        # Pick another main actor from the movie’s cast
        new_actor = random.choice([actor["name"] for actor in cast_data[:5] if actor["name"] != current_actor])
        session["current_actor"] = new_actor
        return redirect("/")
    '''
    return redirect("/wrong")

@app.route("/wrong")
def wrong():
    return "Wrong answer, try again!", 400
