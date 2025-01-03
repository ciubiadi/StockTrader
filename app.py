import os
from datetime import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers.update({
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Expires": 0,
        "Pragma": "no-cache"
    })
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    userCash = user[0]["cash"]

    # Retrieve all transactions of the current user
    userStocks = db.execute(
        "SELECT symbol, name, price, SUM(shares) as totalShares FROM purchases WHERE userid = ? GROUP BY symbol", session["user_id"])

    total = userCash
    stocks = []

    for stock in userStocks:
        if stock["totalShares"] > 0:
            stocks.append(stock)
        total += stock["price"] * stock["totalShares"]

    cashTotal = userCash + total

    return render_template("index.html",
                           cash=userCash, stocks=stocks, total=total, cashTotal=cashTotal, usd=usd
                           )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol", "").upper()
        shares = request.form.get("shares", "")

        # Validate input
        if not symbol or not shares.isdigit() or int(shares) <= 0:
            return apology("Invalid symbol or share quantity", 400)

        shares = int(shares)
        stock = lookup(symbol)
        if not stock:
            return apology("Stock not found", 400)

        # Check user funds
        user = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]
        total_cost = stock["price"] * shares
        if user["cash"] < total_cost:
            return apology("Insufficient funds", 403)

        # Update database
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, session["user_id"])
        db.execute("""
            INSERT INTO purchases (userid, symbol, shares, price, purchase_datetime, name, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, session["user_id"], symbol, shares, stock["price"], datetime.now(), stock["name"], "buy")

        flash(f"Bought {shares} shares of {symbol}")
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT * FROM purchases WHERE userid = ?", session["user_id"])
    return render_template("history.html", transactions=transactions, usd=usd)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return apology("Must provide username and password", 403)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not user or not check_password_hash(user[0]["hash"], password):
            return apology("Invalid username or password", 403)

        session["user_id"] = user[0]["id"]
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol", "").upper()
        if not symbol:
            return apology("Missing symbol", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("Stock not found", 400)

        return render_template("quoted.html", name=stock["name"], price=usd(stock["price"]), symbol=stock["symbol"])
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password:
            return apology("Username and password are required", 400)
        if password != confirmation:
            return apology("Passwords must match", 400)
        if db.execute("SELECT * FROM users WHERE username = ?", username):
            return apology("Username already exists", 400)

        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)
        return redirect("/login")
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol", "").upper()
        shares = request.form.get("shares", "")

        if not symbol or not shares.isdigit() or int(shares) <= 0:
            return apology("Invalid input", 400)

        shares = int(shares)
        stock = lookup(symbol)
        if not stock:
            return apology("Stock not found", 400)

        # Check user's stock holdings
        holding = db.execute("""
            SELECT SUM(shares) AS totalShares FROM purchases
            WHERE userid = ? AND symbol = ?
        """, session["user_id"], symbol)
        if holding[0]["totalShares"] < shares:
            return apology("Not enough shares", 400)

        # Update database
        total_sale = stock["price"] * shares
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_sale, session["user_id"])
        db.execute("""
            INSERT INTO purchases (userid, symbol, shares, price, purchase_datetime, name, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, session["user_id"], symbol, -shares, stock["price"], datetime.now(), stock["name"], "sell")

        flash(f"Sold {shares} shares of {symbol}")
        return redirect("/")
    else:
        symbols = db.execute("""
            SELECT symbol FROM purchases
            WHERE userid = ? GROUP BY symbol HAVING SUM(shares) > 0
        """, session["user_id"])
        return render_template("sell.html", symbols=symbols)
