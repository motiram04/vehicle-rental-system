from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session

from models.user_model import UserModel

auth = Blueprint("auth", __name__)
@auth.route("/")
@auth.route("/login")
def login():

    return render_template("auth/login.html")
@auth.route("/signup")
def signup():

    return render_template("auth/signup.html")
@auth.route("/signup", methods=["POST"])
def register():

    full_name = request.form["fullname"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    role = request.form["role"]

    if password != confirm_password:

        flash("Passwords do not match", "danger")

        return redirect(url_for("auth.signup"))

    user = UserModel.get_user_by_email(email)

    if user:

        flash("Email already exists.", "danger")

        return redirect(url_for("auth.signup"))

    UserModel.create_user(

        full_name,
        email,
        phone,
        address,
        password,
        role

    )

    flash("Account Created Successfully", "success")

    return redirect(url_for("auth.login"))
@auth.route("/login", methods=["POST"])
def login_post():

    email = request.form["email"]
    password = request.form["password"]

    user = UserModel.get_user_by_email(email)

    if not user:

        flash("Email not found.", "danger")

        return redirect(url_for("auth.login"))

    if user["status"] != "active":

        flash("Account is inactive.", "danger")

        return redirect(url_for("auth.login"))

    if not UserModel.verify_password(
            user["password"],
            password
    ):

        flash("Invalid password.", "danger")

        return redirect(url_for("auth.login"))

    UserModel.update_last_login(user["user_id"])

    session["user_id"] = user["user_id"]
    session["full_name"] = user["full_name"]
    session["email"] = user["email"]
    session["role"] = user["role"]
    session["profile_picture"] = user["profile_picture"]

    if user["role"] == "admin":

        return redirect("/admin/dashboard")

    elif user["role"] == "owner":

        return redirect("/owner/dashboard")

    else:

        return redirect("/customer/dashboard")

@auth.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("auth.login"))

