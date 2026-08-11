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

    # Get logged-in owner profile
    owner_data = OwnerModel.get_owner_profile(owner_id)

    if not owner_data:
        flash("Owner profile not found.", "danger")
        return redirect(url_for("auth.login"))

    # Get dashboard statistics
    stats = OwnerModel.dashboard_statistics(owner_id)

    # Get recent vehicles
    recent_vehicles = OwnerModel.recent_vehicles(owner_id)

    # Get owner booking requests
    all_bookings = OwnerModel.get_booking_requests(owner_id)

    # Show only latest 5 bookings
    recent_bookings = all_bookings[:5]

    return render_template(
        "owner/dashboard.html",

        # Owner information
        owner=owner_data,

        # Vehicle statistics
        total_vehicles=stats["total_vehicles"],
        approved_vehicles=stats["approved_vehicles"],
        pending_vehicles=stats["pending_vehicles"],
        rejected_vehicles=stats["rejected_vehicles"],

        # Booking statistics
        total_bookings=stats["total_bookings"],
        pending_bookings=stats["pending_bookings"],

        # Earnings
        total_earnings=stats["total_earnings"],

        # Recent data
        recent_vehicles=recent_vehicles,
        recent_bookings=recent_bookings
    )



# @owner.route("/dashboard")
# def dashboard():

#     check = owner_required()

#     if check:
#         return check

#     owner_id = session["user_id"]

#     # Get dashboard statistics
#     stats = OwnerModel.dashboard_statistics(owner_id)

#     # Get recent vehicles
#     recent_vehicles = OwnerModel.recent_vehicles(owner_id)

#     # Get owner booking requests
#     all_bookings = OwnerModel.get_booking_requests(owner_id)

#     # Show only latest 5 bookings
#     recent_bookings = all_bookings[:5]

#     return render_template(
#         "owner/dashboard.html",

#         # Vehicle statistics
#         total_vehicles=stats["total_vehicles"],
#         approved_vehicles=stats["approved_vehicles"],
#         pending_vehicles=stats["pending_vehicles"],
#         rejected_vehicles=stats["rejected_vehicles"],

#         # Booking statistics
#         total_bookings=stats["total_bookings"],
#         pending_bookings=stats["pending_bookings"],

#         # Earnings
#         total_earnings=stats["total_earnings"],

#         # Recent data
#         recent_vehicles=recent_vehicles,
#         recent_bookings=recent_bookings
#     )

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

# ==========================================
# Owner Earnings
# ==========================================

@owner.route("/earnings")
def earnings():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    # Get earnings summary
    earnings_summary = OwnerModel.get_earnings_summary(owner_id)

    # Get completed earnings history
    earnings_history = OwnerModel.get_earnings_history(owner_id)

    return render_template(
        "owner/earnings.html",
        summary=earnings_summary,
        earnings=earnings_history
    )


# ==========================================
# Owner Profile
# ==========================================

@owner.route("/profile", methods=["GET", "POST"])
def profile():

    # Check whether the logged-in user is an owner
    check = owner_required()

    if check:
        return check

    # Get logged-in owner's ID
    owner_id = session["user_id"]

    # ==========================================================
    # UPDATE PROFILE
    # ==========================================================

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        # Get account status from the form
        status = request.form.get("status", "").strip()

        # ------------------------------------------------------
        # Validate required fields
        # ------------------------------------------------------

        if not full_name or not email:

            flash(
                "Full name and email are required.",
                "danger"
            )

            return redirect(url_for("owner.profile"))

        # ------------------------------------------------------
        # Validate status
        # ------------------------------------------------------

        if status not in ["Active", "Inactive"]:

            flash(
                "Invalid account status.",
                "danger"
            )

            return redirect(url_for("owner.profile"))

        # ------------------------------------------------------
        # Update owner profile
        # ------------------------------------------------------

        OwnerModel.update_owner_profile(
            owner_id,
            full_name,
            email,
            phone,
            status
        )

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(url_for("owner.profile"))

    # ==========================================================
    # LOAD OWNER PROFILE
    # ==========================================================

    owner = OwnerModel.get_owner_profile(owner_id)

    if not owner:

        flash(
            "Owner profile not found.",
            "danger"
        )

        return redirect(url_for("owner.dashboard"))

    # ==========================================================
    # RENDER PROFILE PAGE
    # ==========================================================

    return render_template(
        "owner/profile.html",
        owner=owner
    )
    
    # ==========================================
# Change Owner Profile Picture
# ==========================================

@owner.route("/profile/upload-picture", methods=["POST"])
def upload_profile_picture():

    # Check whether the logged-in user is an owner
    check = owner_required()

    if check:
        return check

    # Get logged-in owner ID
    owner_id = session["user_id"]

    # Get uploaded image
    image = request.files.get("profile_picture")

    if not image or image.filename == "":

        flash(
            "Please select an image.",
            "danger"
        )

        return redirect(url_for("owner.profile"))

    # ==========================================
    # Allowed extensions
    # ==========================================

    allowed_extensions = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp"
    }

    original_name = image.filename

    if "." not in original_name:

        flash(
            "Invalid image file.",
            "danger"
        )

        return redirect(url_for("owner.profile"))

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    if extension not in allowed_extensions:

        flash(
            "Only PNG, JPG, JPEG, GIF and WEBP images are allowed.",
            "danger"
        )

        return redirect(url_for("owner.profile"))

    # ==========================================
    # Upload folder
    # ==========================================

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

    # ==========================================
    # Get old profile picture
    # ==========================================

    old_owner = OwnerModel.get_owner_profile(owner_id)

    old_picture = None

    if old_owner:
        old_picture = old_owner.get("profile_picture")

    # ==========================================
    # Generate new filename
    # ==========================================

    filename = secure_filename(
        f"owner_{owner_id}.{extension}"
    )

    file_path = os.path.join(
        upload_folder,
        filename
    )

    # ==========================================
    # Delete old picture if extension changed
    # ==========================================

    if old_picture and old_picture != filename:

        old_path = os.path.join(
            upload_folder,
            old_picture
        )

        if os.path.exists(old_path):

            os.remove(old_path)

    # ==========================================
    # Save new image
    # ==========================================

    image.save(file_path)

    # ==========================================
    # Update database
    # ==========================================

    OwnerModel.update_owner_profile_picture(
        owner_id,
        filename
    )

    flash(
        "Profile picture updated successfully.",
        "success"
    )

    return redirect(
        url_for("owner.profile")
    )

# ==========================================
# Change Owner Profile Picture
# ==========================================

# @owner.route("/profile/upload-picture", methods=["POST"])
# def upload_profile_picture():

#     check = owner_required()

#     if check:
#         return check

#     owner_id = session["user_id"]

#     image = request.files.get("profile_picture")

#     if not image or image.filename == "":

#         flash(
#             "Please select an image.",
#             "danger"
#         )

#         return redirect(url_for("owner.profile"))

#     # Allowed image extensions
#     allowed_extensions = {
#         "png",
#         "jpg",
#         "jpeg",
#         "gif",
#         "webp"
#     }

#     original_name = image.filename

#     extension = (
#         original_name.rsplit(".", 1)[1].lower()
#         if "." in original_name
#         else ""
#     )

#     if extension not in allowed_extensions:

#         flash(
#             "Only PNG, JPG, JPEG, GIF and WEBP images are allowed.",
#             "danger"
#         )

#         return redirect(url_for("owner.profile"))

#     filename = secure_filename(
#         f"owner_{owner_id}.{extension}"
#     )

#     upload_folder = os.path.join(
#         current_app.root_path,
#         "static",
#         "uploads",
#         "profiles"
#     )

#     os.makedirs(
#         upload_folder,
#         exist_ok=True
#     )

#     image.save(
#         os.path.join(
#             upload_folder,
#             filename
#         )
#     )

#     OwnerModel.update_owner_profile_picture(
#         owner_id,
#         filename
#     )

#     flash(
#         "Profile picture updated successfully.",
#         "success"
#     )

#     return redirect(
#         url_for("owner.profile")
#     )
       


# ==========================================
# Settings
# ==========================================

@owner.route("/settings")
def settings():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    owner_data = OwnerModel.get_owner_profile(owner_id)

    if not owner_data:

        flash(
            "Owner profile not found.",
            "danger"
        )

        return redirect(
            url_for("owner.dashboard")
        )

    return render_template(
        "owner/settings.html",
        owner=owner_data
    )


# ==========================================
# Change Password
# ==========================================

@owner.route(
    "/change-password",
    methods=["POST"]
)
def change_password():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    # ------------------------------------------
    # Get form data
    # ------------------------------------------

    current_password = request.form.get(
        "current_password",
        ""
    ).strip()

    new_password = request.form.get(
        "new_password",
        ""
    ).strip()

    confirm_password = request.form.get(
        "confirm_password",
        ""
    ).strip()


    # ------------------------------------------
    # Required fields
    # ------------------------------------------

    if not current_password or not new_password or not confirm_password:

        flash(
            "All password fields are required.",
            "danger"
        )

        return redirect(
            url_for("owner.settings")
        )


    # ------------------------------------------
    # Password match
    # ------------------------------------------

    if new_password != confirm_password:

        flash(
            "New passwords do not match.",
            "danger"
        )

        return redirect(
            url_for("owner.settings")
        )


    # ------------------------------------------
    # Password length
    # ------------------------------------------

    if len(new_password) < 6:

        flash(
            "New password must contain at least 6 characters.",
            "danger"
        )

        return redirect(
            url_for("owner.settings")
        )


    # ------------------------------------------
    # Prevent same password
    # ------------------------------------------

    if current_password == new_password:

        flash(
            "New password must be different from current password.",
            "danger"
        )

        return redirect(
            url_for("owner.settings")
        )


    # ------------------------------------------
    # Change password
    # ------------------------------------------

    success, message = OwnerModel.change_password(
        owner_id,
        current_password,
        new_password
    )


    if success:

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "danger"
        )


    return redirect(
        url_for("owner.settings")
    )
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