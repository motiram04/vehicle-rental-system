from flask import Flask
from config import Config
from database.db import mysql
from controllers.admin_controller import admin
from controllers.owner_controller import owner
from controllers.auth_controller import auth
from controllers.customer_controller import customer

app = Flask(__name__)


app.config.from_object(Config)


mysql.init_app(app)

app.register_blueprint(auth)

app.register_blueprint(admin)


app.register_blueprint(owner)


app.register_blueprint(customer)
if __name__ == "__main__":
    app.run(debug=True)