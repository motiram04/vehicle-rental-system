from database.db import mysql
from werkzeug.security import generate_password_hash, check_password_hash


class UserModel:

    @staticmethod
    def get_user_by_email(email):
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()
        cursor.close()

        return user

    @staticmethod
    def get_user_by_id(user_id):
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE user_id=%s",
            (user_id,)
        )

        user = cursor.fetchone()
        cursor.close()

        return user

    @staticmethod
    def create_user(full_name,
                    email,
                    phone,
                    address,
                    password,
                    role):

        cursor = mysql.connection.cursor()

        hashed_password = generate_password_hash(password)

        sql = """
        INSERT INTO users
        (
            full_name,
            email,
            phone,
            address,
            password,
            role,
            status,
            last_login
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,'active',NOW()
        )
        """

        cursor.execute(sql, (

            full_name,
            email,
            phone,
            address,
            hashed_password,
            role

        ))

        mysql.connection.commit()

        cursor.close()

    @staticmethod
    def verify_password(hashed_password, password):

        return check_password_hash(
            hashed_password,
            password
        )

    @staticmethod
    def update_last_login(user_id):

        cursor = mysql.connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET last_login=NOW()
            WHERE user_id=%s
            """,
            (user_id,)
        )

        mysql.connection.commit()

        cursor.close()