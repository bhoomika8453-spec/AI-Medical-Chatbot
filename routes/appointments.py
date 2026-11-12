from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date
from models import db, Appointment, Doctor

appointments_bp = Blueprint("appointments", __name__)

@appointments_bp.route("/book", methods=["GET", "POST"])
@login_required
def book():
    doctors = Doctor.query.filter_by(available=True).join(Doctor.user).all()
    if request.method == "POST":
        chosen_date = request.form.get("date")
        if chosen_date < str(date.today()):
            flash("Please select a future date.", "warning")
            return render_template("appointments/book.html", doctors=doctors)
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=request.form.get("doctor_id"),
            date=chosen_date,
            time=request.form.get("time"),
            notes=request.form.get("notes")
        )
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment booked successfully.", "success")
        return redirect(url_for("appointments.list_appointments"))
    return render_template("appointments/book.html", doctors=doctors)

@appointments_bp.route("/list")
@login_required
def list_appointments():
    appointments = (Appointment.query
                    .filter_by(patient_id=current_user.id)
                    .order_by(Appointment.date.desc(), Appointment.time.desc())
                    .all())
    return render_template("appointments/list.html", appointments=appointments)
