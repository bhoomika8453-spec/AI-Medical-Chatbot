from flask import Blueprint, render_template
from flask_login import login_required
from models import Doctor

emergency_bp = Blueprint("emergency", __name__)

HOSPITALS = [
    {"name": "City General Hospital",    "address": "123 Main St",  "phone": "911", "distance": "1.2 km"},
    {"name": "St. Mary Medical Center",  "address": "456 Oak Ave",  "phone": "912", "distance": "2.5 km"},
    {"name": "Downtown Emergency Clinic","address": "789 Pine Rd",  "phone": "913", "distance": "3.1 km"},
]

@emergency_bp.route("/")
@login_required
def index():
    doctors = Doctor.query.join(Doctor.user).all()
    return render_template("emergency/index.html", hospitals=HOSPITALS, doctors=doctors)
