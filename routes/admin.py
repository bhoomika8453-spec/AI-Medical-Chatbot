from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import db, User, Doctor, Appointment, InsuranceClaim
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
from collections import Counter

admin_bp = Blueprint("admin", __name__)


def _last_7_days():
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]


@admin_bp.route("/dashboard")
@login_required
def dashboard():

    users = User.query.all()
    appointments = Appointment.query.all()
    claims = InsuranceClaim.query.all()
    doctors = Doctor.query.all()

    # --- stat counts ---
    total_patients = User.query.filter_by(role="patient").count()
    total_doctors = User.query.filter_by(role="doctor").count()

    # --- appointments per day (last 7 days) ---
    days = _last_7_days()

    ap_counts = Counter()

    for a in appointments:
        if a.date:
            ap_counts[str(a.date)] += 1

    appt_per_day = [ap_counts.get(d, 0) for d in days]
    appt_labels = [d[5:] for d in days]

    # --- claims by status ---
    claim_counts = Counter(c.status for c in claims)

    claim_labels = ["submitted", "approved", "rejected"]
    claim_data = [claim_counts.get(s, 0) for s in claim_labels]

    # --- role breakdown ---
    role_counts = Counter(u.role for u in users)

    role_labels = ["patient", "doctor", "admin"]
    role_data = [role_counts.get(r, 0) for r in role_labels]

    # --- recent activity ---
    activity = []

    for a in Appointment.query.order_by(Appointment.id.desc()).limit(5).all():

        patient_name = a.patient.name if a.patient else "Unknown Patient"
        doctor_name = a.doctor.name if a.doctor else "Unknown Doctor"

        activity.append({
            "icon": "calendar-check",
            "color": "primary",
            "text": f"Appointment booked by {patient_name} with {doctor_name}",
            "time": f"{a.date} {a.time}",
        })

    for c in InsuranceClaim.query.order_by(InsuranceClaim.id.desc()).limit(3).all():

        activity.append({
            "icon": "shield-check",
            "color": "warning",
            "text": f"Insurance claim submitted — ${c.claim_amount:.0f}",
            "time": c.submitted_at.strftime("%Y-%m-%d"),
        })

    for u in User.query.order_by(User.id.desc()).limit(3).all():

        activity.append({
            "icon": "person-plus",
            "color": "success",
            "text": f"New {u.role} registered: {u.name}",
            "time": u.created_at.strftime("%Y-%m-%d"),
        })

    activity = sorted(activity, key=lambda x: x["time"], reverse=True)[:10]

    return render_template(
        "admin/dashboard.html",
        users=users,
        appointments=appointments,
        claims=claims,
        doctors=doctors,
        total_patients=total_patients,
        total_doctors=total_doctors,
        appt_labels=appt_labels,
        appt_per_day=appt_per_day,
        claim_labels=claim_labels,
        claim_data=claim_data,
        role_labels=role_labels,
        role_data=role_data,
        activity=activity
    )


@admin_bp.route("/users")
@login_required
def manage_users():

    users = User.query.all()
    return render_template("admin/users.html", users=users)


VALID_STATUSES = {"pending", "confirmed", "completed", "cancelled"}


@admin_bp.route("/appointments")
@login_required
def manage_appointments():

    status_filter = request.args.get("status", "all")

    query = Appointment.query

    if status_filter in VALID_STATUSES:
        query = query.filter_by(status=status_filter)

    appointments = query.order_by(
        Appointment.date.desc(),
        Appointment.time.desc()
    ).all()

    return render_template(
        "admin/appointments.html",
        appointments=appointments,
        status_filter=status_filter
    )


@admin_bp.route("/appointments/status/<int:appointment_id>", methods=["POST"])
@login_required
def update_appointment_status(appointment_id):

    appointment = Appointment.query.get_or_404(appointment_id)

    data = request.get_json()

    status = (data.get("status") or "").strip().lower()

    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    appointment.status = status

    db.session.commit()

    return jsonify({
        "success": True,
        "status": status
    })


@admin_bp.route("/claims")
@login_required
def manage_claims():

    claims = InsuranceClaim.query.all()

    return render_template(
        "admin/claims.html",
        claims=claims
    )


@admin_bp.route("/doctors")
@login_required
def manage_doctors():

    doctors = Doctor.query.all()

    return render_template(
        "admin/doctors.html",
        doctors=doctors
    )


@admin_bp.route("/doctors/add", methods=["GET", "POST"])
@login_required
def add_doctor():

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        if User.query.filter_by(email=email).first():

            flash("Email already registered.", "warning")

            return redirect(url_for("admin.add_doctor"))

        user = User(
            name=request.form.get("name", "").strip(),
            email=email,
            password=generate_password_hash(
                request.form.get("password", "")
            ),
            role="doctor"
        )

        db.session.add(user)
        db.session.flush()

        try:
            experience = int(
                request.form.get("experience", 0)
            )

        except (ValueError, TypeError):
            experience = 0

        doctor = Doctor(
            user_id=user.id,
            specialization=request.form.get(
                "specialization", ""
            ).strip(),
            phone=request.form.get("phone", "").strip(),
            experience=experience
        )

        db.session.add(doctor)

        db.session.commit()

        flash("Doctor added successfully.", "success")

        return redirect(url_for("admin.manage_doctors"))

    return render_template("admin/add_doctor.html")


@admin_bp.route("/doctors/toggle/<int:doctor_id>")
@login_required
def toggle_availability(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    doctor.available = not doctor.available

    db.session.commit()

    flash("Doctor availability updated.", "info")

    return redirect(url_for("admin.manage_doctors"))


@admin_bp.route("/doctors/delete/<int:doctor_id>")
@login_required
def delete_doctor(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    user = User.query.get(doctor.user_id)

    db.session.delete(doctor)

    if user:
        db.session.delete(user)

    db.session.commit()

    flash("Doctor removed.", "danger")

    return redirect(url_for("admin.manage_doctors"))