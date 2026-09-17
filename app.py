from flask import Flask, jsonify, request, render_template

from database import (
    test_connection,
    get_assessments,
    get_findings,
    get_finding,
    update_finding_status,
    get_dashboard_analytics
)
from config import Config
from assessment import AssessmentEngine

from exceptions import (
    request_exception,
    get_exceptions,
    get_exception,
    approve_exception,
    reject_exception,
    check_expired_exceptions,
    get_active_exceptions,
    get_finding_exceptions
)


app = Flask(__name__)


# ==========================================
# HOME / DASHBOARD
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "message": "Production Readiness Assessment Platform is running"
    })


# ==========================================
# DATABASE TEST
# ==========================================

@app.route("/database-test")
def database_test():

    try:

        result = test_connection()

        return jsonify({
            "status": "success",
            "database": result["database_name"]
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# RUN ASSESSMENT
# ==========================================

@app.route("/api/assessments", methods=["POST"])
def run_assessment():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "status": "error",
                "message": "Request body is required."
            }), 400

        project_path = data.get("project_path")

        if not project_path:

            return jsonify({
                "status": "error",
                "message": "project_path is required."
            }), 400

        # Create assessment engine
        engine = AssessmentEngine(project_path)

        # Run assessment
        result = engine.run()

        return jsonify({
            "status": "success",
            "assessment": result
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET ASSESSMENT HISTORY
# ==========================================

@app.route("/api/assessments", methods=["GET"])
def get_assessment_history():

    try:

        assessments = get_assessments()

        return jsonify({
            "status": "success",
            "assessments": assessments
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET SINGLE ASSESSMENT
# ==========================================

@app.route(
    "/api/assessments/<int:assessment_id>",
    methods=["GET"]
)
def get_single_assessment(assessment_id):

    try:

        assessment = get_assessments(
            assessment_id
        )

        if not assessment:

            return jsonify({
                "status": "error",
                "message": "Assessment not found."
            }), 404

        return jsonify({
            "status": "success",
            "assessment": assessment
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET FINDINGS FOR AN ASSESSMENT
# ==========================================

@app.route(
    "/api/assessments/<int:assessment_id>/findings",
    methods=["GET"]
)
def get_assessment_findings(assessment_id):

    try:

        findings = get_findings(
            assessment_id
        )

        return jsonify({
            "status": "success",
            "findings": findings
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET SINGLE FINDING
# ==========================================

@app.route(
    "/api/findings/<int:finding_id>",
    methods=["GET"]
)
def get_single_finding(finding_id):

    try:

        finding = get_finding(
            finding_id
        )

        if not finding:

            return jsonify({
                "status": "error",
                "message": "Finding not found."
            }), 404

        return jsonify({
            "status": "success",
            "finding": finding
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# UPDATE FINDING STATUS
# ==========================================

@app.route(
    "/api/findings/<int:finding_id>/status",
    methods=["PUT"]
)
def change_finding_status(finding_id):

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "status": "error",
                "message": "Request body is required."
            }), 400

        new_status = data.get("status")

        if not new_status:

            return jsonify({
                "status": "error",
                "message": "status is required."
            }), 400

        # Update finding status
        update_finding_status(
            finding_id,
            new_status
        )

        # Get updated finding
        updated_finding = get_finding(
            finding_id
        )

        return jsonify({
            "status": "success",
            "message": "Finding status updated successfully.",
            "finding": updated_finding
        })

    except ValueError as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET DASHBOARD ANALYTICS
# ==========================================

@app.route(
    "/api/dashboard/analytics",
    methods=["GET"]
)
def dashboard_analytics():

    try:

        analytics = get_dashboard_analytics()

        return jsonify({
            "status": "success",
            "analytics": analytics
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# RISK EXCEPTION MANAGEMENT
# ==========================================


# ==========================================
# REQUEST RISK EXCEPTION
# ==========================================

@app.route(
    "/api/exceptions",
    methods=["POST"]
)
def create_exception():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "status": "error",
                "message": "Request body is required."
            }), 400

        finding_id = data.get("finding_id")
        reason = data.get("reason")
        owner = data.get("owner")
        expiry_date = data.get("expiry_date")
        requested_by = data.get("requested_by")

        if not finding_id:

            return jsonify({
                "status": "error",
                "message": "finding_id is required."
            }), 400

        if not reason:

            return jsonify({
                "status": "error",
                "message": "reason is required."
            }), 400

        if not owner:

            return jsonify({
                "status": "error",
                "message": "owner is required."
            }), 400

        if not expiry_date:

            return jsonify({
                "status": "error",
                "message": "expiry_date is required."
            }), 400

        exception_id = request_exception(
            finding_id=finding_id,
            reason=reason,
            owner=owner,
            expiry_date=expiry_date,
            requested_by=requested_by
        )

        exception = get_exception(
            exception_id
        )

        return jsonify({
            "status": "success",
            "message": "Risk exception requested successfully.",
            "exception": exception
        }), 201

    except ValueError as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET ALL RISK EXCEPTIONS
# ==========================================

@app.route(
    "/api/exceptions",
    methods=["GET"]
)
def list_exceptions():

    try:

        # Automatically mark expired exceptions
        check_expired_exceptions()

        exceptions = get_exceptions()

        return jsonify({
            "status": "success",
            "exceptions": exceptions
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET SINGLE RISK EXCEPTION
# ==========================================

@app.route(
    "/api/exceptions/<int:exception_id>",
    methods=["GET"]
)
def get_single_exception(exception_id):

    try:

        # Automatically check expiration
        check_expired_exceptions()

        exception = get_exception(
            exception_id
        )

        if not exception:

            return jsonify({
                "status": "error",
                "message": "Risk exception not found."
            }), 404

        return jsonify({
            "status": "success",
            "exception": exception
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# APPROVE RISK EXCEPTION
# ==========================================

@app.route(
    "/api/exceptions/<int:exception_id>/approve",
    methods=["POST"]
)
def approve_risk_exception(exception_id):

    try:

        data = request.get_json(
            silent=True
        ) or {}

        approved_by = data.get(
            "approved_by"
        )

        approve_exception(
            exception_id,
            approved_by
        )

        updated_exception = get_exception(
            exception_id
        )

        return jsonify({
            "status": "success",
            "message": "Risk exception approved successfully.",
            "exception": updated_exception
        })

    except ValueError as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# REJECT RISK EXCEPTION
# ==========================================

@app.route(
    "/api/exceptions/<int:exception_id>/reject",
    methods=["POST"]
)
def reject_risk_exception(exception_id):

    try:

        data = request.get_json(
            silent=True
        ) or {}

        approved_by = data.get(
            "approved_by"
        )

        reject_exception(
            exception_id,
            approved_by
        )

        updated_exception = get_exception(
            exception_id
        )

        return jsonify({
            "status": "success",
            "message": "Risk exception rejected successfully.",
            "exception": updated_exception
        })

    except ValueError as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET ACTIVE RISK EXCEPTIONS
# ==========================================

@app.route(
    "/api/exceptions/active",
    methods=["GET"]
)
def list_active_exceptions():

    try:

        check_expired_exceptions()

        exceptions = get_active_exceptions()

        return jsonify({
            "status": "success",
            "exceptions": exceptions
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# GET EXCEPTIONS FOR A FINDING
# ==========================================

@app.route(
    "/api/exceptions/finding/<int:finding_id>",
    methods=["GET"]
)
def list_finding_exceptions(finding_id):

    try:

        check_expired_exceptions()

        exceptions = get_finding_exceptions(
            finding_id
        )

        return jsonify({
            "status": "success",
            "finding_id": finding_id,
            "exceptions": exceptions
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# CHECK EXPIRED EXCEPTIONS
# ==========================================

@app.route(
    "/api/exceptions/check-expired",
    methods=["POST"]
)
def update_expired_exceptions():

    try:

        expired_count = check_expired_exceptions()

        return jsonify({
            "status": "success",
            "message": "Expired exceptions checked successfully.",
            "expired_count": expired_count
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================
# APPLICATION START
# ==========================================

if __name__ == "__main__":
    app.run(
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        debug=False
    )