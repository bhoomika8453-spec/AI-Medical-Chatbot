from flask import Blueprint, render_template, request
from flask_login import login_required
from predictor import predict, DISEASE_DB

predict_bp = Blueprint("predict", __name__)

# Build a flat sorted list of all unique symptoms for the frontend autocomplete
ALL_SYMPTOMS = sorted({
    symptom
    for data in DISEASE_DB.values()
    for symptom in data["symptoms"]
})

@predict_bp.route("/", methods=["GET", "POST"])
@login_required
def predict_disease():
    result      = None
    user_input  = ""
    error       = None

    if request.method == "POST":
        user_input = request.form.get("symptoms", "").strip()
        if user_input:
            result = predict(user_input)
            if result is None:
                error = "No matching disease found for the entered symptoms. Please try different or more specific symptoms."

    return render_template("predict/predict.html",
                           result=result,
                           user_input=user_input,
                           error=error,
                           all_symptoms=ALL_SYMPTOMS)
