from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, patient
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)

class Doctor(db.Model):
    __tablename__ = 'doctor'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    specialization = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    experience = db.Column(
        db.Integer,
        default=0
    )

    available = db.Column(
        db.Boolean,
        default=True
    )

    # Relationship with User table
    user = db.relationship(
        'User',
        backref=db.backref(
            'doctor_profile',
            uselist=False
        )
    )

    def __repr__(self):
        return f'<Doctor {self.id}>'
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, confirmed, cancelled
    notes = db.Column(db.Text)
    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor  = db.relationship("User", foreign_keys=[doctor_id])

class MedicalHistory(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    patient_id   = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_id    = db.Column(db.Integer, db.ForeignKey("user.id"))
    visit_date   = db.Column(db.Date,    nullable=False)
    symptoms     = db.Column(db.Text)
    diagnosis    = db.Column(db.Text)
    medicines    = db.Column(db.Text)   # comma-separated or free text
    prescription = db.Column(db.Text)   # additional prescription notes
    doctor_notes = db.Column(db.Text)
    date         = db.Column(db.DateTime, default=datetime.utcnow)  # record created_at
    patient      = db.relationship("User", foreign_keys=[patient_id])
    doctor       = db.relationship("User", foreign_keys=[doctor_id])

class InsuranceClaim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    claim_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="submitted")  # submitted, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message           = db.Column(db.Text, nullable=False)
    response          = db.Column(db.Text)
    intent            = db.Column(db.String(30))          # greeting/symptom/emergency/medicine/appointment/smalltalk
    symptoms_detected = db.Column(db.Text)                # comma-separated symptoms found in this turn
    timestamp         = db.Column(db.DateTime, default=datetime.utcnow)
