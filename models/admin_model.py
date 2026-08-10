from database.db import mysql


class AdminModel:

    # ==========================================================
    # DASHBOARD STATISTICS
    # ==========================================================

    @staticmethod
    def get_dashboard_statistics():

        cursor = mysql.connection.cursor()

        # --------------------------
        # Users
        # --------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total_users
            FROM users
        """)
        total_users = cursor.fetchone()["total_users"]

        cursor.execute("""
            SELECT COUNT(*) AS customers
            FROM users
            WHERE role = 'customer'
        """)
        customers = cursor.fetchone()["customers"]

        cursor.execute("""
            SELECT COUNT(*) AS owners
            FROM users
            WHERE role = 'owner'
        """)
        owners = cursor.fetchone()["owners"]

        cursor.execute("""
            SELECT COUNT(*) AS admins
            FROM users
            WHERE role = 'admin'
        """)
        admins = cursor.fetchone()["admins"]

        # --------------------------
        # Vehicles
        # --------------------------

        try:
            cursor.execute("""
                SELECT COUNT(*) AS total_vehicles
                FROM vehicles
            """)
            total_vehicles = cursor.fetchone()["total_vehicles"]
        except Exception:
            total_vehicles = 0

        try:
            cursor.execute("""
                SELECT COUNT(*) AS available
                FROM vehicles
                WHERE LOWER(availability_status) = 'available'
            """)
            available = cursor.fetchone()["available"]
        except Exception:
            available = 0

        try:
            cursor.execute("""
                SELECT COUNT(*) AS booked
                FROM vehicles
                WHERE LOWER(availability_status) = 'booked'
            """)
            booked = cursor.fetchone()["booked"]
        except Exception:
            booked = 0

        try:
            cursor.execute("""
                SELECT COUNT(*) AS pending_vehicle
                FROM vehicles
                WHERE LOWER(approval_status) = 'pending'
            """)
            pending_vehicle = cursor.fetchone()["pending_vehicle"]
        except Exception:
            pending_vehicle = 0

        # --------------------------
        # Bookings
        # --------------------------

        try:
            cursor.execute("""
                SELECT COUNT(*) AS total_bookings
                FROM bookings
            """)
            total_bookings = cursor.fetchone()["total_bookings"]
        except Exception:
            total_bookings = 0

        try:
            cursor.execute("""
                SELECT COUNT(*) AS pending_booking
                FROM bookings
                WHERE LOWER(booking_status) = 'pending'
            """)
            pending_booking = cursor.fetchone()["pending_booking"]
        except Exception:
            pending_booking = 0

        # --------------------------
        # Revenue
        # --------------------------

        try:
            cursor.execute("""
                SELECT IFNULL(SUM(amount), 0) AS revenue
                FROM payments
                WHERE LOWER(payment_status) = 'completed'
            """)
            revenue = cursor.fetchone()["revenue"]
        except Exception:
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


    # ==========================================================
    # RECENT USERS
    # ==========================================================

    @staticmethod
    def recent_users(limit=5):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                user_id,
                full_name,
                email,
                role,
                status,
                created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))

        users = cursor.fetchall()

        cursor.close()

        return users


    # ==========================================================
    # RECENT BOOKINGS
    # ==========================================================

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

        except Exception:
            bookings = []

        cursor.close()

        return bookings


    # ==========================================================
    # RECENT VEHICLES
    # ==========================================================

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

        except Exception:
            vehicles = []

        cursor.close()

        return vehicles


    # ==========================================================
    # PENDING VEHICLES
    # ==========================================================

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
            WHERE LOWER(v.approval_status) = 'pending'
            ORDER BY v.vehicle_id ASC
        """

        cursor.execute(query)

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # ==========================================================
    # APPROVE VEHICLE
    # ==========================================================

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


    # ==========================================================
    # REJECT VEHICLE
    # ==========================================================

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


    # ==========================================================
    # VEHICLE DETAILS
    # ==========================================================

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


    # ==========================================================
    # ALL BOOKINGS
    # ==========================================================

    @staticmethod
    def get_all_bookings():

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                b.booking_id,
                b.booking_date,
                b.pickup_date,
                b.return_date,
                b.total_days,
                b.total_amount,
                b.booking_status,

                customer.full_name AS customer_name,

                owner.full_name AS owner_name,

                v.vehicle_name,
                v.vehicle_number

            FROM bookings b

            JOIN users customer
                ON b.customer_id = customer.user_id

            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            JOIN users owner
                ON v.owner_id = owner.user_id

            ORDER BY b.booking_id ASC
        """

        cursor.execute(query)

        bookings = cursor.fetchall()

        cursor.close()

        return bookings


    # ==========================================================
    # BOOKING STATISTICS
    # ==========================================================

    @staticmethod
    def get_booking_statistics():

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN LOWER(booking_status) = 'pending'
                        THEN 1
                        ELSE 0
                    END
                ) AS pending,

                SUM(
                    CASE
                        WHEN LOWER(booking_status) = 'approved'
                        THEN 1
                        ELSE 0
                    END
                ) AS approved,

                SUM(
                    CASE
                        WHEN LOWER(booking_status) = 'rejected'
                        THEN 1
                        ELSE 0
                    END
                ) AS rejected,

                SUM(
                    CASE
                        WHEN LOWER(booking_status) = 'completed'
                        THEN 1
                        ELSE 0
                    END
                ) AS completed,

                SUM(
                    CASE
                        WHEN LOWER(booking_status) = 'cancelled'
                        THEN 1
                        ELSE 0
                    END
                ) AS cancelled

            FROM bookings
        """

        cursor.execute(query)

        stats = cursor.fetchone()

        cursor.close()

        return stats


    # ==========================================================
    # SEARCH BOOKINGS
    # ==========================================================

    @staticmethod
    def search_bookings(search="", status=""):

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                b.booking_id,
                b.booking_date,
                b.pickup_date,
                b.return_date,
                b.total_days,
                b.total_amount,
                b.booking_status,

                customer.full_name AS customer_name,

                owner.full_name AS owner_name,

                v.vehicle_name,
                v.vehicle_number

            FROM bookings b

            JOIN users customer
                ON b.customer_id = customer.user_id

            JOIN vehicles v
                ON b.vehicle_id = v.vehicle_id

            JOIN users owner
                ON v.owner_id = owner.user_id

            WHERE
            (
                CAST(b.booking_id AS CHAR) LIKE %s
                OR customer.full_name LIKE %s
                OR owner.full_name LIKE %s
                OR v.vehicle_name LIKE %s
                OR v.vehicle_number LIKE %s
            )
        """

        values = [
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ]

        if status:
            query += """
                AND b.booking_status = %s
            """

            values.append(status)

        query += """
            ORDER BY b.booking_id ASC
        """

        cursor.execute(query, values)

        bookings = cursor.fetchall()

        cursor.close()

        return bookings


    # ==========================================================
    # ALL USERS
    # ==========================================================

    @staticmethod
    def get_all_users():

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                user_id,
                full_name,
                email,
                phone,
                role,
                status,
                created_at

            FROM users

            ORDER BY user_id ASC
        """

        cursor.execute(query)

        users = cursor.fetchall()

        cursor.close()

        return users


    # ==========================================================
    # SEARCH USERS
    # ==========================================================

    @staticmethod
    def search_users(search="", role=""):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                user_id,
                full_name,
                email,
                phone,
                role,
                status,
                created_at

            FROM users

            WHERE
            (
                full_name LIKE %s
                OR email LIKE %s
                OR phone LIKE %s
            )
        """

        values = [
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ]

        if role:

            query += """
                AND role = %s
            """

            values.append(role)

        query += """
            ORDER BY user_id ASC
        """

        cursor.execute(query, values)

        users = cursor.fetchall()

        cursor.close()

        return users


    # ==========================================================
    # USER STATISTICS
    # ==========================================================

    @staticmethod
    def get_user_statistics():

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                COUNT(*) AS total_users,

                SUM(
                    CASE
                        WHEN role = 'admin'
                        THEN 1
                        ELSE 0
                    END
                ) AS admins,

                SUM(
                    CASE
                        WHEN role = 'owner'
                        THEN 1
                        ELSE 0
                    END
                ) AS owners,

                SUM(
                    CASE
                        WHEN role = 'customer'
                        THEN 1
                        ELSE 0
                    END
                ) AS customers

            FROM users
        """

        cursor.execute(query)

        stats = cursor.fetchone()

        cursor.close()

        return stats


    # ==========================================================
    # GET USER BY ID
    # ==========================================================

    @staticmethod
    def get_user_by_id(user_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                user_id,
                full_name,
                email,
                phone,
                role,
                status,
                created_at

            FROM users

            WHERE user_id = %s
        """

        cursor.execute(query, (user_id,))

        user = cursor.fetchone()

        cursor.close()

        return user


    # ==========================================================
    # UPDATE USER
    # ==========================================================

    @staticmethod
    def update_user(
        user_id,
        full_name,
        email,
        phone,
        role
    ):

        cursor = mysql.connection.cursor()

        query = """
            UPDATE users

            SET
                full_name = %s,
                email = %s,
                phone = %s,
                role = %s

            WHERE user_id = %s
        """

        cursor.execute(
            query,
            (
                full_name,
                email,
                phone,
                role,
                user_id
            )
        )

        mysql.connection.commit()

        cursor.close()


    # ==========================================================
    # DEACTIVATE USER
    # ==========================================================

    @staticmethod
    def deactivate_user(user_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE users

            SET status = 'Inactive'

            WHERE user_id = %s
        """, (user_id,))

        mysql.connection.commit()

        cursor.close()


    # ==========================================================
    # ACTIVATE USER
    # ==========================================================

    @staticmethod
    def activate_user(user_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE users

            SET status = 'Active'

            WHERE user_id = %s
        """, (user_id,))

        mysql.connection.commit()

        cursor.close()


    # ==========================================================
    # VEHICLE MANAGEMENT
    # ==========================================================

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

                v.availability_status,
                v.approval_status,

                v.image,

                u.full_name AS owner_name,

                vc.category_name

            FROM vehicles v

            LEFT JOIN users u
                ON v.owner_id = u.user_id

            LEFT JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            ORDER BY v.vehicle_id ASC
        """

        cursor.execute(query)

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # ==========================================================
    # SEARCH VEHICLES
    # ==========================================================

    @staticmethod
    def search_vehicles(
        search="",
        category="",
        availability="",
        approval=""
    ):

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                v.vehicle_id,
                v.vehicle_name,
                v.model,
                v.vehicle_number,
                v.rent_per_day,

                v.availability_status,
                v.approval_status,

                v.image,
                v.description,
                v.register_at,
                v.created_at,

                u.full_name AS owner_name,

                vc.category_name

            FROM vehicles v

            LEFT JOIN users u
                ON v.owner_id = u.user_id

            LEFT JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            WHERE
            (
                v.vehicle_name LIKE %s
                OR v.model LIKE %s
                OR v.vehicle_number LIKE %s
                OR u.full_name LIKE %s
            )
        """

        values = [
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ]

        if category:

            query += """
                AND v.category_id = %s
            """

            values.append(category)

        if availability:

            query += """
                AND v.availability_status = %s
            """

            values.append(availability)

        if approval:

            query += """
                AND v.approval_status = %s
            """

            values.append(approval)

        query += """
            ORDER BY v.vehicle_id ASC
        """

        cursor.execute(query, values)

        vehicles = cursor.fetchall()

        cursor.close()

        return vehicles


    # ==========================================================
    # GET VEHICLE BY ID
    # ==========================================================

    @staticmethod
    def get_vehicle_by_id(vehicle_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT

                v.vehicle_id,
                v.vehicle_name,
                v.model,
                v.vehicle_number,
                v.rent_per_day,

                v.description,
                v.image,

                v.availability_status,
                v.register_at,
                v.approval_status,
                v.created_at,

                u.user_id AS owner_id,
                u.full_name AS owner_name,
                u.email AS owner_email,
                u.phone AS owner_phone,

                vc.category_id,
                vc.category_name

            FROM vehicles v

            LEFT JOIN users u
                ON v.owner_id = u.user_id

            LEFT JOIN vehicle_categories vc
                ON v.category_id = vc.category_id

            WHERE v.vehicle_id = %s
        """

        cursor.execute(query, (vehicle_id,))

        vehicle = cursor.fetchone()

        cursor.close()

        return vehicle


    # ==========================================================
    # VEHICLE STATISTICS
    # ==========================================================

    @staticmethod
    def get_vehicle_statistics():

        cursor = mysql.connection.cursor()

        # Total
        cursor.execute("""
            SELECT COUNT(*) AS total_vehicles
            FROM vehicles
        """)

        total_vehicles = cursor.fetchone()["total_vehicles"]


        # Available
        cursor.execute("""
            SELECT COUNT(*) AS available
            FROM vehicles
            WHERE LOWER(availability_status) = 'available'
        """)

        available = cursor.fetchone()["available"]


        # Booked
        cursor.execute("""
            SELECT COUNT(*) AS booked
            FROM vehicles
            WHERE LOWER(availability_status) = 'booked'
        """)

        booked = cursor.fetchone()["booked"]


        # Pending Approval
        cursor.execute("""
            SELECT COUNT(*) AS pending
            FROM vehicles
            WHERE LOWER(approval_status) = 'pending'
        """)

        pending = cursor.fetchone()["pending"]


        # Approved
        cursor.execute("""
            SELECT COUNT(*) AS approved
            FROM vehicles
            WHERE LOWER(approval_status) = 'approved'
        """)

        approved = cursor.fetchone()["approved"]


        # Rejected
        cursor.execute("""
            SELECT COUNT(*) AS rejected
            FROM vehicles
            WHERE LOWER(approval_status) = 'rejected'
        """)

        rejected = cursor.fetchone()["rejected"]


        cursor.close()

        return {
            "total_vehicles": total_vehicles,
            "available": available,
            "booked": booked,
            "pending": pending,
            "approved": approved,
            "rejected": rejected
        }
        
            # ==========================================================
    # ADMIN PROFILE
    # ==========================================================

    @staticmethod
    def get_admin_profile(user_id):

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                user_id,
                full_name,
                email,
                phone,
                role,
                status,
                created_at
            FROM users
            WHERE user_id = %s
              AND role = 'admin'
        """

        cursor.execute(query, (user_id,))

        admin = cursor.fetchone()

        cursor.close()

        return admin
    
    @staticmethod
    def update_profile_picture(user_id, filename):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE users
            SET profile_picture = %s
            WHERE user_id = %s
              AND role = 'admin'
        """, (filename, user_id))

        mysql.connection.commit()

        cursor.close()


    @staticmethod
    def remove_profile_picture(user_id):

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE users
            SET profile_picture = NULL
            WHERE user_id = %s
              AND role = 'admin'
        """, (user_id,))

        mysql.connection.commit()

        cursor.close()