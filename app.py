import os

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
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    userCash = user[0]["cash"]

    userTransactions = db.execute("SELECT * FROM purchases WHERE userid = ?", session["user_id"])
    totalTransactions = 0
    print(f"\n user: {user} \n")
    print(f"\n userTransactions: {userTransactions } \n")

    grouped = {}

    for transaction in userTransactions:
        symbol = transaction['symbol']
        shares = transaction['shares']
        price = float(transaction['price'])
        totalTransactions += price * shares

        # Check if the symbol is already in the grouped dictionary
        if symbol not in grouped:
            # Initialize the entry if it doesn't exist
            grouped[symbol] = {'shares': 0, 'price': 0, 'count': 0}

        # Update the values for the symbol
        grouped[symbol]['shares'] += shares
        grouped[symbol]['price'] += price
        grouped[symbol]['count'] += 1

    # Create the new list with merged transactions
    mergedTransactions = []
    for symbol, data in grouped.items():
        # Calculate average price
        avg_price = data['price'] / data['count']
        mergedTransactions.append({
            'symbol': symbol,
            'shares': data['shares'],
            'price': usd(avg_price),  # Format price to 5 decimal places
            'total_price': usd(data['shares'] * avg_price)
        })

    cashTotal = userCash + totalTransactions

    print(f"\n mergedTransactions: {mergedTransactions} \n")

    return render_template("index.html", transactions=mergedTransactions, cash=usd(userCash), cashTotal=usd(cashTotal) )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        requestedSymbol = request.form.get("symbol")
        requestedShares = request.form.get("shares")

        # Ensure symbol was introduced by user
        if not requestedSymbol:
            return apology("symbol not provided", 403)

        # Ensure shares was introduced by user
        if not requestedShares:
            return apology("shares not not provided", 403)

        response = lookup(requestedSymbol)

        if not response:
            return apology("symbol not found", 403)

        # Check user cash and requested total
        userCashList = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        userCash = float(userCashList[0]["cash"])
        requestedTotal = response["price"] * float(requestedShares)

        if userCash < requestedTotal:
            return apology("not enough cash", 403)

        # Store the purchase(buy) transaction in the database
        db.execute("INSERT INTO purchases (userid, symbol, shares, price) VALUES (?, ?, ?, ?)", session["user_id"], requestedSymbol, requestedShares, response["price"])

        # Calculate user remaining cash after the purchase
        remainingCash = userCash - requestedTotal

        # Update the user remaining cash total
        db.execute("UPDATE users SET cash = ? WHERE id = ?", remainingCash, session["user_id"])

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Ensure symbol was found
        if not request.form.get("symbol"):
            return apology("symbol not found", 403)

        # Get the name, price and symbol and use them in quoted template
        if request.form.get("symbol"):
            symbol_response = lookup(request.form.get("symbol"))
            symbol_name = symbol_response['name']
            symbol_price = symbol_response['price']
            symbol = symbol_response['symbol']
            return render_template("quoted.html", name=symbol_name, price=symbol_price, symbol=symbol)
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
         # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) > 0:
            return apology("username already exists", 403)

        # Check if password was retyped correctly
        if request.form.get("password") != request.form.get("passwordConfirm"):
            return apology("passwords don't match")

        hashedPassword = generate_password_hash(request.form.get("password"))
        db.execute("SERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hashedPassword)

        return redirect("/login")
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        return redirect("/")
    else:
        purchases = db.execute("SELECT DISTINCT * FROM purchases WHERE userid = ?", session["user_id"])
        symbols = []

        for purchase in purchases:
            symbols.append(purchase["symbol"])
        print(f"\n purchases: {purchases} \n")
        print(f"\n symbols: {symbols} \n")

        return render_template("sell.html", symbols=symbols)

