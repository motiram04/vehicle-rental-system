from database.db import mysql
from werkzeug.security import generate_password_hash, check_password_hash


class OwnerModel:

    # =====================================================
    # GET VEHICLE CATEGORIES
    # =====================================================

    @staticmethod
    def get_categories():

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM vehicle_categories
            ORDER BY category_name ASC
        """)

        categories = cursor.fetchall()

        cursor.close()

        return categories


    # =====================================================
    # ADD VEHICLE
    # =====================================================

    @staticmethod
    def add_vehicle(data):

        cursor = mysql.connection.cursor()

        query = """
            INSERT INTO vehicles (
                owner_id,
                category_id,
                vehicle_name,
                model,
                vehicle_number,
                rent_per_day,
                description,
                image,
                approval_status,
                availability_status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            data["owner_id"],
            data["category_id"],
            data["vehicle_name"],
            data["model"],
            data["vehicle_number"],
            data["rent_per_day"],
            data["description"],
            data["image"],
            "Pending",
            data["availability_status"]
        )

        cursor.execute(query, values)

        mysql.connection.commit()

        cursor.close()


    # =====================================================
    # GET OWNER VEHICLES
    # =====================================================

    @staticmethod
    def get_owner_vehicles(owner_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                v.*,
                vc.category_name
            FROM vehicles v
            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id
            WHERE v.owner_id = %s
            ORDER BY v.vehicle_id DESC
        """

        cursor.execute(query, (owner_id,))

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # =====================================================
    # DASHBOARD STATISTICS
    # =====================================================

    @staticmethod
    def dashboard_statistics(owner_id):

        cursor = mysql.connection.cursor()

        stats = {}


        # -------------------------------------------------
        # Total Vehicles
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM vehicles
            WHERE owner_id = %s
        """, (owner_id,))

        stats["total_vehicles"] = cursor.fetchone()["total"]


        # -------------------------------------------------
        # Approved Vehicles
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM vehicles
            WHERE owner_id = %s
            AND approval_status = 'Approved'
        """, (owner_id,))

        stats["approved_vehicles"] = cursor.fetchone()["total"]


        # -------------------------------------------------
        # Pending Vehicles
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM vehicles
            WHERE owner_id = %s
            AND approval_status = 'Pending'
        """, (owner_id,))

        stats["pending_vehicles"] = cursor.fetchone()["total"]


        # -------------------------------------------------
        # Rejected Vehicles
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM vehicles
            WHERE owner_id = %s
            AND approval_status = 'Rejected'
        """, (owner_id,))

        stats["rejected_vehicles"] = cursor.fetchone()["total"]


        # -------------------------------------------------
        # Total Bookings
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM bookings b
            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            WHERE v.owner_id = %s
        """, (owner_id,))

        stats["total_bookings"] = cursor.fetchone()["total"]


        # -------------------------------------------------
        # Pending Bookings
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM bookings b
            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            WHERE v.owner_id = %s
            AND b.booking_status = 'Pending'
        """, (owner_id,))

        stats["pending_bookings"] = cursor.fetchone()["total"]


        # -------------------------------------------------
        # Total Earnings
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COALESCE(SUM(b.total_amount), 0) AS total
            FROM bookings b
            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            WHERE v.owner_id = %s
            AND b.booking_status = 'Completed'
        """, (owner_id,))

        earnings = cursor.fetchone()["total"]

        stats["total_earnings"] = earnings or 0


        cursor.close()

        return stats


    # =====================================================
    # RECENT VEHICLES
    # =====================================================

    @staticmethod
    def recent_vehicles(owner_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM vehicles
            WHERE owner_id = %s
            ORDER BY vehicle_id DESC
            LIMIT 5
        """, (owner_id,))

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # =====================================================
    # EARNINGS SUMMARY
    # =====================================================

    @staticmethod
    def get_earnings_summary(owner_id):

        cursor = mysql.connection.cursor()

        summary = {}


        # -------------------------------------------------
        # Total Earnings
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COALESCE(SUM(b.total_amount), 0) AS total_earnings
            FROM bookings b
            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            WHERE v.owner_id = %s
            AND b.booking_status = 'Completed'
        """, (owner_id,))

        result = cursor.fetchone()

        summary["total_earnings"] = (
            result["total_earnings"] or 0
        )


        # -------------------------------------------------
        # Completed Rentals
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total_completed
            FROM bookings b
            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            WHERE v.owner_id = %s
            AND b.booking_status = 'Completed'
        """, (owner_id,))

        summary["total_completed"] = (
            cursor.fetchone()["total_completed"]
        )


        # -------------------------------------------------
        # Total Revenue
        # Approved + Completed
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COALESCE(SUM(b.total_amount), 0) AS total_revenue
            FROM bookings b
            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            WHERE v.owner_id = %s
            AND b.booking_status IN ('Approved', 'Completed')
        """, (owner_id,))

        result = cursor.fetchone()

        summary["total_revenue"] = (
            result["total_revenue"] or 0
        )


        cursor.close()

        return summary


    # =====================================================
    # EARNINGS HISTORY
    # =====================================================

    @staticmethod
    def get_earnings_history(owner_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                b.booking_id,
                b.pickup_date,
                b.return_date,
                b.total_days,
                b.total_amount,
                b.booking_status,

                v.vehicle_name,
                v.vehicle_number,

                u.full_name AS customer_name

            FROM bookings b

            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            INNER JOIN users u
                ON b.customer_id = u.user_id

            WHERE v.owner_id = %s
            AND b.booking_status = 'Completed'

            ORDER BY b.booking_id DESC
        """

        cursor.execute(query, (owner_id,))

        earnings = cursor.fetchall()

        cursor.close()

        return earnings


    # =====================================================
    # GET BOOKING REQUESTS
    # =====================================================

    @staticmethod
    def get_booking_requests(owner_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                b.booking_id,
                b.pickup_date,
                b.return_date,
                b.total_days,
                b.total_amount,
                b.booking_status,

                u.full_name AS customer_name,
                u.email,

                v.vehicle_id,
                v.vehicle_name,
                v.image,
                v.vehicle_number

            FROM bookings b

            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            JOIN users u
                ON b.customer_id = u.user_id

            WHERE v.owner_id = %s

            ORDER BY b.booking_id DESC
        """

        cursor.execute(query, (owner_id,))

        bookings = cursor.fetchall()

        cursor.close()

        return bookings


    # =====================================================
    # APPROVE BOOKING
    # =====================================================

    @staticmethod
    def approve_booking(booking_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                b.vehicle_id,
                v.vehicle_name,
                u.full_name
            FROM bookings b
            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            JOIN users u
                ON b.customer_id = u.user_id
            WHERE b.booking_id = %s
        """, (booking_id,))

        booking = cursor.fetchone()

        if not booking:

            cursor.close()

            return False, "Booking not found."


        cursor.execute("""
            UPDATE bookings
            SET booking_status = 'Approved'
            WHERE booking_id = %s
        """, (booking_id,))


        cursor.execute("""
            UPDATE vehicles
            SET availability_status = 'Booked'
            WHERE vehicle_id = %s
        """, (booking["vehicle_id"],))


        mysql.connection.commit()

        cursor.close()

        return (
            True,
            f"{booking['vehicle_name']} has been approved for {booking['full_name']}."
        )


    # =====================================================
    # REJECT BOOKING
    # =====================================================

    @staticmethod
    def reject_booking(booking_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                v.vehicle_name,
                u.full_name
            FROM bookings b
            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            JOIN users u
                ON b.customer_id = u.user_id
            WHERE b.booking_id = %s
        """, (booking_id,))

        booking = cursor.fetchone()

        if not booking:

            cursor.close()

            return False, "Booking not found."


        cursor.execute("""
            UPDATE bookings
            SET booking_status = 'Rejected'
            WHERE booking_id = %s
        """, (booking_id,))


        mysql.connection.commit()

        cursor.close()

        return (
            True,
            f"{booking['vehicle_name']} booking for {booking['full_name']} has been rejected."
        )


    # =====================================================
    # OWNER PROFILE
    # =====================================================

    @staticmethod
    def get_owner_profile(owner_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                user_id,
                full_name,
                email,
                phone,
                address,
                role,
                status,
                profile_picture,
                created_at
            FROM users
            WHERE user_id = %s
            AND role = 'owner'
        """, (owner_id,))

        owner = cursor.fetchone()

        cursor.close()

        return owner


    # =====================================================
    # UPDATE OWNER PROFILE
    # =====================================================

    @staticmethod
    def update_owner_profile(
        owner_id,
        full_name,
        email,
        phone,
        status
    ):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE users
            SET
                full_name = %s,
                email = %s,
                phone = %s,
                status = %s
            WHERE user_id = %s
            AND role = 'owner'
        """, (
            full_name,
            email,
            phone,
            status,
            owner_id
        ))

        mysql.connection.commit()

        cursor.close()


    # =====================================================
    # UPDATE PROFILE PICTURE
    # =====================================================

    @staticmethod
    def update_owner_profile_picture(
        owner_id,
        profile_picture
    ):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE users
            SET profile_picture = %s
            WHERE user_id = %s
            AND role = 'owner'
        """, (
            profile_picture,
            owner_id
        ))

        mysql.connection.commit()

        cursor.close()


    # =====================================================
    # CHANGE PASSWORD
    # =====================================================

    @staticmethod
    def change_password(
        owner_id,
        current_password,
        new_password
    ):

        cursor = mysql.connection.cursor()

        # Get current hashed password
        cursor.execute("""
            SELECT password
            FROM users
            WHERE user_id = %s
            AND role = 'owner'
        """, (owner_id,))

        user = cursor.fetchone()

        if not user:

            cursor.close()

            return False, "Owner account not found."


        # Verify current password
        if not check_password_hash(
            user["password"],
            current_password
        ):

            cursor.close()

            return False, "Current password is incorrect."


        # Hash new password
        hashed_password = generate_password_hash(
            new_password
        )


        # Update password
        cursor.execute("""
            UPDATE users
            SET password = %s
            WHERE user_id = %s
            AND role = 'owner'
        """, (
            hashed_password,
            owner_id
        ))


        mysql.connection.commit()

        cursor.close()

        return True, "Password changed successfully."
    
    
    # ==========================================================
# GET SINGLE OWNER VEHICLE
# ==========================================================

    @staticmethod
    def get_vehicle_by_id(owner_id, vehicle_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                v.*,
                vc.category_name

            FROM vehicles v

            LEFT JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            WHERE
                v.vehicle_id = %s
                AND v.owner_id = %s

            LIMIT 1
        """

        cursor.execute(
            query,
            (
                vehicle_id,
                owner_id
            )
        )

        vehicle = cursor.fetchone()

        cursor.close()

        return vehicle


    # ==========================================================
    # SEARCH OWNER VEHICLES
    # ==========================================================

    @staticmethod
    def search_owner_vehicles(owner_id, search=""):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                v.*,
                vc.category_name

            FROM vehicles v

            LEFT JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            WHERE
                v.owner_id = %s
        """

        values = [owner_id]

        if search:

            query += """
                AND (
                    v.vehicle_name LIKE %s
                    OR v.model LIKE %s
                    OR v.vehicle_number LIKE %s
                    OR vc.category_name LIKE %s
                )
            """

            keyword = f"%{search}%"

            values.extend([
                keyword,
                keyword,
                keyword,
                keyword
            ])

        query += """
            ORDER BY v.vehicle_id DESC
        """

        cursor.execute(
            query,
            values
        )

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # ==========================================================
    # UPDATE VEHICLE
    # ==========================================================

    @staticmethod
    def update_vehicle(
        owner_id,
        vehicle_id,
        category_id,
        vehicle_name,
        model,
        vehicle_number,
        rent_per_day,
        description,
        availability_status,
        image=None
    ):

        cursor = mysql.connection.cursor()

        # ------------------------------------------------------
        # Verify ownership
        # ------------------------------------------------------

        cursor.execute("""
            SELECT vehicle_id
            FROM vehicles

            WHERE
                vehicle_id = %s
                AND owner_id = %s
        """, (
            vehicle_id,
            owner_id
        ))

        vehicle = cursor.fetchone()

        if not vehicle:

            cursor.close()

            return False, "Vehicle not found."


        # ------------------------------------------------------
        # Update with / without image
        # ------------------------------------------------------

        if image:

            query = """
                UPDATE vehicles

                SET
                    category_id = %s,
                    vehicle_name = %s,
                    model = %s,
                    vehicle_number = %s,
                    rent_per_day = %s,
                    description = %s,
                    availability_status = %s,
                    image = %s

                WHERE
                    vehicle_id = %s
                    AND owner_id = %s
            """

            values = (
                category_id,
                vehicle_name,
                model,
                vehicle_number,
                rent_per_day,
                description,
                availability_status,
                image,
                vehicle_id,
                owner_id
            )

        else:

            query = """
                UPDATE vehicles

                SET
                    category_id = %s,
                    vehicle_name = %s,
                    model = %s,
                    vehicle_number = %s,
                    rent_per_day = %s,
                    description = %s,
                    availability_status = %s

                WHERE
                    vehicle_id = %s
                    AND owner_id = %s
            """

            values = (
                category_id,
                vehicle_name,
                model,
                vehicle_number,
                rent_per_day,
                description,
                availability_status,
                vehicle_id,
                owner_id
            )

        cursor.execute(
            query,
            values
        )

        mysql.connection.commit()

        cursor.close()

        return True, "Vehicle updated successfully."


    # ==========================================================
    # DELETE VEHICLE
    # ==========================================================

    @staticmethod
    def delete_vehicle(
        owner_id,
        vehicle_id
    ):

        cursor = mysql.connection.cursor()

        try:

            # --------------------------------------------------
            # Get vehicle
            # --------------------------------------------------

            cursor.execute("""
                SELECT
                    vehicle_id,
                    vehicle_name,
                    availability_status,
                    image

                FROM vehicles

                WHERE
                    vehicle_id = %s
                    AND owner_id = %s

                LIMIT 1
            """, (
                vehicle_id,
                owner_id
            ))

            vehicle = cursor.fetchone()

            if not vehicle:

                cursor.close()

                return False, "Vehicle not found."


            # --------------------------------------------------
            # Prevent deletion of actively booked vehicle
            # --------------------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total

                FROM bookings

                WHERE
                    vehicle_id = %s

                    AND LOWER(TRIM(booking_status))
                    IN (
                        'pending',
                        'approved'
                    )
            """, (
                vehicle_id,
            ))

            active_booking = cursor.fetchone()["total"]


            if active_booking > 0:

                cursor.close()

                return False, (
                    "This vehicle cannot be deleted because "
                    "it has an active booking."
                )


            # --------------------------------------------------
            # Delete vehicle
            # --------------------------------------------------

            cursor.execute("""
                DELETE FROM vehicles

                WHERE
                    vehicle_id = %s
                    AND owner_id = %s
            """, (
                vehicle_id,
                owner_id
            ))

            mysql.connection.commit()

            cursor.close()

            return True, (
                f"Vehicle '{vehicle['vehicle_name']}' "
                "deleted successfully."
            )


        except Exception as e:

            mysql.connection.rollback()

            cursor.close()

            print(
                "Delete vehicle error:",
                e
            )

            return False, (
                "Unable to delete vehicle."
            )