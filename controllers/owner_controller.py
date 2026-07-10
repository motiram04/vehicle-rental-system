import os
from werkzeug.utils import secure_filename

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app
)

from models.owner_model import OwnerModel

owner = Blueprint(
    "owner",
    __name__,
    url_prefix="/owner"
)  


# ==========================================
# Owner Login Required
# ==========================================

def owner_required():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "owner":
        flash("Access Denied!", "danger")
        return redirect(url_for("auth.login"))

    return None


# ==========================================
# Dashboard
# ==========================================

@owner.route("/dashboard")
def dashboard():
    
   

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    stats = OwnerModel.dashboard_statistics(owner_id)

    recent_vehicles = OwnerModel.recent_vehicles(owner_id)
     

    return render_template(

        "owner/dashboard.html",

        total_vehicles=stats["total_vehicles"],
        approved_vehicles=stats["approved_vehicles"],
        pending_vehicles=stats["pending_vehicles"],
        rejected_vehicles=stats["rejected_vehicles"],

        total_bookings=0,
        total_earnings=0,

        recent_vehicles=recent_vehicles,

        recent_bookings=[]

    )
    

# ==========================================
# My Vehicles
# ==========================================

@owner.route("/vehicles")
def vehicles():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    vehicles = OwnerModel.get_owner_vehicles(owner_id)

    return render_template(

        "owner/vehicles.html",

        vehicles=vehicles

    )


# ==========================================
# Add Vehicle
# ==========================================

@owner.route("/add_vehicle", methods=["GET", "POST"])
def add_vehicle():

    check = owner_required()

    if check:
        return check

    if request.method == "POST":

        vehicle_name = request.form["vehicle_name"]
        category_id = request.form["category_id"]
        model = request.form["model"]
        vehicle_number = request.form["vehicle_number"]
        rent_per_day = request.form["rent_per_day"]
        description = request.form["description"]
        availability_status = request.form["availability_status"]

        image = request.files["image"]

        filename = "default_vehicle.jpg"  # Default image path

        if image and image.filename != "":

            filename = secure_filename(image.filename)

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "vehicles"
            )

            os.makedirs(upload_folder, exist_ok=True)

            image.save(os.path.join(upload_folder, filename))

        data = {

            "owner_id": session["user_id"],
            "category_id": category_id,
            "vehicle_name": vehicle_name,
            "model": model,
            "vehicle_number": vehicle_number,
            "rent_per_day": rent_per_day,
            "description": description,
            "availability_status": availability_status,
            "image": filename

        }

        OwnerModel.add_vehicle(data)

        flash(
            "Vehicle uploaded successfully. Waiting for admin approval.",
            "success"
        )

        return redirect(url_for("owner.vehicles"))

    categories = OwnerModel.get_categories()

    return render_template(

        "owner/add_vehicle.html",

        categories=categories

    )


# ==========================================
# Bookings
    # # ==========================================

    # # ==========================================
# Bookings
# ==========================================

# @owner.route("/bookings")
# def bookings():

#     check = owner_required()

#     if check:
#         return check

#     return render_template("owner/bookings.html")


# ==========================================
# Earnings
# ==========================================

@owner.route("/earnings")
def earnings():

    check = owner_required()

    if check:
        return check

    return render_template("owner/earnings.html")


# ==========================================
# Profile
# ==========================================

@owner.route("/profile")
def profile():

    check = owner_required()

    if check:
        return check

    return render_template("owner/profile.html")


# ==========================================
# Settings
# ==========================================

@owner.route("/settings")
def settings():

    check = owner_required()

    if check:
        return check

    return render_template("owner/settings.html")
# =====================================================
# Owner Booking Requests
# =====================================================

@owner.route("/bookings")
def bookings():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    bookings = OwnerModel.get_booking_requests(owner_id)

    return render_template(
        "owner/bookings.html",
        bookings=bookings
    )
    # =====================================================
# Approve Booking
# =====================================================

@owner.route("/approve-booking/<int:booking_id>")
def approve_booking(booking_id):

    check = owner_required()

    if check:
        return check

    success, message = OwnerModel.approve_booking(booking_id)

    flash(message, "success" if success else "danger")

    return redirect(url_for("owner.bookings"))

# =====================================================
# Reject Booking
# =====================================================

@owner.route("/reject-booking/<int:booking_id>")
def reject_booking(booking_id):

    check = owner_required()

    if check:
        return check

    success, message = OwnerModel.reject_booking(booking_id)

    flash(message, "warning" if success else "danger")

    return redirect(url_for("owner.bookings"))