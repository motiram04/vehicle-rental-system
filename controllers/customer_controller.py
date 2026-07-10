from flask import Blueprint, flash, render_template, session, redirect, url_for, request

from models.customer_model import CustomerModel

# Customer Blueprint
customer = Blueprint("customer", __name__)


# =========================================================
# Customer Authentication Check
# =========================================================

def customer_required():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "customer":
        return "Access Denied", 403

    return None


# =========================================================
# Dashboard
# =========================================================

@customer.route("/customer/dashboard")
def dashboard():

    check = customer_required()

    if check:
        return check

    vehicles = CustomerModel.get_all_vehicles()

    categories = CustomerModel.get_categories()

    return render_template(
        "customer/dashboard.html",
        vehicles=vehicles,
        categories=categories
    )


# =========================================================
# Vehicle Details
# =========================================================

@customer.route("/customer/vehicle/<int:vehicle_id>")
def vehicle_details(vehicle_id):

    check = customer_required()

    if check:
        return check

    vehicle = CustomerModel.get_vehicle_by_id(vehicle_id)

    return render_template(
        "customer/vehicle_details.html",
        vehicle=vehicle
    )


# =========================================================
# Search Vehicle
# =========================================================

@customer.route("/customer/search")
def search_vehicle():

    check = customer_required()

    if check:
        return check

    search = request.args.get("search", "")

    vehicles = CustomerModel.search_vehicle(search)

    categories = CustomerModel.get_categories()

    return render_template(
        "customer/dashboard.html",
        vehicles=vehicles,
        categories=categories
    )


# =========================================================
# Filter Vehicles
# =========================================================

@customer.route("/customer/filter/<int:category_id>")
def filter_vehicle(category_id):

    check = customer_required()

    if check:
        return check

    vehicles = CustomerModel.filter_category(category_id)

    categories = CustomerModel.get_categories()

    return render_template(
        "customer/dashboard.html",
        vehicles=vehicles,
        categories=categories
    )


# =========================================================
# My Bookings
# =========================================================

# @customer.route("/customer/bookings")
# def my_bookings():

#     check = customer_required()

#     if check:
#         return check

#     return render_template("customer/bookings.html")
@customer.route("/customer/book_vehicle/<int:vehicle_id>", methods=["POST"])
def book_vehicle(vehicle_id):

    check = customer_required()

    if check:
        return check

    customer_id = session["user_id"]

    pickup_date = request.form.get("pickup_date")
    return_date = request.form.get("return_date")

    success, message = CustomerModel.book_vehicle(
        vehicle_id,
        customer_id,
        pickup_date,
        return_date
    )

    flash(message, "success" if success else "danger")

    if success:
        return redirect(url_for("customer.bookings"))

    return redirect(url_for(
        "customer.vehicle_details",
        vehicle_id=vehicle_id
    ))

# =========================================================
# Wishlist
# =========================================================

@customer.route("/customer/wishlist")
def wishlist():

    check = customer_required()

    if check:
        return check

    return render_template("customer/wishlist.html")


# =========================================================
# Profile
# =========================================================

@customer.route("/customer/profile")
def profile():

    check = customer_required()

    if check:
        return check

    return render_template("customer/profile.html")
    
@customer.route("/customer/vehicles")
def vehicles():

    check = customer_required()

    if check:
        return check

    vehicles = CustomerModel.get_all_vehicles()

    return render_template(
        "customer/dashboard.html",
        vehicles=vehicles,
        categories=CustomerModel.get_categories()
    )
    # ==========================================
# My Bookings
# ==========================================

@customer.route("/bookings")
def bookings():

    check = customer_required()

    if check:
        return check

    customer_id = session["user_id"]

    bookings = CustomerModel.get_customer_bookings(customer_id)

    return render_template(
        "customer/bookings.html",
        bookings=bookings
    )