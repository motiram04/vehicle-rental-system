from database.db import mysql


class OwnerModel:

    # ============================================
    # Get All Vehicle Categories
    # ============================================
    @staticmethod
    def get_categories():
        cursor = mysql.connection.cursor()

        query = """
            SELECT *
            FROM vehicle_categories
            ORDER BY category_name ASC
        """

        cursor.execute(query)

        categories = cursor.fetchall()

        cursor.close()

        return categories


    # ============================================
    # Add New Vehicle
    # ============================================
    @staticmethod
    def add_vehicle(data):

        cursor = mysql.connection.cursor()

        query = """
            INSERT INTO vehicles(

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

            VALUES(

                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s

            )
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


    # ============================================
    # Get All Vehicles of Logged-in Owner
    # ============================================
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

        WHERE owner_id=%s

        ORDER BY vehicle_id DESC

        """

        cursor.execute(query, (owner_id,))

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # ============================================
    # Dashboard Statistics
    # ============================================
    @staticmethod
    def dashboard_statistics(owner_id):

        cursor = mysql.connection.cursor()

        stats = {}

        # Total Vehicles
        cursor.execute("""

            SELECT COUNT(*) AS total

            FROM vehicles

            WHERE owner_id=%s

        """, (owner_id,))

        stats["total_vehicles"] = cursor.fetchone()["total"]

        # Approved
        cursor.execute("""

            SELECT COUNT(*) AS total

            FROM vehicles

            WHERE owner_id=%s
            AND approval_status='Approved'

        """, (owner_id,))

        stats["approved_vehicles"] = cursor.fetchone()["total"]

        # Pending
        cursor.execute("""

            SELECT COUNT(*) AS total

            FROM vehicles

            WHERE owner_id=%s
            AND approval_status='Pending'

        """, (owner_id,))

        stats["pending_vehicles"] = cursor.fetchone()["total"]

        # Rejected
        cursor.execute("""

            SELECT COUNT(*) AS total

            FROM vehicles

            WHERE owner_id=%s
            AND approval_status='Rejected'

        """, (owner_id,))

        stats["rejected_vehicles"] = cursor.fetchone()["total"]

        cursor.close()

        return stats


    # ============================================
    # Recent Vehicles
    # ============================================
    @staticmethod
    def recent_vehicles(owner_id):

        cursor = mysql.connection.cursor()

        query = """

        SELECT *

        FROM vehicles

        WHERE owner_id=%s

        ORDER BY vehicle_id DESC

        LIMIT 5

        """

        cursor.execute(query, (owner_id,))

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles
    
    @staticmethod
    def get_categories():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM vehicle_categories ORDER BY category_name ASC")
        categories = cursor.fetchall()
        cursor.close()
        return categories
    
 # =====================================================
# Get Booking Requests
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
    # Approve Booking
    # =====================================================

    @staticmethod
    def approve_booking(booking_id):

        cursor = mysql.connection.cursor()

        # Get booking, vehicle and customer information
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
            WHERE b.booking_id=%s
        """, (booking_id,))

        booking = cursor.fetchone()

        if not booking:
            cursor.close()
            return False, "Booking not found."

        # Approve booking
        cursor.execute("""
            UPDATE bookings
            SET booking_status='Approved'
            WHERE booking_id=%s
        """, (booking_id,))

        # Mark vehicle as booked
        cursor.execute("""
            UPDATE vehicles
            SET availability_status='Booked'
            WHERE vehicle_id=%s
        """, (booking["vehicle_id"],))

        mysql.connection.commit()
        cursor.close()

        return (
            True,
            f"{booking['vehicle_name']} has been approved for {booking['full_name']}."
        )
        
        # =====================================================
    # Reject Booking
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
                ON b.vehicle_id=v.vehicle_id
            JOIN users u
                ON b.customer_id=u.user_id
            WHERE b.booking_id=%s
        """, (booking_id,))

        booking = cursor.fetchone()

        if not booking:
            cursor.close()
            return False, "Booking not found."

        cursor.execute("""
            UPDATE bookings
            SET booking_status='Rejected'
            WHERE booking_id=%s
        """, (booking_id,))

        mysql.connection.commit()
        cursor.close()

        return (
            True,
            f"{booking['vehicle_name']} booking for {booking['full_name']} has been rejected."
        )