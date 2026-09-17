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
# TEST DATABASE CONNECTION
# ==========================================

def test_connection():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT DATABASE() AS database_name"
            )

            result = cursor.fetchone()

            return result

    finally:

        connection.close()


# ==========================================
# SAVE ASSESSMENT
# ==========================================

def save_assessment(
    project_name,
    project_path,
    score,
    status,
    total_rules,
    passed_rules,
    failed_rules,
    duration_seconds
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                INSERT INTO assessments
                (
                    project_name,
                    project_path,
                    score,
                    status,
                    total_rules,
                    passed_rules,
                    failed_rules,
                    duration_seconds
                )
                VALUES
                (
                    %s,
                    %s,
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
                    project_name,
                    project_path,
                    score,
                    status,
                    total_rules,
                    passed_rules,
                    failed_rules,
                    duration_seconds
                )
            )

            assessment_id = cursor.lastrowid

        connection.commit()

        return assessment_id

    finally:

        connection.close()


# ==========================================
# SAVE FINDING
# ==========================================

def save_finding(assessment_id, finding):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                INSERT INTO findings
                (
                    assessment_id,
                    rule_id,
                    name,
                    category,
                    severity,
                    message,
                    file_path,
                    line_number,
                    evidence,
                    remediation,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
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
                    assessment_id,
                    finding["rule_id"],
                    finding["name"],
                    finding["category"],
                    finding["severity"],
                    finding["message"],
                    finding.get("file_path"),
                    finding.get("line_number"),
                    finding.get("evidence"),
                    finding["remediation"],
                    finding.get("status", "Open")
                )
            )

            finding_id = cursor.lastrowid

        connection.commit()

        return finding_id

    finally:

        connection.close()


# ==========================================
# GET ASSESSMENT HISTORY
# ==========================================

def get_assessments():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                SELECT
                    id,
                    project_name,
                    project_path,
                    assessment_date,
                    score,
                    status,
                    total_rules,
                    passed_rules,
                    failed_rules,
                    duration_seconds
                FROM assessments
                ORDER BY assessment_date DESC
            """

            cursor.execute(sql)

            return cursor.fetchall()

    finally:

        connection.close()


# ==========================================
# GET SINGLE ASSESSMENT
# ==========================================

def get_assessment(assessment_id):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                SELECT
                    id,
                    project_name,
                    project_path,
                    assessment_date,
                    score,
                    status,
                    total_rules,
                    passed_rules,
                    failed_rules,
                    duration_seconds
                FROM assessments
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (assessment_id,)
            )

            return cursor.fetchone()

    finally:

        connection.close()


# ==========================================
# GET FINDINGS FOR AN ASSESSMENT
# ==========================================

def get_findings(assessment_id):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                SELECT
                    id,
                    assessment_id,
                    rule_id,
                    name,
                    category,
                    severity,
                    message,
                    file_path,
                    line_number,
                    evidence,
                    remediation,
                    status
                FROM findings
                WHERE assessment_id = %s
                ORDER BY id ASC
            """

            cursor.execute(
                sql,
                (assessment_id,)
            )

            return cursor.fetchall()

    finally:

        connection.close()


# ==========================================
# UPDATE FINDING STATUS
# ==========================================

def update_finding_status(finding_id, status):

    allowed_statuses = {
        "Open",
        "In Progress",
        "Resolved"
    }

    if status not in allowed_statuses:

        raise ValueError(
            "Invalid status. "
            "Allowed values are: Open, In Progress, Resolved."
        )

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                UPDATE findings
                SET status = %s
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (
                    status,
                    finding_id
                )
            )

            rows_updated = cursor.rowcount

        connection.commit()

        if rows_updated == 0:

            raise ValueError(
                f"Finding with ID {finding_id} was not found."
            )

        return True

    finally:

        connection.close()


# ==========================================
# GET SINGLE FINDING
# ==========================================

def get_finding(finding_id):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            sql = """
                SELECT
                    id,
                    assessment_id,
                    rule_id,
                    name,
                    category,
                    severity,
                    message,
                    file_path,
                    line_number,
                    evidence,
                    remediation,
                    status
                FROM findings
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (finding_id,)
            )

            return cursor.fetchone()

    finally:

        connection.close()

# ==========================================
# GET DASHBOARD ANALYTICS
# ==========================================

def get_dashboard_analytics():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            # ------------------------------------------
            # ASSESSMENT SUMMARY
            # ------------------------------------------

            cursor.execute("""
                SELECT
                    COUNT(*) AS total_assessments,
                    COALESCE(AVG(score), 0) AS average_score,
                    SUM(
                        CASE
                            WHEN status = 'Ready'
                            THEN 1
                            ELSE 0
                        END
                    ) AS ready_projects,
                    SUM(
                        CASE
                            WHEN status != 'Ready'
                            THEN 1
                            ELSE 0
                        END
                    ) AS attention_projects
                FROM assessments
            """)

            assessment_summary = cursor.fetchone()


            # ------------------------------------------
            # FINDING SUMMARY
            # ------------------------------------------

            cursor.execute("""
                SELECT
                    SUM(
                        CASE
                            WHEN status = 'Open'
                            THEN 1
                            ELSE 0
                        END
                    ) AS open_findings,

                    SUM(
                        CASE
                            WHEN status = 'Resolved'
                            THEN 1
                            ELSE 0
                        END
                    ) AS resolved_findings
                FROM findings
            """)

            finding_summary = cursor.fetchone()


            # ------------------------------------------
            # SCORE TREND
            # ------------------------------------------

            cursor.execute("""
                SELECT
                    id,
                    project_name,
                    score,
                    status,
                    assessment_date
                FROM assessments
                ORDER BY assessment_date ASC
            """)

            score_trend = cursor.fetchall()


            # ------------------------------------------
            # RETURN ANALYTICS
            # ------------------------------------------

            return {
                "total_assessments": assessment_summary["total_assessments"] or 0,
                "average_score": round(
                    float(assessment_summary["average_score"] or 0),
                    2
                ),
                "ready_projects": assessment_summary["ready_projects"] or 0,
                "attention_projects": assessment_summary["attention_projects"] or 0,

                "open_findings": finding_summary["open_findings"] or 0,
                "resolved_findings": finding_summary["resolved_findings"] or 0,

                "score_trend": score_trend
            }

    finally:

        connection.close()