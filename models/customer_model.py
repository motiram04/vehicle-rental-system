from database.db import mysql
from datetime import datetime


class CustomerModel:

    # =========================================================
    # GET ALL APPROVED & AVAILABLE VEHICLES
    # =========================================================

    @staticmethod
    def get_all_vehicles():

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                v.vehicle_id,
                v.vehicle_name,
                v.model,
                v.vehicle_number,
                v.rent_per_day,
                v.image,
                v.description,
                v.availability_status,
                v.approval_status,
                vc.category_id,
                vc.category_name,
                u.user_id AS owner_id,
                u.full_name AS owner_name

            FROM vehicles v

            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            INNER JOIN users u
                ON v.owner_id = u.user_id

            WHERE
                LOWER(v.approval_status) = 'approved'
                AND LOWER(v.availability_status) = 'available'

            ORDER BY v.register_at DESC
        """

        cursor.execute(query)

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # =========================================================
    # GET SINGLE VEHICLE DETAILS
    # =========================================================

    @staticmethod
    def get_vehicle_by_id(vehicle_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                v.*,

                vc.category_id,
                vc.category_name,

                u.user_id AS owner_id,
                u.full_name AS owner_name,
                u.email AS owner_email,
                u.phone AS owner_phone

            FROM vehicles v

            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            INNER JOIN users u
                ON v.owner_id = u.user_id

            WHERE v.vehicle_id = %s
        """

        cursor.execute(query, (vehicle_id,))

        vehicle = cursor.fetchone()

        cursor.close()

        return vehicle


    # =========================================================
    # SEARCH VEHICLES
    # =========================================================

    @staticmethod
    def search_vehicle(search):

        cursor = mysql.connection.cursor()

        keyword = "%" + search.strip() + "%"

        query = """
            SELECT
                v.vehicle_id,
                v.vehicle_name,
                v.model,
                v.vehicle_number,
                v.rent_per_day,
                v.image,
                v.description,
                v.availability_status,
                v.approval_status,

                vc.category_id,
                vc.category_name,

                u.user_id AS owner_id,
                u.full_name AS owner_name

            FROM vehicles v

            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            INNER JOIN users u
                ON v.owner_id = u.user_id

            WHERE

                LOWER(v.approval_status) = 'approved'

                AND

                LOWER(v.availability_status) = 'available'

                AND

                (
                    v.vehicle_name LIKE %s
                    OR v.model LIKE %s
                    OR v.vehicle_number LIKE %s
                    OR vc.category_name LIKE %s
                    OR u.full_name LIKE %s
                )

            ORDER BY v.register_at DESC
        """

        cursor.execute(
            query,
            (
                keyword,
                keyword,
                keyword,
                keyword,
                keyword
            )
        )

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # =========================================================
    # FILTER BY CATEGORY
    # =========================================================

    @staticmethod
    def filter_category(category_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                v.vehicle_id,
                v.vehicle_name,
                v.model,
                v.vehicle_number,
                v.rent_per_day,
                v.image,
                v.description,
                v.availability_status,
                v.approval_status,

                vc.category_id,
                vc.category_name,

                u.user_id AS owner_id,
                u.full_name AS owner_name

            FROM vehicles v

            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            INNER JOIN users u
                ON v.owner_id = u.user_id

            WHERE

                LOWER(v.approval_status) = 'approved'

                AND

                LOWER(v.availability_status) = 'available'

                AND

                v.category_id = %s

            ORDER BY v.register_at DESC
        """

        cursor.execute(
            query,
            (category_id,)
        )

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # =========================================================
    # FILTER BY PRICE
    # =========================================================

    @staticmethod
    def filter_price(max_price):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                v.vehicle_id,
                v.vehicle_name,
                v.model,
                v.vehicle_number,
                v.rent_per_day,
                v.image,
                v.description,
                v.availability_status,
                v.approval_status,

                vc.category_id,
                vc.category_name,

                u.user_id AS owner_id,
                u.full_name AS owner_name

            FROM vehicles v

            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            INNER JOIN users u
                ON v.owner_id = u.user_id

            WHERE

                LOWER(v.approval_status) = 'approved'

                AND

                LOWER(v.availability_status) = 'available'

                AND

                v.rent_per_day <= %s

            ORDER BY v.rent_per_day ASC
        """

        cursor.execute(
            query,
            (max_price,)
        )

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # =========================================================
    # GET CATEGORIES
    # =========================================================

    @staticmethod
    def get_categories():

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                category_id,
                category_name

            FROM vehicle_categories

            ORDER BY category_name ASC
        """)

        categories = cursor.fetchall()

        cursor.close()

        return categories


    # =========================================================
    # BOOK VEHICLE
    # =========================================================

    @staticmethod
    def book_vehicle(
        vehicle_id,
        customer_id,
        pickup_date,
        return_date
    ):

        cursor = mysql.connection.cursor()

        # -----------------------------------------
        # Check vehicle
        # -----------------------------------------

        cursor.execute("""
            SELECT
                rent_per_day

            FROM vehicles

            WHERE
                vehicle_id = %s
                AND LOWER(approval_status) = 'approved'
                AND LOWER(availability_status) = 'available'

        """, (vehicle_id,))

        vehicle = cursor.fetchone()

        if not vehicle:

            cursor.close()

            return False, "Vehicle is not available."


        # -----------------------------------------
        # Validate dates
        # -----------------------------------------

        try:

            pickup = datetime.strptime(
                pickup_date,
                "%Y-%m-%d"
            )

            return_day = datetime.strptime(
                return_date,
                "%Y-%m-%d"
            )

        except (TypeError, ValueError):

            cursor.close()

            return False, "Invalid pickup or return date."


        if pickup < datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ):

            cursor.close()

            return False, "Pickup date cannot be in the past."


        total_days = (
            return_day - pickup
        ).days


        if total_days <= 0:

            cursor.close()

            return False, (
                "Return date must be after pickup date."
            )


        # -----------------------------------------
        # Calculate amount
        # -----------------------------------------

        rent = float(
            vehicle["rent_per_day"]
        )

        total_amount = (
            total_days * rent
        )


        # -----------------------------------------
        # Create booking
        # -----------------------------------------

        cursor.execute("""
            INSERT INTO bookings(

                vehicle_id,
                customer_id,
                booking_date,
                pickup_date,
                return_date,
                total_days,
                total_amount,
                booking_status

            )

            VALUES(

                %s,
                %s,
                CURDATE(),
                %s,
                %s,
                %s,
                %s,
                'Pending'

            )

        """, (
            vehicle_id,
            customer_id,
            pickup_date,
            return_date,
            total_days,
            total_amount
        ))


        mysql.connection.commit()

        cursor.close()

        return True, "Vehicle booked successfully."


    # =========================================================
    # GET CUSTOMER BOOKINGS
    # =========================================================

    @staticmethod
    def get_customer_bookings(customer_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT

                b.*,

                v.vehicle_name,
                v.image,
                v.vehicle_number,

                vc.category_name,

                u.full_name AS owner_name

            FROM bookings b

            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            JOIN users u
                ON v.owner_id = u.user_id

            WHERE
                b.customer_id = %s

            ORDER BY
                b.booking_id DESC

        """, (customer_id,))

        bookings = cursor.fetchall()

        cursor.close()

        return bookings
    
        # =========================================================
    # CANCEL CUSTOMER BOOKING
    # =========================================================

    @staticmethod
    def cancel_booking(booking_id, customer_id):

        cursor = mysql.connection.cursor()

        try:

            # -------------------------------------------------
            # Get booking and verify ownership
            # -------------------------------------------------

            cursor.execute("""
                SELECT
                    b.booking_status,
                    b.vehicle_id,
                    v.vehicle_name
                FROM bookings b

                JOIN vehicles v
                    ON b.vehicle_id = v.vehicle_id

                WHERE
                    b.booking_id = %s
                    AND b.customer_id = %s
            """, (
                booking_id,
                customer_id
            ))

            booking = cursor.fetchone()

            if not booking:

                cursor.close()

                return False, "Booking not found."

            current_status = str(
                booking["booking_status"]
            ).lower()

            # -------------------------------------------------
            # Already cancelled
            # -------------------------------------------------

            if current_status == "cancelled":

                cursor.close()

                return False, "This booking is already cancelled."

            # -------------------------------------------------
            # Completed booking cannot be cancelled
            # -------------------------------------------------

            if current_status == "completed":

                cursor.close()

                return False, "Completed bookings cannot be cancelled."

            # -------------------------------------------------
            # Rejected booking cannot be cancelled
            # -------------------------------------------------

            if current_status == "rejected":

                cursor.close()

                return False, "Rejected bookings cannot be cancelled."

            # -------------------------------------------------
            # Only Pending / Approved can be cancelled
            # -------------------------------------------------

            if current_status not in (
                "pending",
                "approved"
            ):

                cursor.close()

                return False, "This booking cannot be cancelled."

            # -------------------------------------------------
            # Cancel booking
            # -------------------------------------------------

            cursor.execute("""
                UPDATE bookings

                SET booking_status = 'Cancelled'

                WHERE
                    booking_id = %s
                    AND customer_id = %s
            """, (
                booking_id,
                customer_id
            ))

            # -------------------------------------------------
            # If booking was Approved,
            # make vehicle available again
            # -------------------------------------------------

            if current_status == "approved":

                cursor.execute("""
                    UPDATE vehicles

                    SET availability_status = 'Available'

                    WHERE vehicle_id = %s
                """, (
                    booking["vehicle_id"],
                ))

            # -------------------------------------------------
            # Commit
            # -------------------------------------------------

            mysql.connection.commit()

            cursor.close()

            return True, (
                f"Booking for '{booking['vehicle_name']}' "
                f"has been cancelled successfully."
            )

        except Exception as e:

            mysql.connection.rollback()

            cursor.close()

            print("Cancel booking error:", e)

            return False, "Unable to cancel booking."