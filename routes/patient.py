from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Appointment, MedicalHistory, InsuranceClaim, Doctor

patient_bp = Blueprint("patient", __name__)

@patient_bp.route("/dashboard")
@login_required
def dashboard():
    appointments = (Appointment.query
                    .filter_by(patient_id=current_user.id)
                    .order_by(Appointment.date.desc())
                    .all())
    claims = InsuranceClaim.query.filter_by(patient_id=current_user.id).all()
    return render_template("patient/dashboard.html",
                           appointments=appointments, claims=claims)

@patient_bp.route("/history")
@login_required
def history():
    records = MedicalHistory.query.filter_by(patient_id=current_user.id).all()
    return render_template("patient/history.html", records=records)

@patient_bp.route("/profile")
@login_required
def profile():
    return render_template("patient/profile.html")
