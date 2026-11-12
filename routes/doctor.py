from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date as date_type
from models import db, Appointment, MedicalHistory, User

doctor_bp = Blueprint("doctor", __name__)


@doctor_bp.route("/dashboard")
@login_required
def dashboard():
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    return render_template("doctor/dashboard.html", appointments=appointments)


@doctor_bp.route("/appointments")
@login_required
def appointments():
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    return render_template("doctor/appointments.html", appointments=appointments)


@doctor_bp.route("/patients")
@login_required
def patients():
    # All unique patients who have appointments with this doctor
    appts = (Appointment.query
             .filter_by(doctor_id=current_user.id)
             .order_by(Appointment.date.desc())
             .all())
    # Deduplicate patients while preserving order
    seen, patient_list = set(), []
    for a in appts:
        if a.patient_id not in seen:
            seen.add(a.patient_id)
            record_count = MedicalHistory.query.filter_by(
                patient_id=a.patient_id, doctor_id=current_user.id).count()
            patient_list.append({
                "user":         a.patient,
                "last_visit":   a.date,
                "record_count": record_count,
            })
    return render_template("doctor/patients.html", patients=patient_list)


@doctor_bp.route("/records/<int:patient_id>")
@login_required
def patient_records(patient_id):
    patient = User.query.get_or_404(patient_id)
    records = (MedicalHistory.query
               .filter_by(patient_id=patient_id, doctor_id=current_user.id)
               .order_by(MedicalHistory.visit_date.desc())
               .all())
    return render_template("doctor/patient_records.html",
                           patient=patient, records=records)


@doctor_bp.route("/records/<int:patient_id>/add", methods=["GET", "POST"])
@login_required
def add_record(patient_id):
    patient = User.query.get_or_404(patient_id)
    if request.method == "POST":
        visit_date_str = request.form.get("visit_date")
        record = MedicalHistory(
            patient_id   = patient_id,
            doctor_id    = current_user.id,
            visit_date   = date_type.fromisoformat(visit_date_str),
            symptoms     = request.form.get("symptoms", "").strip(),
            diagnosis    = request.form.get("diagnosis", "").strip(),
            medicines    = request.form.get("medicines", "").strip(),
            prescription = request.form.get("prescription", "").strip(),
            doctor_notes = request.form.get("doctor_notes", "").strip(),
        )
        db.session.add(record)
        db.session.commit()
        flash(f"Medical record added for {patient.name}.", "success")
        return redirect(url_for("doctor.patient_records", patient_id=patient_id))
    return render_template("doctor/add_record.html",
                           patient=patient, today=date_type.today().isoformat())


@doctor_bp.route("/records/edit/<int:record_id>", methods=["GET", "POST"])
@login_required
def edit_record(record_id):
    record  = MedicalHistory.query.get_or_404(record_id)
    patient = User.query.get_or_404(record.patient_id)
    if request.method == "POST":
        record.visit_date   = date_type.fromisoformat(request.form.get("visit_date"))
        record.symptoms     = request.form.get("symptoms", "").strip()
        record.diagnosis    = request.form.get("diagnosis", "").strip()
        record.medicines    = request.form.get("medicines", "").strip()
        record.prescription = request.form.get("prescription", "").strip()
        record.doctor_notes = request.form.get("doctor_notes", "").strip()
        db.session.commit()
        flash("Record updated successfully.", "success")
        return redirect(url_for("doctor.patient_records", patient_id=record.patient_id))
    return render_template("doctor/edit_record.html", record=record, patient=patient)


@doctor_bp.route("/records/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(record_id):
    record = MedicalHistory.query.get_or_404(record_id)
    patient_id = record.patient_id
    db.session.delete(record)
    db.session.commit()
    flash("Record deleted.", "danger")
    return redirect(url_for("doctor.patient_records", patient_id=patient_id))
