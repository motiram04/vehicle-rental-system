from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from models.payment_model import PaymentModel


payment = Blueprint("payment", __name__)


# ==========================================================
# CUSTOMER AUTHORIZATION
# ==========================================================

def customer_required():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "customer":
        return "Access Denied", 403

    return None


# ==========================================================
# PAYMENT PAGE
# ==========================================================

@payment.route(
    "/customer/payment/<int:booking_id>"
)
def payment_page(booking_id):

    check = customer_required()

    if check:
        return check

    customer_id = session.get("user_id")

    booking = PaymentModel.get_booking_for_payment(
        booking_id,
        customer_id
    )

    if not booking:

        flash(
            "Booking not found or you are not allowed to pay for this booking.",
            "danger"
        )

        return redirect(
            url_for("customer.bookings")
        )


    existing_payment = PaymentModel.get_payment_by_booking(
        booking_id,
        customer_id
    )


    # Already paid
    if existing_payment:

        payment_status = str(
            existing_payment.get(
                "payment_status",
                ""
            )
        ).strip().lower()

        if payment_status in {
            "paid",
            "completed",
            "successful",
            "success"
        }:

            flash(
                "This booking has already been paid.",
                "info"
            )

            return redirect(
                url_for("payment.my_payments")
            )


    return render_template(
        "customer/payment.html",
        booking=booking,
        payment=existing_payment
    )


# ==========================================================
# PROCESS PAYMENT
# ==========================================================

@payment.route(
    "/customer/payment/<int:booking_id>/process",
    methods=["POST"]
)
def process_payment(booking_id):

    check = customer_required()

    if check:
        return check

    customer_id = session.get("user_id")


    payment_method = request.form.get(
        "payment_method",
        ""
    ).strip()


    transaction_id = request.form.get(
        "transaction_id",
        ""
    ).strip()


    allowed_methods = {
        "Cash",
        "eSewa",
        "Khalti"
    }


    if payment_method not in allowed_methods:

        flash(
            "Please select a valid payment method.",
            "danger"
        )

        return redirect(
            url_for(
                "payment.payment_page",
                booking_id=booking_id
            )
        )


    # Online payment requires transaction ID
    if payment_method in {
        "eSewa",
        "Khalti"
    } and not transaction_id:

        flash(
            "Transaction ID is required for eSewa or Khalti.",
            "danger"
        )

        return redirect(
            url_for(
                "payment.payment_page",
                booking_id=booking_id
            )
        )


    success, message = PaymentModel.create_payment(
        booking_id=booking_id,
        customer_id=customer_id,
        payment_method=payment_method,
        transaction_id=transaction_id
    )


    flash(
        message,
        "success" if success else "danger"
    )


    if success:

        return redirect(
            url_for("payment.my_payments")
        )


    return redirect(
        url_for(
            "payment.payment_page",
            booking_id=booking_id
        )
    )


# ==========================================================
# MY PAYMENTS
# ==========================================================

@payment.route("/customer/payments")
def my_payments():

    check = customer_required()

    if check:
        return check

    customer_id = session.get("user_id")

    payments = PaymentModel.get_customer_payments(
        customer_id
    )

    return render_template(
        "customer/payments.html",
        payments=payments
    )