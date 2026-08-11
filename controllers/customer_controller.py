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
# CUSTOMER BLUEPRINT
# =========================================================

customer = Blueprint(
    "customer",
    __name__
)


# =========================================================
# CUSTOMER AUTHENTICATION CHECK
# =========================================================

def customer_required():

    if "user_id" not in session:

        return redirect(
            url_for("auth.login")
        )


    if session.get("role") != "customer":

        return "Access Denied", 403


    return None


# =========================================================
# CUSTOMER DASHBOARD
# =========================================================

@customer.route("/customer/dashboard")
def dashboard():

    check = customer_required()

    if check:
        return check


    # -----------------------------------------------------
    # Get filter values
    # -----------------------------------------------------

    search = request.args.get(
        "search",
        ""
    ).strip()


    category_id = request.args.get(
        "category",
        ""
    ).strip()


    max_price = request.args.get(
        "max_price",
        ""
    ).strip()


    # -----------------------------------------------------
    # Get vehicles
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

        except ValueError:

            vehicles = CustomerModel.get_all_vehicles()

    elif max_price:

        try:

            price = float(max_price)

            vehicles = CustomerModel.filter_price(
                price
            )

        except (ValueError, TypeError):

            vehicles = CustomerModel.get_all_vehicles()

    else:

        vehicles = CustomerModel.get_all_vehicles()


    # -----------------------------------------------------
    # Apply price filter together with search/category
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
            TypeError
        ):

            pass


    # -----------------------------------------------------
    # Categories
    # -----------------------------------------------------

    categories = (
        CustomerModel.get_categories()
    )


    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    total_vehicles = len(
        CustomerModel.get_all_vehicles()
    )


    available_vehicles = len(
        CustomerModel.get_all_vehicles()
    )


    # -----------------------------------------------------
    # Customer bookings
    # -----------------------------------------------------

    customer_id = session["user_id"]

    try:

        bookings = (
            CustomerModel
            .get_customer_bookings(
                customer_id
            )
        )

    except Exception:

        bookings = []


    # -----------------------------------------------------
    # Booking statistics
    # -----------------------------------------------------

    total_bookings = len(
        bookings
    )


    pending_bookings = len([
        booking
        for booking in bookings
        if str(
            booking.get(
                "booking_status",
                ""
            )
        ).lower() == "pending"
    ])


    approved_bookings = len([
        booking
        for booking in bookings
        if str(
            booking.get(
                "booking_status",
                ""
            )
        ).lower() == "approved"
    ])


    completed_bookings = len([
        booking
        for booking in bookings
        if str(
            booking.get(
                "booking_status",
                ""
            )
        ).lower() == "completed"
    ])


    # -----------------------------------------------------
    # Total spending
    # -----------------------------------------------------

    total_spent = 0


    for booking in bookings:

        status = str(
            booking.get(
                "booking_status",
                ""
            )
        ).lower()


        if status in [
            "approved",
            "completed"
        ]:

            try:

                total_spent += float(
                    booking.get(
                        "total_amount",
                        0
                    ) or 0
                )

            except (
                ValueError,
                TypeError
            ):

                pass


    # -----------------------------------------------------
    # Dashboard stats
    # -----------------------------------------------------

    stats = {

        "total_vehicles":
            total_vehicles,

        "available_vehicles":
            available_vehicles,

        "total_bookings":
            total_bookings,

        "pending_bookings":
            pending_bookings,

        "approved_bookings":
            approved_bookings,

        "completed_bookings":
            completed_bookings,

        "total_spent":
            total_spent

    }


    # -----------------------------------------------------
    # Render
    # -----------------------------------------------------

    return render_template(

        "customer/dashboard.html",

        vehicles=vehicles,

        categories=categories,

        bookings=bookings,

        stats=stats,

        search=search,

        category_id=category_id,

        max_price=max_price

    )


# =========================================================
# VEHICLE DETAILS
# =========================================================

@customer.route(
    "/customer/vehicle/<int:vehicle_id>"
)
def vehicle_details(vehicle_id):

    check = customer_required()

    if check:
        return check


    vehicle = (
        CustomerModel
        .get_vehicle_by_id(
            vehicle_id
        )
    )


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


    return render_template(

        "customer/vehicle_details.html",

        vehicle=vehicle

    )


# =========================================================
# BOOK VEHICLE
# =========================================================

@customer.route(
    "/customer/book_vehicle/<int:vehicle_id>",
    methods=["POST"]
)
def book_vehicle(vehicle_id):

    check = customer_required()

    if check:
        return check


    customer_id = session["user_id"]


    pickup_date = request.form.get(
        "pickup_date"
    )


    return_date = request.form.get(
        "return_date"
    )


    if not pickup_date or not return_date:

        flash(
            "Please select pickup and return dates.",
            "danger"
        )

        return redirect(
            url_for(
                "customer.vehicle_details",
                vehicle_id=vehicle_id
            )
        )


    success, message = (
        CustomerModel.book_vehicle(
            vehicle_id,
            customer_id,
            pickup_date,
            return_date
        )
    )


    flash(
        message,
        "success" if success else "danger"
    )


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
# VEHICLES
# =========================================================

@customer.route("/customer/vehicles")
def vehicles():

    check = customer_required()

    if check:
        return check


    return redirect(
        url_for(
            "customer.dashboard"
        )
    )


# =========================================================
# MY BOOKINGS
# =========================================================

@customer.route("/customer/bookings")
def bookings():

    check = customer_required()

    if check:
        return check


    customer_id = session["user_id"]


    bookings = (
        CustomerModel
        .get_customer_bookings(
            customer_id
        )
    )


    return render_template(

        "customer/bookings.html",

        bookings=bookings

    )
    # =========================================================
# CANCEL BOOKING
# =========================================================

@customer.route(
    "/customer/cancel-booking/<int:booking_id>",
    methods=["POST"]
)
def cancel_booking(booking_id):

    check = customer_required()

    if check:
        return check

    customer_id = session["user_id"]

    success, message = CustomerModel.cancel_booking(
        booking_id,
        customer_id
    )

    flash(
        message,
        "success" if success else "danger"
    )

    return redirect(
        url_for("customer.bookings")
    )


# =========================================================
# WISHLIST
# =========================================================

@customer.route("/customer/wishlist")
def wishlist():

    check = customer_required()

    if check:
        return check


    return render_template(
        "customer/wishlist.html"
    )


# =========================================================
# PROFILE
# =========================================================

@customer.route("/customer/profile")
def profile():

    check = customer_required()

    if check:
        return check


    return render_template(
        "customer/profile.html"
    )