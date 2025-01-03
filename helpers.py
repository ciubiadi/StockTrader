import requests

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper()
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def validateSharesAndSymbol(givenShares, givenSymbol):
    """Validate the submitted symbol and shares for buy and sell operations"""
    requestedSymbol = givenSymbol
    requestedShares = givenShares

    # Ensure symbol was introduced by user
    if not requestedSymbol:
        return apology("symbol not provided", 403)

    # Ensure shares was introduced by user
    if not requestedShares:
        return apology("shares not not provided", 403)

    try:
        requestedShares = int(requestedShares)
    except:
        return apology("shares must be an integer number!", 403)

    if requestedShares <= 0:
        return apology("shares must be a positive integer", 403)

    response = lookup(requestedSymbol)

    if not response:
        return apology("symbol not found", 403)

    return [requestedShares, requestedSymbol, response]

# def validateSharesAndSymbol(givenShares, givenSymbol):
#     """Validate the submitted symbol and shares for buy and sell operations"""
#     requestedSymbol = givenSymbol
#     requestedShares = givenShares

#     error_message = ""

#     # Ensure symbol was introduced by user
#     if not requestedSymbol or requestedSymbol == None:
#         error_message = "symbol not provided"

#     # Ensure shares was introduced by user
#     if not requestedShares:
#         error_message = "shares not not provided"

#     if error_message == "":
#         requestedShares = int(requestedShares)
#         if requestedShares <= 0:
#             error_message = "shares must be a positive integer"

#         if error_message == "":
#             response = lookup(requestedSymbol)
#             if not response:
#                 error_message = "symbol not found"

#     resultList = []
#     if error_message == "":
#         return {
#             'error_message': error_message,
#             'result': {
#                 'requestedShares': requestedShares,
#                 'requestedSymbol': requestedSymbol,
#                 'response': response
#             }
#         }
#     else:
#         return {
#             'error_message': error_message,
#             'result': {}
#         }
