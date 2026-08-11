import os
import uuid

from flask import (
    Blueprint,
    flash,
    render_template,
    session,
    redirect,
    url_for,
    request,
    current_app
)

from werkzeug.utils import secure_filename

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
    # Filter values
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

            vehicles = CustomerModel.filter_price(
                float(max_price)
            )

        except (ValueError, TypeError):

            vehicles = CustomerModel.get_all_vehicles()

    else:

        vehicles = CustomerModel.get_all_vehicles()

    # -----------------------------------------------------
    # Apply price filter
    # -----------------------------------------------------

    if max_price:

        try:

            max_price_value = float(max_price)

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
    # Categories
    # -----------------------------------------------------

    categories = CustomerModel.get_categories()

    # -----------------------------------------------------
    # Customer
    # -----------------------------------------------------

    customer_id = session["user_id"]

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    all_vehicles = CustomerModel.get_all_vehicles()

    total_vehicles = len(all_vehicles)

    available_vehicles = len(all_vehicles)

    # -----------------------------------------------------
    # Customer bookings
    # -----------------------------------------------------

    try:

        bookings = CustomerModel.get_customer_bookings(
            customer_id
        )

    except Exception:

        bookings = []

    # -----------------------------------------------------
    # Booking statistics
    # -----------------------------------------------------

    total_bookings = len(bookings)

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
    # Render dashboard
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

    vehicle = CustomerModel.get_vehicle_by_id(
        vehicle_id
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

    success, message = CustomerModel.book_vehicle(
        vehicle_id,
        customer_id,
        pickup_date,
        return_date
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

    bookings = CustomerModel.get_customer_bookings(
        customer_id
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
        url_for(
            "customer.bookings"
        )
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
# CUSTOMER PROFILE
# =========================================================

@customer.route(
    "/customer/profile",
    methods=["GET", "POST"]
)
def profile():

    check = customer_required()

    if check:
        return check

    customer_id = session["user_id"]

    # =====================================================
    # UPDATE PERSONAL INFORMATION
    # =====================================================

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not full_name:

            flash(
                "Full name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "customer.profile"
                )
            )

        if not email:

            flash(
                "Email is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "customer.profile"
                )
            )

        # -------------------------------------------------
        # Update database
        # -------------------------------------------------

        success, message = (
            CustomerModel.update_customer_profile(
                customer_id,
                full_name,
                email,
                phone
            )
        )

        # -------------------------------------------------
        # Update session name
        # -------------------------------------------------

        if success:

            session["full_name"] = full_name

        flash(
            message,
            "success" if success else "danger"
        )

        return redirect(
            url_for(
                "customer.profile"
            )
        )

    # =====================================================
    # GET PROFILE DATA
    # =====================================================

    customer_data = CustomerModel.get_customer_profile(
    customer_id
    )

    if not customer_data:
        flash(
            "Customer profile not found.",
            "danger"
        )

        return redirect(
            url_for("customer.dashboard")
        )

    # Keep profile picture available in navbar
    if customer_data.get("profile_picture"):
        session["profile_picture"] = customer_data["profile_picture"]
    # =====================================================
    # GET BOOKINGS
    # =====================================================

    bookings = (
        CustomerModel.get_customer_bookings(
            customer_id
        )
    )

    # =====================================================
    # BOOKING STATISTICS
    # =====================================================

    total_bookings = len(bookings)

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

    cancelled_bookings = len([
        booking
        for booking in bookings
        if str(
            booking.get(
                "booking_status",
                ""
            )
        ).lower() == "cancelled"
    ])

    stats = {

        "total_bookings":
            total_bookings,

        "pending_bookings":
            pending_bookings,

        "approved_bookings":
            approved_bookings,

        "completed_bookings":
            completed_bookings,

        "cancelled_bookings":
            cancelled_bookings
    }

    # =====================================================
    # RECENT BOOKINGS
    # =====================================================

    recent_bookings = bookings[:3]

    # =====================================================
    # RENDER PROFILE
    # =====================================================

    return render_template(

        "customer/profile.html",

        customer=customer_data,

        stats=stats,

        recent_bookings=recent_bookings
    )


# =========================================================
# CUSTOMER PROFILE PICTURE
# =========================================================

@customer.route(
    "/customer/profile/upload-picture",
    methods=["POST"]
)
def upload_profile_picture():

    check = customer_required()

    if check:
        return check

    customer_id = session["user_id"]

    # =====================================================
    # GET FILE
    # =====================================================

    file = request.files.get(
        "profile_picture"
    )

    if not file or file.filename == "":

        flash(
            "Please select a profile picture.",
            "danger"
        )

        return redirect(
            url_for(
                "customer.profile"
            )
        )

    # =====================================================
    # ALLOWED EXTENSIONS
    # =====================================================

    allowed_extensions = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    # =====================================================
    # SECURE ORIGINAL FILENAME
    # =====================================================

    original_filename = secure_filename(
        file.filename
    )

    if not original_filename:

        flash(
            "Invalid file name.",
            "danger"
        )

        return redirect(
            url_for(
                "customer.profile"
            )
        )

    # =====================================================
    # GET EXTENSION
    # =====================================================

    if "." not in original_filename:

        flash(
            "Invalid image file.",
            "danger"
        )

        return redirect(
            url_for(
                "customer.profile"
            )
        )

    extension = (
        original_filename
        .rsplit(".", 1)[1]
        .lower()
    )

    # =====================================================
    # VALIDATE EXTENSION
    # =====================================================

    if extension not in allowed_extensions:

        flash(
            "Only JPG, JPEG, PNG and WEBP images are allowed.",
            "danger"
        )

        return redirect(
            url_for(
                "customer.profile"
            )
        )

    # =====================================================
    # UPLOAD DIRECTORY
    # =====================================================

    upload_folder = os.path.join(

        current_app.root_path,

        "static",

        "uploads",

        "profiles"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    # =====================================================
    # GENERATE UNIQUE FILENAME
    # =====================================================

    new_filename = (
        f"customer_{customer_id}_"
        f"{uuid.uuid4().hex}."
        f"{extension}"
    )

    # =====================================================
    # FILE PATH
    # =====================================================

    file_path = os.path.join(
        upload_folder,
        new_filename
    )

    # =====================================================
    # SAVE FILE
    # =====================================================

    try:

        file.save(
            file_path
        )

    except Exception as e:

        flash(
            f"Unable to save profile picture: {str(e)}",
            "danger"
        )

        return redirect(
            url_for(
                "customer.profile"
            )
        )

    # =====================================================
    # SAVE FILENAME TO DATABASE
    # =====================================================

    success, message = (
        CustomerModel
        .update_customer_profile_picture(
            customer_id,
            new_filename
        )
    )

    # =====================================================
    # DELETE FILE IF DATABASE UPDATE FAILED
    # =====================================================

    if not success:

        if os.path.exists(file_path):

            os.remove(file_path)

    # =====================================================
    # FLASH MESSAGE
    # =====================================================

    flash(
        message,
        "success" if success else "danger"
    )

    return redirect(
        url_for(
            "customer.profile"
        )
    )