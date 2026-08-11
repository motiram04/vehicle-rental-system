from flask import flash
from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from flask import request
import os
import uuid
from werkzeug.utils import secure_filename

from database.db import mysql

from models.admin_model import AdminModel

admin = Blueprint("admin", __name__)
# --------------------------------------------
# Helper Function
# --------------------------------------------
# @admin.route("/admin/dashboard")
def admin_required():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return "Access Denied", 403

    return None



# --------------------------------------------
# Dashboard
# --------------------------------------------

@admin.route("/admin/dashboard")
def dashboard():

    check = admin_required()

    if check:
        return check

    stats = AdminModel.get_dashboard_statistics()

    booking_stats = AdminModel.get_booking_statistics()

    vehicle_stats = AdminModel.get_vehicle_statistics()

    recent_users = AdminModel.recent_users()

    recent_bookings = AdminModel.recent_bookings()

    recent_vehicles = AdminModel.recent_vehicles()

    return render_template(

        "admin/dashboard.html",

        total_users=stats["total_users"],
        customers=stats["customers"],
        owners=stats["owners"],
        admins=stats["admins"],

        total_vehicles=stats["total_vehicles"],
        available=stats["available"],
        booked=stats["booked"],

        pending_vehicle=stats["pending_vehicle"],

        total_bookings=stats["total_bookings"],
        pending_booking=stats["pending_booking"],

        revenue=stats["revenue"],

        booking_stats=booking_stats,
        vehicle_stats=vehicle_stats,

        recent_users=recent_users,
        recent_bookings=recent_bookings,
        recent_vehicles=recent_vehicles

    )
    
    # ==========================================================
# ADMIN PROFILE
# ==========================================================

@admin.route("/admin/profile")
def profile():

    check = admin_required()

    if check:
        return check

    user_id = session.get("user_id")

    admin_user = AdminModel.get_admin_profile(user_id)

    if not admin_user:

        flash("Admin profile not found.", "danger")

        return redirect(url_for("admin.dashboard"))

    return render_template(
        "admin/profile.html",
        admin=admin_user
    )
    
    
@admin.route("/admin/profile/upload-picture", methods=["POST"])
def upload_profile_picture():

    check = admin_required()

    if check:
        return check

    user_id = session.get("user_id")

    if "profile_picture" not in request.files:
        flash("No image selected.", "danger")
        return redirect(url_for("admin.profile"))

    file = request.files["profile_picture"]

    if file.filename == "":
        flash("Please select an image.", "danger")
        return redirect(url_for("admin.profile"))

    allowed_extensions = {"png", "jpg", "jpeg", "webp"}

    original_filename = secure_filename(file.filename)

    extension = original_filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_extensions:
        flash(
            "Only JPG, JPEG, PNG and WEBP images are allowed.",
            "danger"
        )
        return redirect(url_for("admin.profile"))

    # Absolute upload path
    upload_folder = os.path.join(
        admin.root_path,
        "..",
        "static",
        "uploads",
        "profile"
    )

    upload_folder = os.path.abspath(upload_folder)

    os.makedirs(upload_folder, exist_ok=True)

    # Unique filename
    new_filename = f"{uuid.uuid4().hex}.{extension}"

    file_path = os.path.join(
        upload_folder,
        new_filename
    )

    # Save image
    file.save(file_path)

    # Verify file actually exists
    if not os.path.exists(file_path):

        flash(
            "Image could not be saved.",
            "danger"
        )

        return redirect(url_for("admin.profile"))

    # Update database
    AdminModel.update_profile_picture(
        user_id,
        new_filename
    )

    flash(
        "Profile picture updated successfully.",
        "success"
    )

    return redirect(url_for("admin.profile"))

@admin.route("/admin/profile/remove-picture", methods=["POST"])
def remove_profile_picture():

    check = admin_required()

    if check:
        return check

    user_id = session.get("user_id")

    AdminModel.remove_profile_picture(user_id)

    flash(
        "Profile picture removed successfully.",
        "success"
    )

    return redirect(url_for("admin.profile"))
    
    # --------------------------------------------
# User Management
# --------------------------------------------
@admin.route("/admin/users")
def users():

    check = admin_required()

    if check:
        return check

    search = request.args.get("search", "").strip()
    role = request.args.get("role", "").strip()

    stats = AdminModel.get_user_statistics()

    if search or role:
        users = AdminModel.search_users(search, role)
    else:
        users = AdminModel.get_all_users()

    return render_template(
        "admin/users.html",
        users=users,
        search=search,
        role=role,
        stats=stats
    )
    
@admin.route("/admin/user/<int:user_id>")
def view_user(user_id):

    check = admin_required()

    if check:
        return check

    user = AdminModel.get_user_by_id(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))

    return render_template(
        "admin/user_details.html",
        user=user
    )

# Edit User

@admin.route("/admin/user/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):

    check = admin_required()

    if check:
        return check

    user = AdminModel.get_user_by_id(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        role = request.form["role"]

        AdminModel.update_user(
            user_id,
            full_name,
            email,
            phone,
            role
        )

        flash("User updated successfully.", "success")

        return redirect(url_for("admin.users"))

    return render_template(
        "admin/edit_user.html",
        user=user
    )
    
# Deactivate User

@admin.route("/admin/user/deactivate/<int:user_id>")
def deactivate_user(user_id):

    check = admin_required()

    if check:
        return check

    AdminModel.deactivate_user(user_id)

    flash("User deactivated successfully.", "success")

    return redirect(url_for("admin.users"))
# Activate User
@admin.route("/admin/activate_user/<int:user_id>")
def activate_user(user_id):

    check = admin_required()

    if check:
        return check

    AdminModel.activate_user(user_id)

    flash("✅ User activated successfully.", "success")

    return redirect(url_for("admin.users"))
# --------------------------------------------
# Vehicle Management
# --------------------------------------------

@admin.route("/admin/vehicles")
def vehicles():

    check = admin_required()

    if check:
        return check

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    availability = request.args.get("availability", "").strip()
    approval = request.args.get("approval", "").strip()

    stats = AdminModel.get_vehicle_statistics()
    vehicles = AdminModel.get_all_vehicles()

    if search or category or availability or approval:

        vehicles = AdminModel.search_vehicles(
            search,
            category,
            availability,
            approval
        )

    else:

        vehicles = AdminModel.get_all_vehicles()

    # Get categories for filter dropdown
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT category_id, category_name
        FROM vehicle_categories
        ORDER BY category_name ASC
    """)

    categories = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin/vehicles.html",
        vehicles=vehicles,
        stats=stats,
        categories=categories,
        search=search,
        category=category,
        availability=availability,
        approval=approval
    )
    
@admin.route("/admin/vehicle/<int:vehicle_id>")
def view_vehicle(vehicle_id):

    check = admin_required()

    if check:
        return check

    vehicle = AdminModel.get_vehicle_by_id(vehicle_id)

    if not vehicle:

        flash("Vehicle not found.", "danger")

        return redirect(url_for("admin.vehicles"))

    return render_template(
        "admin/vehicle_details.html",
        vehicle=vehicle
    )


# ==========================================
# Booking Management
# ==========================================

# ==========================================
# Booking Management
# ==========================================

@admin.route("/admin/bookings")
def bookings():

    check = admin_required()

    if check:
        return check

    search = request.args.get(
        "search",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    stats = AdminModel.get_booking_statistics()

    if search or status:

        bookings = AdminModel.search_bookings(
            search,
            status
        )

    else:

        bookings = AdminModel.get_all_bookings()

    return render_template(
        "admin/bookings.html",
        bookings=bookings,
        stats=stats,
        search=search,
        status=status
    )


# ==========================================
# Approve Booking
# ==========================================

@admin.route(
    "/admin/booking/approve/<int:booking_id>",
    methods=["POST"]
)
def approve_booking(booking_id):

    check = admin_required()

    if check:
        return check

    success, message = AdminModel.approve_booking(
        booking_id
    )

    flash(
        message,
        "success" if success else "danger"
    )

    return redirect(
        url_for("admin.bookings")
    )


# ==========================================
# Reject Booking
# ==========================================

@admin.route(
    "/admin/booking/reject/<int:booking_id>",
    methods=["POST"]
)
def reject_booking(booking_id):

    check = admin_required()

    if check:
        return check

    success, message = AdminModel.reject_booking(
        booking_id
    )

    flash(
        message,
        "success" if success else "danger"
    )

    return redirect(
        url_for("admin.bookings")
    )


# ==========================================================
# PAYMENT MANAGEMENT
# ==========================================================

@admin.route("/admin/payments")
def payments():

    check = admin_required()

    if check:
        return check

    search = request.args.get(
        "search",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()


    stats = AdminModel.get_payment_statistics()


    if search or status:

        payments = AdminModel.search_payments(
            search,
            status
        )

    else:

        payments = AdminModel.get_all_payments()


    return render_template(
        "admin/payments.html",
        payments=payments,
        stats=stats,
        search=search,
        status=status
    )


# ==========================================================
# UPDATE PAYMENT STATUS
# ==========================================================

@admin.route(
    "/admin/payments/status/<int:payment_id>",
    methods=["POST"]
)
def update_payment_status(payment_id):

    check = admin_required()

    if check:
        return check


    new_status = request.form.get(
        "payment_status",
        ""
    ).strip()


    allowed_statuses = {
        "Pending",
        "Paid",
        "Failed",
        "Completed"
    }


    if new_status not in allowed_statuses:

        flash(
            "Invalid payment status.",
            "danger"
        )

        return redirect(
            url_for("admin.payments")
        )


    success = AdminModel.update_payment_status(
        payment_id,
        new_status
    )


    if success:

        flash(
            f"Payment status changed to {new_status}.",
            "success"
        )

    else:

        flash(
            "Payment not found.",
            "danger"
        )


    return redirect(
        url_for("admin.payments")
    )


# ==========================================================
# REPORTS
# ==========================================================

@admin.route("/admin/reports")
def reports():

    check = admin_required()

    if check:
        return check

    # ------------------------------------------------------
    # Date filters
    # ------------------------------------------------------

    start_date = request.args.get(
        "start_date",
        ""
    ).strip()

    end_date = request.args.get(
        "end_date",
        ""
    ).strip()

    # ------------------------------------------------------
    # Report statistics
    # ------------------------------------------------------

    stats = AdminModel.get_report_statistics(
        start_date,
        end_date
    )

    # ------------------------------------------------------
    # Booking report
    # ------------------------------------------------------

    booking_report = AdminModel.get_booking_report(
        start_date,
        end_date
    )

    # ------------------------------------------------------
    # Payment report
    # ------------------------------------------------------

    payment_report = AdminModel.get_payment_report(
        start_date,
        end_date
    )

    # ------------------------------------------------------
    # Vehicle report
    # ------------------------------------------------------

    vehicle_report = AdminModel.get_vehicle_report()

    # ------------------------------------------------------
    # Customer report
    # ------------------------------------------------------

    customer_report = AdminModel.get_customer_report()

    return render_template(
        "admin/reports.html",

        stats=stats,

        booking_report=booking_report,

        payment_report=payment_report,

        vehicle_report=vehicle_report,

        customer_report=customer_report,

        start_date=start_date,

        end_date=end_date
    )

# --------------------------------------------
# Settings
# --------------------------------------------

@admin.route("/settings")
def settings():

    check = admin_required()

    if check:
        return check

    return render_template("admin/settings.html")


# pending vehicles

@admin.route("/pending_vehicles")
def pending_vehicles():

    check = admin_required()

    if check:
        return check

    vehicles = AdminModel.get_pending_vehicles()

    return render_template(
        "admin/pending_vehicles.html",
        vehicles=vehicles
    )

@admin.route("/approve_vehicle/<int:vehicle_id>")
def approve_vehicle(vehicle_id):

    check = admin_required()

    if check:
        return check

    vehicle = AdminModel.get_vehicle_details(vehicle_id)

    AdminModel.approve_vehicle(vehicle_id)

    flash(
        f"✅ You approved '{vehicle['vehicle_name']}' submitted by {vehicle['full_name']}.",
        "success"
    )

    return redirect(url_for("admin.pending_vehicles"))

@admin.route("/reject_vehicle/<int:vehicle_id>")
def reject_vehicle(vehicle_id):

    check = admin_required()

    if check:
        return check

    vehicle = AdminModel.get_vehicle_details(vehicle_id)

    AdminModel.reject_vehicle(vehicle_id)

    flash(
        f"❌ You rejected '{vehicle['vehicle_name']}' submitted by {vehicle['full_name']}.",
        "warning"
    )

    return redirect(url_for("admin.pending_vehicles"))


# Vehicle Activation/Deactivation
@admin.route("/admin/vehicle/deactivate/<int:vehicle_id>")
def deactivate_vehicle(vehicle_id):

    check = admin_required()

    if check:
        return check

    AdminModel.deactivate_vehicle(vehicle_id)

    flash("Vehicle deactivated successfully.", "success")

    return redirect(url_for("admin.vehicles"))

@admin.route("/admin/vehicle/activate/<int:vehicle_id>")
def activate_vehicle(vehicle_id):

    check = admin_required()

    if check:
        return check

    AdminModel.activate_vehicle(vehicle_id)

    flash("Vehicle activated successfully.", "success")

    return redirect(url_for("admin.vehicles"))

