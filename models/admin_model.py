from database.db import mysql


class AdminModel:

    @staticmethod
    def get_dashboard_statistics():

        cursor = mysql.connection.cursor()

        # Total Users
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        # Total Customers
        cursor.execute("SELECT COUNT(*) AS customers FROM users WHERE role='customer'")
        customers = cursor.fetchone()["customers"]

        # Total Owners
        cursor.execute("SELECT COUNT(*) AS owners FROM users WHERE role='owner'")
        owners = cursor.fetchone()["owners"]

        # Total Admins
        cursor.execute("SELECT COUNT(*) AS admins FROM users WHERE role='admin'")
        admins = cursor.fetchone()["admins"]

        # Total Vehicles
        try:
            cursor.execute("SELECT COUNT(*) AS total_vehicles FROM vehicles")
            total_vehicles = cursor.fetchone()["total_vehicles"]
        except:
            total_vehicles = 0

        # Available Vehicles
        try:
            cursor.execute("SELECT COUNT(*) AS available FROM vehicles WHERE status='available'")
            available = cursor.fetchone()["available"]
        except:
            available = 0

        # Booked Vehicles
        try:
            cursor.execute("SELECT COUNT(*) AS booked FROM vehicles WHERE status='booked'")
            booked = cursor.fetchone()["booked"]
        except:
            booked = 0

        # Pending Vehicle Requests
        try:
            cursor.execute("""
                SELECT COUNT(*) AS pending_vehicle
                FROM vehicles
                WHERE approval_status='pending'
            """)
            pending_vehicle = cursor.fetchone()["pending_vehicle"]
        except:
            pending_vehicle = 0

        # Total Bookings
        try:
            cursor.execute("SELECT COUNT(*) AS total_bookings FROM bookings")
            total_bookings = cursor.fetchone()["total_bookings"]
        except:
            total_bookings = 0

        # Pending Bookings
        try:
            cursor.execute("""
                SELECT COUNT(*) AS pending_booking
                FROM bookings
                WHERE booking_status='pending'
            """)
            pending_booking = cursor.fetchone()["pending_booking"]
        except:
            pending_booking = 0

        # Total Revenue
        try:
            cursor.execute("""
                SELECT IFNULL(SUM(amount),0) AS revenue
                FROM payments
                WHERE payment_status='completed'
            """)
            revenue = cursor.fetchone()["revenue"]
        except:
            revenue = 0

        cursor.close()

        return {

            "total_users": total_users,

            "customers": customers,

            "owners": owners,

            "admins": admins,

            "total_vehicles": total_vehicles,

            "available": available,

            "booked": booked,

            "pending_vehicle": pending_vehicle,

            "total_bookings": total_bookings,

            "pending_booking": pending_booking,

            "revenue": revenue

        }


    @staticmethod
    def recent_users(limit=5):

        cursor = mysql.connection.cursor()

        cursor.execute("""

            SELECT
                full_name,
                email,
                role,
                created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT %s

        """, (limit,))

        users = cursor.fetchall()

        cursor.close()

        return users


    @staticmethod
    def recent_bookings(limit=5):

        cursor = mysql.connection.cursor()

        try:

            cursor.execute("""

                SELECT *

                FROM bookings

                ORDER BY booking_date DESC

                LIMIT %s

            """, (limit,))

            bookings = cursor.fetchall()

        except:

            bookings = []

        cursor.close()

        return bookings


    @staticmethod
    def recent_vehicles(limit=5):

        cursor = mysql.connection.cursor()

        try:

            cursor.execute("""

                SELECT *

                FROM vehicles

                ORDER BY created_at DESC

                LIMIT %s

            """, (limit,))

            vehicles = cursor.fetchall()

        except:

            vehicles = []

        cursor.close()

        return vehicles
#  
    @staticmethod
    def get_pending_vehicles():

        cursor = mysql.connection.cursor()

        query = """
        SELECT
            v.*,
            u.full_name
        FROM vehicles v
        JOIN users u
        ON v.owner_id = u.user_id
        WHERE LOWER(v.approval_status)='pending'
        """

        cursor.execute(query)

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    @staticmethod
    def approve_vehicle(vehicle_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE vehicles
            SET approval_status = 'Approved'
            WHERE vehicle_id = %s
        """, (vehicle_id,))

        mysql.connection.commit()

        cursor.close()


    @staticmethod
    def reject_vehicle(vehicle_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE vehicles
            SET approval_status = 'Rejected'
            WHERE vehicle_id = %s
        """, (vehicle_id,))

        mysql.connection.commit()

        cursor.close()
    
    @staticmethod
    def get_vehicle_details(vehicle_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
        SELECT
            v.vehicle_name,
            u.full_name
        FROM vehicles v
        JOIN users u
            ON v.owner_id = u.user_id
        WHERE v.vehicle_id = %s
        """, (vehicle_id,))

        vehicle = cursor.fetchone()

        cursor.close()

        return vehicle
    @staticmethod
    def get_all_bookings():

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                b.*,
                u.full_name AS customer_name,
                v.vehicle_name
            FROM bookings b
            JOIN users u
                ON b.customer_id = u.user_id
            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id
            ORDER BY b.booking_id DESC
        """)

        bookings = cursor.fetchall()

        cursor.close()

        return bookings