from database.db import mysql
from datetime import datetime




class CustomerModel:

    # ==========================================
    # Get All Approved & Available Vehicles
    # ==========================================

    @staticmethod
    def get_all_vehicles():

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                v.vehicle_id,
                v.vehicle_name,
                v.model,
                v.rent_per_day,
                v.image,
                v.availability_status,
                vc.category_name,
                u.full_name AS owner_name

            FROM vehicles v

            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            INNER JOIN users u
                ON v.owner_id = u.user_id

            WHERE
                v.approval_status = 'Approved'
                AND v.availability_status = 'Available'

            ORDER BY v.register_at DESC
        """

        cursor.execute(query)

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles

    # ==========================================
    # Get Single Vehicle Details
    # ==========================================

    @staticmethod
    def get_vehicle_by_id(vehicle_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                v.*,

                vc.category_name,

                u.full_name,
                u.email,
                u.phone

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

    # ==========================================
    # Search Vehicles
    # ==========================================

    @staticmethod
    def search_vehicle(search):

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                v.*,
                vc.category_name

            FROM vehicles v

            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            WHERE
                v.approval_status='Approved'

            AND
            (
                v.vehicle_name LIKE %s

                OR

                vc.category_name LIKE %s
            )
        """

        keyword = "%" + search + "%"

        cursor.execute(query, (keyword, keyword))

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles

    # ==========================================
    # Filter By Category
    # ==========================================

    @staticmethod
    def filter_category(category_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                v.*,
                vc.category_name

            FROM vehicles v

            INNER JOIN vehicle_categories vc
                ON vc.category_id = v.category_id

            WHERE

                v.approval_status='Approved'

            AND

                vc.category_id=%s
        """

        cursor.execute(query, (category_id,))

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles

    # ==========================================
    # Get Categories
    # ==========================================

    @staticmethod
    def get_categories():

        cursor = mysql.connection.cursor()

        cursor.execute("""

            SELECT *

            FROM vehicle_categories

            ORDER BY category_name

        """)

        categories = cursor.fetchall()

        cursor.close()

        return categories
        # ==========================================
    # Book Vehicle
    # ==========================================


    @staticmethod
    def book_vehicle(vehicle_id, customer_id, pickup_date, return_date):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT rent_per_day
            FROM vehicles
            WHERE vehicle_id=%s
              AND approval_status='Approved'
              AND availability_status='Available'
        """, (vehicle_id,))

        vehicle = cursor.fetchone()

        if not vehicle:
            cursor.close()
            return False, "Vehicle is not available."

        rent = float(vehicle["rent_per_day"])

        pickup = datetime.strptime(pickup_date, "%Y-%m-%d")
        return_day = datetime.strptime(return_date, "%Y-%m-%d")

        total_days = (return_day - pickup).days

        if total_days <= 0:
            cursor.close()
            return False, "Return date must be after pickup date."

        total_amount = total_days * rent

        cursor.execute("""
            INSERT INTO bookings(
                vehicle_id,
                customer_id,
                booking_date,
                pickup_date,
                return_date,
                total_days,
                total_amount
            )
            VALUES(%s,%s,CURDATE(),%s,%s,%s,%s)
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
    # ==========================================
    # Get Customer Bookings
    # ==========================================

    @staticmethod
    def get_customer_bookings(customer_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT

                b.*,

                v.vehicle_name,
                v.image,
                v.vehicle_number,
                vc.category_name

            FROM bookings b

            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            WHERE b.customer_id = %s

            ORDER BY b.booking_id DESC
        """, (customer_id,))

        bookings = cursor.fetchall()

        cursor.close()

        return bookings
    

    # ==========================================
    # Customer Dashboard Statistics
    # ==========================================

   

    @staticmethod
    def get_dashboard_stats(customer_id):

        cursor = mysql.connection.cursor()

        # ------------------------------------------
        # Total Bookings
        # ------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total_bookings
            FROM bookings
            WHERE customer_id = %s
        """, (customer_id,))

        total_bookings = cursor.fetchone()["total_bookings"]


        # ------------------------------------------
        # Pending Bookings
        # ------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS pending_bookings
            FROM bookings
            WHERE customer_id = %s
            AND LOWER(booking_status) = 'pending'
        """, (customer_id,))

        pending_bookings = cursor.fetchone()["pending_bookings"]


        # ------------------------------------------
        # Total Spent
        # ------------------------------------------

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) AS total_spent
            FROM bookings
            WHERE customer_id = %s
            AND LOWER(booking_status)
                IN ('approved', 'completed')
        """, (customer_id,))

        total_spent = cursor.fetchone()["total_spent"]


        # ------------------------------------------
        # Available Vehicles
        # ------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS available_vehicles
            FROM vehicles
            WHERE approval_status = 'Approved'
            AND availability_status = 'Available'
        """)

        available_vehicles = cursor.fetchone()["available_vehicles"]


        cursor.close()


        return {
            "total_bookings": total_bookings,
            "pending_bookings": pending_bookings,
            "total_spent": total_spent,
            "available_vehicles": available_vehicles
        }


    # ==========================================
    # Recent Customer Bookings
    # ==========================================

    @staticmethod
    def get_recent_bookings(customer_id, limit=5):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT

                b.booking_id,
                b.booking_date,
                b.pickup_date,
                b.return_date,
                b.total_days,
                b.total_amount,
                b.booking_status,

                v.vehicle_name,
                v.image,

                vc.category_name

            FROM bookings b

            INNER JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            INNER JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            WHERE b.customer_id = %s

            ORDER BY b.booking_id DESC

            LIMIT %s
        """, (customer_id, limit))

        recent_bookings = cursor.fetchall()

        cursor.close()

        return recent_bookings