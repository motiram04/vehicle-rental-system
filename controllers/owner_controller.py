import os
import uuid

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


# ==========================================================
# OWNER BLUEPRINT
# ==========================================================

owner = Blueprint(
    "owner",
    __name__,
    url_prefix="/owner"
)


# ==========================================================
# OWNER LOGIN REQUIRED
# ==========================================================

def owner_required():

    if "user_id" not in session:

        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "owner":

        flash(
            "Access Denied!",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    return None


# ==========================================================
# DASHBOARD
# ==========================================================

@owner.route("/dashboard")
def dashboard():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    owner_data = OwnerModel.get_owner_profile(
        owner_id
    )

    if not owner_data:

        flash(
            "Owner profile not found.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    stats = OwnerModel.dashboard_statistics(
        owner_id
    )

    recent_vehicles = OwnerModel.recent_vehicles(
        owner_id
    )

    all_bookings = OwnerModel.get_booking_requests(
        owner_id
    )

    recent_bookings = all_bookings[:5]

    return render_template(
        "owner/dashboard.html",

        owner=owner_data,

        total_vehicles=stats["total_vehicles"],
        approved_vehicles=stats["approved_vehicles"],
        pending_vehicles=stats["pending_vehicles"],
        rejected_vehicles=stats["rejected_vehicles"],

        total_bookings=stats["total_bookings"],
        pending_bookings=stats["pending_bookings"],

        total_earnings=stats["total_earnings"],

        recent_vehicles=recent_vehicles,
        recent_bookings=recent_bookings
    )


# ==========================================================
# MY VEHICLES
# ==========================================================

@owner.route("/vehicles")
def vehicles():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    search = request.args.get(
        "search",
        ""
    ).strip()

    if search:

        vehicles = OwnerModel.search_owner_vehicles(
            owner_id,
            search
        )

    else:

        vehicles = OwnerModel.get_owner_vehicles(
            owner_id
        )

    return render_template(
        "owner/vehicles.html",
        vehicles=vehicles,
        search=search
    )


# ==========================================================
# ADD VEHICLE
# ==========================================================

@owner.route(
    "/add_vehicle",
    methods=["GET", "POST"]
)
def add_vehicle():

    check = owner_required()

    if check:
        return check

    if request.method == "POST":

        vehicle_name = request.form.get(
            "vehicle_name",
            ""
        ).strip()

        category_id = request.form.get(
            "category_id"
        )

        model = request.form.get(
            "model",
            ""
        ).strip()

        vehicle_number = request.form.get(
            "vehicle_number",
            ""
        ).strip()

        rent_per_day = request.form.get(
            "rent_per_day",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        availability_status = request.form.get(
            "availability_status",
            "Available"
        ).strip()

        image = request.files.get(
            "image"
        )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not vehicle_name:

            flash(
                "Vehicle name is required.",
                "danger"
            )

            return redirect(
                url_for("owner.add_vehicle")
            )

        if not category_id:

            flash(
                "Vehicle category is required.",
                "danger"
            )

            return redirect(
                url_for("owner.add_vehicle")
            )

        try:

            rent = float(rent_per_day)

            if rent <= 0:
                raise ValueError

        except (ValueError, TypeError):

            flash(
                "Please enter a valid rent per day.",
                "danger"
            )

            return redirect(
                url_for("owner.add_vehicle")
            )

        # --------------------------------------------------
        # Image
        # --------------------------------------------------

        filename = "default_vehicle.jpg"

        if image and image.filename:

            original_filename = secure_filename(
                image.filename
            )

            if (
                not original_filename
                or "." not in original_filename
            ):

                flash(
                    "Invalid image file.",
                    "danger"
                )

                return redirect(
                    url_for("owner.add_vehicle")
                )

            extension = (
                original_filename
                .rsplit(".", 1)[1]
                .lower()
            )

            allowed_extensions = {
                "jpg",
                "jpeg",
                "png",
                "webp"
            }

            if extension not in allowed_extensions:

                flash(
                    "Only JPG, JPEG, PNG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for("owner.add_vehicle")
                )

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "vehicles"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            filename = (
                f"vehicle_{session['user_id']}_"
                f"{uuid.uuid4().hex}."
                f"{extension}"
            )

            image.save(
                os.path.join(
                    upload_folder,
                    filename
                )
            )

        # --------------------------------------------------
        # Save vehicle
        # --------------------------------------------------

        data = {

            "owner_id":
                session["user_id"],

            "category_id":
                category_id,

            "vehicle_name":
                vehicle_name,

            "model":
                model,

            "vehicle_number":
                vehicle_number,

            "rent_per_day":
                rent,

            "description":
                description,

            "availability_status":
                availability_status,

            "image":
                filename
        }

        OwnerModel.add_vehicle(
            data
        )

        flash(
            "Vehicle uploaded successfully. "
            "Waiting for admin approval.",
            "success"
        )

        return redirect(
            url_for("owner.vehicles")
        )

    categories = OwnerModel.get_categories()

    return render_template(
        "owner/add_vehicle.html",
        categories=categories
    )


# ==========================================================
# VIEW VEHICLE
# ==========================================================

@owner.route(
    "/vehicle/<int:vehicle_id>"
)
def view_vehicle(vehicle_id):

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    vehicle = OwnerModel.get_vehicle_by_id(
        owner_id,
        vehicle_id
    )

    if not vehicle:

        flash(
            "Vehicle not found.",
            "danger"
        )

        return redirect(
            url_for("owner.vehicles")
        )

    return render_template(
        "owner/vehicle_details.html",
        vehicle=vehicle
    )


# ==========================================================
# EDIT VEHICLE
# ==========================================================

@owner.route(
    "/vehicle/edit/<int:vehicle_id>",
    methods=["GET", "POST"]
)
def edit_vehicle(vehicle_id):

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    vehicle = OwnerModel.get_vehicle_by_id(
        owner_id,
        vehicle_id
    )

    if not vehicle:

        flash(
            "Vehicle not found.",
            "danger"
        )

        return redirect(
            url_for("owner.vehicles")
        )

    categories = OwnerModel.get_categories()

    if request.method == "POST":

        category_id = request.form.get(
            "category_id"
        )

        vehicle_name = request.form.get(
            "vehicle_name",
            ""
        ).strip()

        model = request.form.get(
            "model",
            ""
        ).strip()

        vehicle_number = request.form.get(
            "vehicle_number",
            ""
        ).strip()

        rent_per_day = request.form.get(
            "rent_per_day",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        availability_status = request.form.get(
            "availability_status",
            "Available"
        ).strip()

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not vehicle_name:

            flash(
                "Vehicle name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "owner.edit_vehicle",
                    vehicle_id=vehicle_id
                )
            )

        if not category_id:

            flash(
                "Vehicle category is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "owner.edit_vehicle",
                    vehicle_id=vehicle_id
                )
            )

        try:

            rent = float(
                rent_per_day
            )

            if rent <= 0:
                raise ValueError

        except (ValueError, TypeError):

            flash(
                "Please enter a valid rent per day.",
                "danger"
            )

            return redirect(
                url_for(
                    "owner.edit_vehicle",
                    vehicle_id=vehicle_id
                )
            )

        # --------------------------------------------------
        # Availability validation
        # --------------------------------------------------

        current_status = str(
            vehicle["availability_status"] or ""
        ).strip()

        allowed_statuses = {
            "Available",
            "Maintenance"
        }

        if current_status.lower() == "booked":

            availability_status = "Booked"

        elif availability_status not in allowed_statuses:

            flash(
                "Invalid availability status.",
                "danger"
            )

            return redirect(
                url_for(
                    "owner.edit_vehicle",
                    vehicle_id=vehicle_id
                )
            )

        # --------------------------------------------------
        # Image
        # --------------------------------------------------

        image_file = request.files.get(
            "image"
        )

        image_filename = None

        if image_file and image_file.filename:

            original_filename = secure_filename(
                image_file.filename
            )

            if (
                not original_filename
                or "." not in original_filename
            ):

                flash(
                    "Invalid image file.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "owner.edit_vehicle",
                        vehicle_id=vehicle_id
                    )
                )

            extension = (
                original_filename
                .rsplit(".", 1)[1]
                .lower()
            )

            allowed_extensions = {
                "jpg",
                "jpeg",
                "png",
                "webp"
            }

            if extension not in allowed_extensions:

                flash(
                    "Only JPG, JPEG, PNG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "owner.edit_vehicle",
                        vehicle_id=vehicle_id
                    )
                )

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "vehicles"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            image_filename = (
                f"vehicle_{owner_id}_"
                f"{uuid.uuid4().hex}."
                f"{extension}"
            )

            image_file.save(
                os.path.join(
                    upload_folder,
                    image_filename
                )
            )

        # --------------------------------------------------
        # Update database
        # --------------------------------------------------

        success, message = OwnerModel.update_vehicle(
            owner_id,
            vehicle_id,
            category_id,
            vehicle_name,
            model,
            vehicle_number,
            rent,
            description,
            availability_status,
            image_filename
        )

        flash(
            message,
            "success" if success else "danger"
        )

        if success:

            return redirect(
                url_for("owner.vehicles")
            )

        return redirect(
            url_for(
                "owner.edit_vehicle",
                vehicle_id=vehicle_id
            )
        )

    return render_template(
        "owner/edit_vehicle.html",
        vehicle=vehicle,
        categories=categories
    )


# ==========================================================
# DELETE VEHICLE
# ==========================================================

@owner.route(
    "/vehicle/delete/<int:vehicle_id>",
    methods=["POST"]
)
def delete_vehicle(vehicle_id):

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    success, message = OwnerModel.delete_vehicle(
        owner_id,
        vehicle_id
    )

    flash(
        message,
        "success" if success else "danger"
    )

    return redirect(
        url_for("owner.vehicles")
    )


# ==========================================================
# BOOKINGS
# ==========================================================

@owner.route("/bookings")
def bookings():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    bookings = OwnerModel.get_booking_requests(
        owner_id
    )

    return render_template(
        "owner/bookings.html",
        bookings=bookings
    )


# ==========================================================
# APPROVE BOOKING
# ==========================================================

@owner.route(
    "/approve-booking/<int:booking_id>"
)
def approve_booking(booking_id):

    check = owner_required()

    if check:
        return check

    success, message = OwnerModel.approve_booking(
        booking_id
    )

    flash(
        message,
        "success" if success else "danger"
    )

    return redirect(
        url_for("owner.bookings")
    )


# ==========================================================
# REJECT BOOKING
# ==========================================================

@owner.route(
    "/reject-booking/<int:booking_id>"
)
def reject_booking(booking_id):

    check = owner_required()

    if check:
        return check

    success, message = OwnerModel.reject_booking(
        booking_id
    )

    flash(
        message,
        "warning" if success else "danger"
    )

    return redirect(
        url_for("owner.bookings")
    )


# ==========================================================
# EARNINGS
# ==========================================================

@owner.route("/earnings")
def earnings():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    earnings_summary = (
        OwnerModel.get_earnings_summary(
            owner_id
        )
    )

    earnings_history = (
        OwnerModel.get_earnings_history(
            owner_id
        )
    )

    return render_template(
        "owner/earnings.html",
        summary=earnings_summary,
        earnings=earnings_history
    )


# ==========================================================
# OWNER PROFILE
# ==========================================================

@owner.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

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

        status = request.form.get(
            "status",
            ""
        ).strip()

        if not full_name or not email:

            flash(
                "Full name and email are required.",
                "danger"
            )

            return redirect(
                url_for("owner.profile")
            )

        if status not in [
            "Active",
            "Inactive"
        ]:

            flash(
                "Invalid account status.",
                "danger"
            )

            return redirect(
                url_for("owner.profile")
            )

        OwnerModel.update_owner_profile(
            owner_id,
            full_name,
            email,
            phone,
            status
        )

        session["full_name"] = full_name

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("owner.profile")
        )

    owner_data = OwnerModel.get_owner_profile(
        owner_id
    )

    if not owner_data:

        flash(
            "Owner profile not found.",
            "danger"
        )

        return redirect(
            url_for("owner.dashboard")
        )

    if owner_data.get("profile_picture"):

        session["profile_picture"] = (
            owner_data["profile_picture"]
        )

    return render_template(
        "owner/profile.html",
        owner=owner_data
    )


# ==========================================================
# OWNER PROFILE PICTURE
# ==========================================================

@owner.route(
    "/profile/upload-picture",
    methods=["POST"]
)
def upload_profile_picture():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    image = request.files.get(
        "profile_picture"
    )

    if not image or not image.filename:

        flash(
            "Please select an image.",
            "danger"
        )

        return redirect(
            url_for("owner.profile")
        )

    allowed_extensions = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp"
    }

    original_name = secure_filename(
        image.filename
    )

    if (
        not original_name
        or "." not in original_name
    ):

        flash(
            "Invalid image file.",
            "danger"
        )

        return redirect(
            url_for("owner.profile")
        )

    extension = (
        original_name
        .rsplit(".", 1)[1]
        .lower()
    )

    if extension not in allowed_extensions:

        flash(
            "Only PNG, JPG, JPEG, GIF and WEBP images are allowed.",
            "danger"
        )

        return redirect(
            url_for("owner.profile")
        )

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

    old_owner = OwnerModel.get_owner_profile(
        owner_id
    )

    old_picture = None

    if old_owner:

        old_picture = old_owner.get(
            "profile_picture"
        )

    filename = secure_filename(
        f"owner_{owner_id}.{extension}"
    )

    file_path = os.path.join(
        upload_folder,
        filename
    )

    if old_picture and old_picture != filename:

        old_path = os.path.join(
            upload_folder,
            old_picture
        )

        if os.path.exists(old_path):

            os.remove(old_path)

    image.save(
        file_path
    )

    OwnerModel.update_owner_profile_picture(
        owner_id,
        filename
    )

    session["profile_picture"] = filename

    flash(
        "Profile picture updated successfully.",
        "success"
    )

    return redirect(
        url_for("owner.profile")
    )


# ==========================================================
# SETTINGS
# ==========================================================

@owner.route("/settings")
def settings():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

    owner_data = OwnerModel.get_owner_profile(
        owner_id
    )

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


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@owner.route(
    "/change-password",
    methods=["POST"]
)
def change_password():

    check = owner_required()

    if check:
        return check

    owner_id = session["user_id"]

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

    if (
        not current_password
        or not new_password
        or not confirm_password
    ):

        flash(
            "All password fields are required.",
            "danger"
        )

        return redirect(
            url_for("owner.settings")
        )

    if new_password != confirm_password:

        flash(
            "New passwords do not match.",
            "danger"
        )

        return redirect(
            url_for("owner.settings")
        )

    if len(new_password) < 6:

        flash(
            "New password must contain at least 6 characters.",
            "danger"
        )

        return redirect(
            url_for("owner.settings")
        )

    if current_password == new_password:

        flash(
            "New password must be different from current password.",
            "danger"
        )

        return redirect(
            url_for("owner.settings")
        )

    success, message = OwnerModel.change_password(
        owner_id,
        current_password,
        new_password
    )

    flash(
        message,
        "success" if success else "danger"
    )

    return redirect(
        url_for("owner.settings")
    )