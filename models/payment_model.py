from database.db import mysql


class PaymentModel:

    # ==========================================================
    # GET BOOKING FOR PAYMENT
    # ==========================================================

    @staticmethod
    def get_booking_for_payment(booking_id, customer_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                b.booking_id,
                b.customer_id,
                b.vehicle_id,
                b.pickup_date,
                b.return_date,
                b.total_days,
                b.total_amount,
                b.booking_status,

                v.vehicle_name,
                v.vehicle_number,
                v.image,

                owner.full_name AS owner_name

            FROM bookings b

            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            INNER JOIN users owner
                ON v.owner_id = owner.user_id

            WHERE b.booking_id = %s
              AND b.customer_id = %s
        """

        cursor.execute(
            query,
            (booking_id, customer_id)
        )

        booking = cursor.fetchone()

        cursor.close()

        return booking


    # ==========================================================
    # GET PAYMENT BY BOOKING
    # ==========================================================

    @staticmethod
    def get_payment_by_booking(booking_id, customer_id=None):

        cursor = mysql.connection.cursor()

        if customer_id is not None:

            query = """
                SELECT
                    p.payment_id,
                    p.booking_id,
                    p.amount,
                    p.payment_method,
                    p.transaction_id,
                    p.payment_status,
                    p.payment_date

                FROM payments p

                INNER JOIN bookings b
                    ON p.booking_id = b.booking_id

                WHERE p.booking_id = %s
                  AND b.customer_id = %s

                ORDER BY p.payment_id DESC
                LIMIT 1
            """

            cursor.execute(
                query,
                (booking_id, customer_id)
            )

        else:

            query = """
                SELECT
                    payment_id,
                    booking_id,
                    amount,
                    payment_method,
                    transaction_id,
                    payment_status,
                    payment_date

                FROM payments

                WHERE booking_id = %s

                ORDER BY payment_id DESC
                LIMIT 1
            """

            cursor.execute(
                query,
                (booking_id,)
            )

        payment = cursor.fetchone()

        cursor.close()

        return payment


    # ==========================================================
    # CREATE / UPDATE PAYMENT
    # ==========================================================

    @staticmethod
    def create_payment(
        booking_id,
        customer_id,
        payment_method,
        transaction_id=""
    ):

        cursor = mysql.connection.cursor()

        # ------------------------------------------------------
        # Verify booking
        # ------------------------------------------------------

        cursor.execute("""
            SELECT
                booking_id,
                customer_id,
                total_amount,
                booking_status

            FROM bookings

            WHERE booking_id = %s
              AND customer_id = %s

            LIMIT 1
        """, (
            booking_id,
            customer_id
        ))

        booking = cursor.fetchone()

        if not booking:

            cursor.close()

            return (
                False,
                "Booking not found."
            )

        booking_status = str(
            booking["booking_status"] or ""
        ).strip().lower()

        if booking_status != "approved":

            cursor.close()

            return (
                False,
                "Payment is allowed only after the booking is approved."
            )


        # ------------------------------------------------------
        # Check existing payment
        # ------------------------------------------------------

        cursor.execute("""
            SELECT
                payment_id,
                payment_status

            FROM payments

            WHERE booking_id = %s

            ORDER BY payment_id DESC

            LIMIT 1
        """, (booking_id,))

        existing_payment = cursor.fetchone()


        # ------------------------------------------------------
        # Prevent duplicate successful payment
        # ------------------------------------------------------

        if existing_payment:

            existing_status = str(
                existing_payment["payment_status"] or ""
            ).strip().lower()

            if existing_status in {
                "paid",
                "completed",
                "successful",
                "success"
            }:

                cursor.close()

                return (
                    False,
                    "This booking has already been paid."
                )


        amount = booking["total_amount"]


        # ======================================================
        # IMPORTANT
        # SUCCESSFUL PAYMENT = Paid
        # ======================================================

        if existing_payment:

            cursor.execute("""
                UPDATE payments

                SET
                    amount = %s,
                    payment_method = %s,
                    transaction_id = %s,
                    payment_status = 'Paid',
                    payment_date = NOW()

                WHERE payment_id = %s
            """, (
                amount,
                payment_method,
                transaction_id or None,
                existing_payment["payment_id"]
            ))

        else:

            cursor.execute("""
                INSERT INTO payments (
                    booking_id,
                    amount,
                    payment_method,
                    transaction_id,
                    payment_status,
                    payment_date
                )

                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    'Paid',
                    NOW()
                )
            """, (
                booking_id,
                amount,
                payment_method,
                transaction_id or None
            ))


        mysql.connection.commit()

        cursor.close()

        return (
            True,
            "Payment completed successfully."
        )


    # ==========================================================
    # CUSTOMER PAYMENTS
    # ==========================================================

    @staticmethod
    def get_customer_payments(customer_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                p.payment_id,
                p.booking_id,
                p.amount,
                p.payment_method,
                p.transaction_id,
                p.payment_status,
                p.payment_date,

                v.vehicle_name,
                v.vehicle_number,

                b.pickup_date,
                b.return_date

            FROM payments p

            INNER JOIN bookings b
                ON p.booking_id = b.booking_id

            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            WHERE b.customer_id = %s

            ORDER BY p.payment_id DESC
        """

        cursor.execute(
            query,
            (customer_id,)
        )

        payments = cursor.fetchall()

        cursor.close()

        return payments


    # ==========================================================
    # SINGLE CUSTOMER PAYMENT
    # ==========================================================

    @staticmethod
    def get_customer_payment(
        payment_id,
        customer_id
    ):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                p.payment_id,
                p.booking_id,
                p.amount,
                p.payment_method,
                p.transaction_id,
                p.payment_status,
                p.payment_date,

                v.vehicle_name,
                v.vehicle_number,

                b.pickup_date,
                b.return_date

            FROM payments p

            INNER JOIN bookings b
                ON p.booking_id = b.booking_id

            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            WHERE p.payment_id = %s
              AND b.customer_id = %s
        """

        cursor.execute(
            query,
            (payment_id, customer_id)
        )

        payment = cursor.fetchone()

        cursor.close()

        return payment