from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
import requests, random

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# My TMDb API key
TMDB_API_KEY = "b0ae1057e51208e1713059117208de90"

# Temporary in-memory database
db = SQL("sqlite:///temp_game.db")

@app.before_first_request
def setup_db():
    # Create tables for tracking actors and movies
    db.execute("CREATE TABLE IF NOT EXISTS actors (id INTEGER PRIMARY KEY, name TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS movies (id INTEGER PRIMARY KEY, title TEXT)")

# To pick a random actor at start
def get_random_actor():
    response = requests.get(
        "https://api.themoviedb.org/3/person/popular",
        params={"api_key": TMDB_API_KEY}
    )
    actors = response.json().get("results", [])

    # Randomly pick an actor
    selected_actor = random.choice(actors)

    # Add actor to the temporary database
    db.execute("INSERT INTO actors (name) VALUES (?)", selected_actor["name"])

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
def index():
    # Get a random actor if none has been set
    current_actor = session.get("current_actor") or get_random_actor()
    session["current_actor"] = current_actor
    return render_template("index.html", actor=current_actor)

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
    movies = [{"title": movie["title"]} for movie in data.get("results", [])[:10]]

    return jsonify(movies)
