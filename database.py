from models import db, User, Doctor
from werkzeug.security import generate_password_hash

SAMPLE_DOCTORS = [
    {"name": "Dr. Sarah Mitchell",  "email": "sarah.mitchell@medical.com",  "specialization": "Cardiologist",       "phone": "+1-555-0101", "experience": 12},
    {"name": "Dr. James Patel",     "email": "james.patel@medical.com",     "specialization": "Neurologist",        "phone": "+1-555-0102", "experience": 9},
    {"name": "Dr. Emily Chen",      "email": "emily.chen@medical.com",      "specialization": "General Physician",  "phone": "+1-555-0103", "experience": 7},
    {"name": "Dr. Robert Okafor",   "email": "robert.okafor@medical.com",   "specialization": "Orthopedic Surgeon", "phone": "+1-555-0104", "experience": 15},
    {"name": "Dr. Priya Sharma",    "email": "priya.sharma@medical.com",    "specialization": "Dermatologist",      "phone": "+1-555-0105", "experience": 6},
]

def init_db(app):
    with app.app_context():
        db.create_all()

        # Seed admin
        if not User.query.filter_by(email="admin@medical.com").first():
            admin = User(name="Admin", email="admin@medical.com",
                         password=generate_password_hash("admin123"), role="admin")
            db.session.add(admin)
            db.session.commit()
            print("Admin user seeded.")

        # Seed doctors
        for d in SAMPLE_DOCTORS:
            if not User.query.filter_by(email=d["email"]).first():
                user = User(name=d["name"], email=d["email"],
                            password=generate_password_hash("doctor123"), role="doctor")
                db.session.add(user)
                db.session.flush()  # get user.id before commit
                doctor = Doctor(user_id=user.id, specialization=d["specialization"],
                                phone=d["phone"], experience=d["experience"], available=True)
                db.session.add(doctor)
        db.session.commit()
        print("Sample doctors seeded.")
