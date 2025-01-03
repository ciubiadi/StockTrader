# CS50 Finance Application

The **CS50 Finance Application** is a web-based stock trading simulation built using Flask, SQLite, and the CS50 library. It enables users to register, log in, view their portfolio, buy and sell stocks, and check transaction history.

This project is inspired by the CS50 Finance assignment and has been enhanced with additional features for a seamless user experience.

---

## Features

- **User Authentication**: Secure registration and login system using hashed passwords.
- **Portfolio Management**: View stock holdings, including total shares and current prices.
- **Buy and Sell Stocks**: Trade stocks with real-time price lookup.
- **Transaction History**: Track all stock transactions (buys and sells).
- **Dynamic Updates**: Real-time updates to cash balance and portfolio values.
- **Mobile-Friendly**: Designed with responsiveness for mobile and desktop users.

---

## Installation

### Prerequisites
Ensure you have the following installed on your system:
- Python (3.9 or later)
- SQLite
- pip

### Steps
1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
2. **Set Up a Virtual Environment**
```bash
  python -m venv venv
  source venv/bin/activate   # On Windows, use venv\Scripts\activate
```

3. **Install Dependencies**
```bash
  pip install -r requirements.txt
```
  
4. **Set Up the Database Initialize the SQLite database:**
```bash
  flask run
```
The finance.db file will be created in the root directory.

### Usage
1. **Run the Application Start the Flask development server:**
```bash
  flask run
```
Access the application at http://127.0.0.1:5000.

2. **Create an Account Register as a new user and log in to access the application.**

3. **Explore Features**
* Use the Buy tab to purchase stocks.
* Use the Sell tab to sell your stocks.
* View your holdings in the Portfolio tab.
* Check past transactions in the History tab.

### Directory Structure
```php
  .
  ├── app.py               # Main application logic
  ├── templates/           # HTML templates for web pages
  ├── static/              # Static assets (CSS, JS, images)
  ├── helpers.py           # Helper functions for the app
  ├── finance.db           # SQLite database
  ├── requirements.txt     # Python dependencies
  └── README.md            # Project documentation
```

### Dependencies
The project relies on the following Python packages:
* Flask
* Flask-Session
* Werkzeug
* CS50 Library
Install all dependencies using pip install -r requirements.txt.

### Contributing
Contributions are welcome! Please submit a pull request or create an issue to discuss potential changes or features.

### License
This project is licensed under the MIT License. See the LICENSE file for details.

### Acknowledgments
* CS50x: This project is inspired by the CS50 Finance assignment.
* Harvard University: Thanks for providing the foundation for this project.

### Author
Developed by Adrian Albert. Feel free to reach out for questions or feedback.
