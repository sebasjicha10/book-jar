import os
import requests

from flask import Flask, session, render_template, request, redirect, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required


app = Flask(__name__)

# Data Base
app.config["DATABASE_URL"]="postgres://rjnvzxxwghgcfb:367546554eeb44b550bdc1d735516aecd56f66b47fee0490a0a662b6a8cbdf77@ec2-52-202-146-43.compute-1.amazonaws.com:5432/d14a26rabqvt84"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    """Default route"""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    
    #Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":

        # Define variables
        username = (request.form.get("username").lower())
        password = request.form.get("password")

        # Ensure both inputs where submitted 
        if not username or not password:
            return render_template("error.html", message="Please provide a username and password.")

        # Query database for user_name
        given_username = db.execute("SELECT * FROM users WHERE username = :username", {'username': username}).fetchall()

        # Ensure user_id exists and password is correct
        if len(given_username) != 1 or not check_password_hash(given_username[0]["password"], password):
            return render_template("error.html", message="Invalid usernamea nd/or password.")

        # Remember which user has logged in
        session["user_id"] = given_username[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached rout via GET
    else :
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    #Forget any user_id
    session.clear()
   
    # User reached route via POST
    if request.method == "POST":
        # Define variables
        username = (request.form.get("username").lower())
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure both inputs where submitted 
        if not username or not password:
            return render_template("error.html", message="Please provide a username and password.")

        # Ensure new username is prompted 
        username_taken = db.execute("SELECT username FROM users WHERE username = :username", {'username': username}).fetchone()
        if username_taken:
            return render_template("error.html", message="Username already taken.")

        # Ensure password is at least 6 chars long
        if len(password) < 6:
            return render_template("error.html", message="Password must be at least 6 characters long.")

        # Ensure password matches
        elif not (confirmation == password):
            return render_template("error.html", message="Passwords must match.")

        # Add user to data base 
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password": generate_password_hash(password)})
        db.commit()

        # Remember which user has logged in
        user_id = db.execute("SELECT user_id FROM users WHERE username = :username", {'username': username}).fetchall()
        session["user_id"] = user_id[0][0]
        
        # Redirect user to home page
        return redirect("/")

    # User reached rout via GET
    else :
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
  
    # Redirect user to login form
    return redirect("/")


@app.route("/search_books", methods=["GET"])
@login_required
def search_books():
    """Given an search input, returns what is available after fetching the database"""
   
    # Retrieve input prompted by the user
    search_input = request.args.get("search")

    if search_input == "":
        return render_template("search.html", search=search_input)

    # Fetch database
    database_response = db.execute("SELECT * FROM books WHERE title iLIKE :entry OR author iLIKE :entry OR isbn iLIKE :entry", {'entry': "%" + search_input + "%"}).fetchall()

    return render_template("search.html", results=database_response, search=search_input)


@app.route("/books/<string:isbn>")
@login_required
def book(isbn):
    """Lists details about a single book."""

    user = session["user_id"]

    # Make sure book exits
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return render_template("error.html", message="Sorry, no info available for that book.")

    # goodreads api request
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "nZ64AJPcsnoHylIwopeYg", "isbns": book.isbn})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    goodreads = data["books"][0]

    # Fetch reviews
    reviews = db.execute("SELECT DISTINCT review_id, rating, review, reviews.user_id, username FROM reviews JOIN users ON users.user_id = reviews.user_id::int WHERE book_id::int = :book_id;", {"book_id": book.book_id}).fetchall()

    # Ensure one review per user
    reviewed = False
    for review in reviews:
        if int(review.user_id) == int(user):
            reviewed = True

    return render_template("book.html", book=book, ratings_count=goodreads['work_ratings_count'], average_rating=goodreads['average_rating'], reviews=reviews, reviewed=reviewed)
   

@app.route("/review", methods=["POST"])
@login_required
def review():
    """Add reviews"""

    # Variables 
    rating = request.form.get("rating")
    review = request.form.get("review")
    book_id = request.form.get("book")
    user = session["user_id"]

    isbn = db.execute("SELECT isbn FROM books WHERE book_id = :book_id", {"book_id": book_id}).fetchone()

    if len(review) <= 0 or len(review) > 255:
        return redirect(f"/books/{isbn[0]}")

    # Taking care of duplicate submissions 
    try:
        db.execute("INSERT INTO reviews (book_id, user_id, review, rating) VALUES (:book, :user, :review, :rating)", {"book": book_id, "user": user, "review": review, "rating": rating})
        db.commit()
    except Exception:
        pass

    flash('Your review was succesfully added')
    return redirect(f"/books/{isbn[0]}")


@app.route("/api/<string:isbn>")
def book_api(isbn):
    """Return details about a single book."""

    # Make sure book exits
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid book isbn"}), 404

    reviews = db.execute("SELECT COUNT(*), AVG(rating::int) from reviews WHERE book_id = ':book_id';", {"book_id": book.book_id}).fetchall()
   
    if reviews[0][1] is None:
        count = score = "none"
    else: 
        count = reviews[0][0]
        score = float(reviews[0][1])

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count" : count,
        "average_score": score,
    })



    
    

  
    





 