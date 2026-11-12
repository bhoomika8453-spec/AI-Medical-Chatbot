from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, InsuranceClaim

insurance_bp = Blueprint("insurance", __name__)

@insurance_bp.route("/")
@login_required
def index():
    claims = InsuranceClaim.query.filter_by(patient_id=current_user.id).all()
    return render_template("insurance/index.html", claims=claims)

@insurance_bp.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    if request.method == "POST":
        claim = InsuranceClaim(
            patient_id=current_user.id,
            claim_amount=request.form.get("amount"),
            description=request.form.get("description")
        )
        db.session.add(claim)
        db.session.commit()
        flash("Insurance claim submitted.", "success")
        return redirect(url_for("insurance.index"))
    return render_template("insurance/submit.html")
