import pymysql
from config import Config


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


# ==========================================
# REQUEST RISK EXCEPTION
# ==========================================

def request_exception(
    finding_id,
    reason,
    owner,
    expiry_date,
    requested_by=None
):

    if not finding_id:
        raise ValueError("finding_id is required.")

    if not reason or not reason.strip():
        raise ValueError("Reason is required.")

    if not owner or not owner.strip():
        raise ValueError("Owner is required.")

    if not expiry_date:
        raise ValueError("Expiry date is required.")

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            # ------------------------------------------
            # CHECK FINDING EXISTS
            # ------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM findings
                WHERE id = %s
                """,
                (finding_id,)
            )

            finding = cursor.fetchone()

            if not finding:

                raise ValueError(
                    f"Finding with ID {finding_id} was not found."
                )

            # ------------------------------------------
            # CREATE EXCEPTION
            # ------------------------------------------

            sql = """
                INSERT INTO exceptions
                (
                    finding_id,
                    reason,
                    owner,
                    expiry_date,
                    status,
                    requested_by
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                sql,
                (
                    finding_id,
                    reason.strip(),
                    owner.strip(),
                    expiry_date,
                    "Pending",
                    requested_by
                )
            )

            exception_id = cursor.lastrowid

        connection.commit()

        return exception_id

    finally:

        connection.close()


# ==========================================
# GET ALL EXCEPTIONS
# ==========================================

def get_exceptions():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                SELECT
                    id,
                    finding_id,
                    reason,
                    owner,
                    expiry_date,
                    status,
                    requested_by,
                    approved_by,
                    created_at
                FROM exceptions
                ORDER BY created_at DESC
            """

            cursor.execute(sql)

            return cursor.fetchall()

    finally:

        connection.close()


# ==========================================
# GET SINGLE EXCEPTION
# ==========================================

def get_exception(exception_id):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                SELECT
                    id,
                    finding_id,
                    reason,
                    owner,
                    expiry_date,
                    status,
                    requested_by,
                    approved_by,
                    created_at
                FROM exceptions
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (exception_id,)
            )

            return cursor.fetchone()

    finally:

        connection.close()


# ==========================================
# APPROVE EXCEPTION
# ==========================================

def approve_exception(
    exception_id,
    approved_by=None
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            # ------------------------------------------
            # CHECK EXCEPTION EXISTS
            # ------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM exceptions
                WHERE id = %s
                """,
                (exception_id,)
            )

            exception = cursor.fetchone()

            if not exception:

                raise ValueError(
                    f"Exception with ID {exception_id} was not found."
                )

            # ------------------------------------------
            # APPROVE EXCEPTION
            # ------------------------------------------

            cursor.execute(
                """
                UPDATE exceptions
                SET
                    status = %s,
                    approved_by = %s
                WHERE id = %s
                """,
                (
                    "Approved",
                    approved_by,
                    exception_id
                )
            )

        connection.commit()

        return True

    finally:

        connection.close()


# ==========================================
# REJECT EXCEPTION
# ==========================================

def reject_exception(
    exception_id,
    approved_by=None
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            # ------------------------------------------
            # CHECK EXCEPTION EXISTS
            # ------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM exceptions
                WHERE id = %s
                """,
                (exception_id,)
            )

            exception = cursor.fetchone()

            if not exception:

                raise ValueError(
                    f"Exception with ID {exception_id} was not found."
                )

            # ------------------------------------------
            # REJECT EXCEPTION
            # ------------------------------------------

            cursor.execute(
                """
                UPDATE exceptions
                SET
                    status = %s,
                    approved_by = %s
                WHERE id = %s
                """,
                (
                    "Rejected",
                    approved_by,
                    exception_id
                )
            )

        connection.commit()

        return True

    finally:

        connection.close()


# ==========================================
# CHECK EXPIRED EXCEPTIONS
# ==========================================

def check_expired_exceptions():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                UPDATE exceptions
                SET status = %s
                WHERE expiry_date < CURDATE()
                AND status = %s
            """

            cursor.execute(
                sql,
                (
                    "Expired",
                    "Approved"
                )
            )

            expired_count = cursor.rowcount

        connection.commit()

        return expired_count

    finally:

        connection.close()


# ==========================================
# GET ACTIVE EXCEPTIONS
# ==========================================

def get_active_exceptions():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                SELECT
                    id,
                    finding_id,
                    reason,
                    owner,
                    expiry_date,
                    status,
                    requested_by,
                    approved_by,
                    created_at
                FROM exceptions
                WHERE status = %s
                AND expiry_date >= CURDATE()
                ORDER BY expiry_date ASC
            """

            cursor.execute(
                sql,
                ("Approved",)
            )

            return cursor.fetchall()

    finally:

        connection.close()


# ==========================================
# GET EXCEPTIONS FOR A FINDING
# ==========================================

def get_finding_exceptions(finding_id):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                SELECT
                    id,
                    finding_id,
                    reason,
                    owner,
                    expiry_date,
                    status,
                    requested_by,
                    approved_by,
                    created_at
                FROM exceptions
                WHERE finding_id = %s
                ORDER BY created_at DESC
            """

            cursor.execute(
                sql,
                (finding_id,)
            )

            return cursor.fetchall()

    finally:

        connection.close()