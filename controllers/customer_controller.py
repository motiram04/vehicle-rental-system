from flask import (
    Blueprint,
    flash,
    render_template,
    session,
    redirect,
    url_for,
    request
)

from models.customer_model import CustomerModel


# =========================================================
# Customer Blueprint
# =========================================================

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
# Customer Dashboard
# =========================================================

@customer.route("/customer/dashboard")
def dashboard():

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    check = customer_required()

    if check:
        return check

    customer_id = session["user_id"]


    # -----------------------------------------------------
    # Get Filter Values
    # -----------------------------------------------------

    search = request.args.get(
        "search",
        ""
    ).strip()

    category_id = request.args.get(
        "category_id",
        ""
    ).strip()

    max_price = request.args.get(
        "max_price",
        ""
    ).strip()

    availability = request.args.get(
        "availability",
        ""
    ).strip()


    # -----------------------------------------------------
    # Get Vehicles
    # -----------------------------------------------------

    if search:

        vehicles = CustomerModel.search_vehicle(
            search
        )

    elif category_id:

        try:

            vehicles = CustomerModel.filter_category(
                int(category_id)
            )

        except (ValueError, TypeError):

            vehicles = CustomerModel.get_all_vehicles()

    else:

        vehicles = CustomerModel.get_all_vehicles()


    # -----------------------------------------------------
    # Maximum Price Filter
    # -----------------------------------------------------

    if max_price:

        try:

            max_price_value = float(
                max_price
            )

            vehicles = [
                vehicle
                for vehicle in vehicles

                if float(
                    vehicle["rent_per_day"]
                ) <= max_price_value
            ]

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            pass


    # -----------------------------------------------------
    # Availability Filter
    # -----------------------------------------------------

    if availability:

        vehicles = [
            vehicle
            for vehicle in vehicles

            if str(
                vehicle.get(
                    "availability_status",
                    ""
                )
            ).lower()
            ==
            availability.lower()
        ]


    # -----------------------------------------------------
    # Categories
    # -----------------------------------------------------

    categories = CustomerModel.get_categories()


    # -----------------------------------------------------
    # Customer Bookings
    # -----------------------------------------------------

    bookings = CustomerModel.get_customer_bookings(
        customer_id
    )


    # -----------------------------------------------------
    # Dashboard Statistics
    # -----------------------------------------------------

    stats = CustomerModel.get_dashboard_stats(
        customer_id
    )


    # -----------------------------------------------------
    # Recent Bookings
    # -----------------------------------------------------

    recent_bookings = CustomerModel.get_recent_bookings(
        customer_id,
        5
    )


    # -----------------------------------------------------
    # Render Dashboard
    # -----------------------------------------------------

    return render_template(

        "customer/dashboard.html",

        vehicles=vehicles,

        categories=categories,

        bookings=bookings,

        stats=stats,

        recent_bookings=recent_bookings,

        search=search,

        category_id=category_id,

        max_price=max_price,

        availability=availability

    )


# =========================================================
# Vehicle Details
# =========================================================

@customer.route(
    "/customer/vehicle/<int:vehicle_id>"
)
def vehicle_details(vehicle_id):

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    check = customer_required()

    if check:
        return check


    # -----------------------------------------------------
    # Get Vehicle
    # -----------------------------------------------------

    vehicle = CustomerModel.get_vehicle_by_id(
        vehicle_id
    )


    # -----------------------------------------------------
    # Vehicle Not Found
    # -----------------------------------------------------

    if not vehicle:

        flash(
            "Vehicle not found.",
            "danger"
        )

        return redirect(
            url_for(
                "customer.dashboard"
            )
        )


    # -----------------------------------------------------
    # Vehicle Details Page
    # -----------------------------------------------------

    return render_template(

        "customer/vehicle_details.html",

        vehicle=vehicle

    )


# =========================================================
# Book Vehicle
# =========================================================

@customer.route(
    "/customer/book_vehicle/<int:vehicle_id>",
    methods=["POST"]
)
def book_vehicle(vehicle_id):

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    check = customer_required()

    if check:
        return check


    # -----------------------------------------------------
    # Customer ID
    # -----------------------------------------------------

    customer_id = session["user_id"]


    # -----------------------------------------------------
    # Booking Dates
    # -----------------------------------------------------

    pickup_date = request.form.get(
        "pickup_date"
    )

    return_date = request.form.get(
        "return_date"
    )


    # -----------------------------------------------------
    # Validate Dates
    # -----------------------------------------------------

    if not pickup_date or not return_date:

        flash(
            "Pickup date and return date are required.",
            "danger"
        )

        return redirect(
            url_for(
                "customer.vehicle_details",
                vehicle_id=vehicle_id
            )
        )


    # -----------------------------------------------------
    # Create Booking
    # -----------------------------------------------------

    success, message = CustomerModel.book_vehicle(

        vehicle_id,

        customer_id,

        pickup_date,

        return_date

    )


    # -----------------------------------------------------
    # Flash Message
    # -----------------------------------------------------

    flash(

        message,

        "success"
        if success
        else "danger"

    )


    # -----------------------------------------------------
    # Redirect
    # -----------------------------------------------------

    if success:

        return redirect(
            url_for(
                "customer.bookings"
            )
        )


    return redirect(

        url_for(

            "customer.vehicle_details",

            vehicle_id=vehicle_id

        )

    )


# =========================================================
# Vehicles
# =========================================================

@customer.route(
    "/customer/vehicles"
)
def vehicles():

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    check = customer_required()

    if check:
        return check


    # -----------------------------------------------------
    # Redirect to Dashboard
    # -----------------------------------------------------

    return redirect(

        url_for(
            "customer.dashboard"
        )

    )


# =========================================================
# My Bookings
# =========================================================

@customer.route(
    "/customer/bookings"
)
def bookings():

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    check = customer_required()

    if check:
        return check


    # -----------------------------------------------------
    # Customer ID
    # -----------------------------------------------------

    customer_id = session["user_id"]


    # -----------------------------------------------------
    # Get Bookings
    # -----------------------------------------------------

    bookings = CustomerModel.get_customer_bookings(

        customer_id

    )


    # -----------------------------------------------------
    # Render
    # -----------------------------------------------------

    return render_template(

        "customer/bookings.html",

        bookings=bookings

    )


# =========================================================
# Wishlist
# =========================================================

@customer.route(
    "/customer/wishlist"
)
def wishlist():

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    check = customer_required()

    if check:
        return check


    return render_template(

        "customer/wishlist.html"

    )


# =========================================================
# Profile
# =========================================================

@customer.route(
    "/customer/profile"
)
def profile():

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    check = customer_required()

    if check:
        return check


    return render_template(

        "customer/profile.html"

    )