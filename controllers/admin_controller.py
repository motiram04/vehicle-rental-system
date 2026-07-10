from flask import flash
from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for

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

        recent_users=recent_users,
        recent_bookings=recent_bookings,
        recent_vehicles=recent_vehicles

    )


# --------------------------------------------
# User Management
# --------------------------------------------

@admin.route("/users")
def users():

    check = admin_required()

    if check:
        return check

    return render_template("admin/users.html")


# --------------------------------------------
# Vehicle Management
# --------------------------------------------

@admin.route("/vehicles")
def vehicles():

    check = admin_required()

    if check:
        return check

    return render_template("admin/vehicles.html")



# ==========================================
# Booking Management
# ==========================================

@admin.route("/admin/bookings")
def bookings():

    check = admin_required()

    if check:
        return check

    bookings = AdminModel.get_all_bookings()

    return render_template(
        "admin/bookings.html",
        bookings=bookings
    )


# --------------------------------------------
# Payment Management
# --------------------------------------------

@admin.route("/payments")
def payments():

    check = admin_required()

    if check:
        return check

    return render_template("admin/payments.html")


# --------------------------------------------
# Reports
# --------------------------------------------

@admin.route("/reports")
def reports():

    check = admin_required()

    if check:
        return check

    return render_template("admin/reports.html")


# --------------------------------------------
# Settings
# --------------------------------------------

@admin.route("/settings")
def settings():

    check = admin_required()

    if check:
        return check

    return render_template("admin/settings.html")

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