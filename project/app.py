from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to the Oracle database [TODO]
'''db = '''

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

    return render_template("index.html")

# query route
@app.route("/query", methods=["GET"])
def query():
    query = request.args.get('q')
    # If query is not empty, fetch matching movie titles
    if query:
        results = db.execute("SELECT title FROM movies WHERE title LIKE ? LIMIT 10", f"%{query}%")
    else:
        results = []
    # Return results in JSON format
    return jsonify(results)
