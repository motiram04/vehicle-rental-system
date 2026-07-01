from flask import Flask

from config import *

from database.db import mysql

from controllers.auth_controller import auth

app = Flask(__name__)

# ------------------------
# Flask Configuration
# ------------------------

app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["MYSQL_CURSORCLASS"] = MYSQL_CURSORCLASS

app.secret_key = SECRET_KEY

# ------------------------
# Initialize Database
# ------------------------

mysql.init_app(app)

# ------------------------
# Register Blueprints
# ------------------------

app.register_blueprint(auth)



if __name__ == "__main__":
    app.run(debug=True)