"""
Symptom-based disease prediction engine.
Uses weighted keyword overlap scoring — no external ML libraries required.
"""

DISEASE_DB = {
    "Influenza (Flu)": {
        "symptoms": ["fever", "cough", "fatigue", "body ache", "chills", "sore throat",
                     "runny nose", "headache", "sneezing", "loss of appetite"],
        "precautions": [
            "Rest and stay hydrated",
            "Take fever-reducing medication (paracetamol)",
            "Avoid contact with others to prevent spread",
            "Use a humidifier to ease congestion",
            "Wash hands frequently",
        ],
        "specialist": "General Physician",
        "severity": "Moderate",
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "fatigue", "loss of smell", "loss of taste",
                     "shortness of breath", "body ache", "chills", "sore throat",
                     "headache", "diarrhea"],
        "precautions": [
            "Isolate immediately and get tested",
            "Monitor oxygen levels with a pulse oximeter",
            "Stay hydrated and rest",
            "Seek emergency care if breathing becomes difficult",
            "Inform close contacts",
        ],
        "specialist": "Infectious Disease Specialist",
        "severity": "High",
    },
    "Migraine": {
        "symptoms": ["headache", "nausea", "vomiting", "sensitivity to light",
                     "sensitivity to sound", "blurred vision", "dizziness", "fatigue"],
        "precautions": [
            "Rest in a dark, quiet room",
            "Apply cold or warm compress to the head",
            "Stay hydrated",
            "Avoid known triggers (bright lights, strong smells)",
            "Take prescribed migraine medication",
        ],
        "specialist": "Neurologist",
        "severity": "Moderate",
    },
    "Type 2 Diabetes": {
        "symptoms": ["frequent urination", "excessive thirst", "fatigue", "blurred vision",
                     "slow healing wounds", "weight loss", "numbness in hands",
                     "numbness in feet", "increased hunger", "dry mouth"],
        "precautions": [
            "Monitor blood sugar levels regularly",
            "Follow a low-sugar, balanced diet",
            "Exercise at least 30 minutes daily",
            "Take prescribed medication consistently",
            "Avoid smoking and alcohol",
        ],
        "specialist": "Endocrinologist",
        "severity": "High",
    },
    "Hypertension": {
        "symptoms": ["headache", "dizziness", "blurred vision", "chest pain",
                     "shortness of breath", "nosebleed", "fatigue", "irregular heartbeat"],
        "precautions": [
            "Reduce salt intake in your diet",
            "Exercise regularly and maintain healthy weight",
            "Take blood pressure medication as prescribed",
            "Avoid stress and practice relaxation techniques",
            "Limit alcohol and quit smoking",
        ],
        "specialist": "Cardiologist",
        "severity": "High",
    },
    "Pneumonia": {
        "symptoms": ["fever", "cough", "chest pain", "shortness of breath", "fatigue",
                     "chills", "sweating", "nausea", "vomiting", "rapid breathing"],
        "precautions": [
            "Complete the full course of prescribed antibiotics",
            "Rest and avoid strenuous activity",
            "Stay hydrated with fluids",
            "Use a humidifier to ease breathing",
            "Seek emergency care if breathing worsens",
        ],
        "specialist": "Pulmonologist",
        "severity": "High",
    },
    "Gastroenteritis": {
        "symptoms": ["nausea", "vomiting", "diarrhea", "stomach pain", "cramps",
                     "fever", "fatigue", "loss of appetite", "bloating", "headache"],
        "precautions": [
            "Stay hydrated with oral rehydration salts (ORS)",
            "Eat bland foods (rice, toast, bananas)",
            "Avoid dairy, fatty, and spicy foods",
            "Wash hands thoroughly before eating",
            "Rest and avoid strenuous activity",
        ],
        "specialist": "Gastroenterologist",
        "severity": "Moderate",
    },
    "Urinary Tract Infection (UTI)": {
        "symptoms": ["burning urination", "frequent urination", "cloudy urine",
                     "pelvic pain", "lower back pain", "fever", "chills",
                     "strong urine odor", "blood in urine"],
        "precautions": [
            "Drink plenty of water to flush bacteria",
            "Complete the full antibiotic course",
            "Avoid holding urine for long periods",
            "Wipe front to back after using the toilet",
            "Avoid irritants like caffeine and alcohol",
        ],
        "specialist": "Urologist",
        "severity": "Moderate",
    },
    "Asthma": {
        "symptoms": ["shortness of breath", "wheezing", "chest tightness", "cough",
                     "difficulty breathing", "fatigue", "rapid breathing"],
        "precautions": [
            "Always carry your rescue inhaler",
            "Avoid known triggers (dust, pollen, smoke)",
            "Use air purifiers indoors",
            "Follow your asthma action plan",
            "Get annual flu vaccination",
        ],
        "specialist": "Pulmonologist",
        "severity": "High",
    },
    "Dengue Fever": {
        "symptoms": ["high fever", "severe headache", "pain behind eyes", "joint pain",
                     "muscle pain", "rash", "nausea", "vomiting", "fatigue",
                     "bleeding gums", "easy bruising"],
        "precautions": [
            "Use mosquito repellent and wear protective clothing",
            "Stay hydrated and monitor platelet count",
            "Avoid aspirin and ibuprofen (use paracetamol only)",
            "Rest and avoid physical exertion",
            "Seek immediate care if bleeding occurs",
        ],
        "specialist": "Infectious Disease Specialist",
        "severity": "High",
    },
    "Anemia": {
        "symptoms": ["fatigue", "weakness", "pale skin", "shortness of breath",
                     "dizziness", "cold hands", "cold feet", "headache",
                     "irregular heartbeat", "chest pain"],
        "precautions": [
            "Eat iron-rich foods (spinach, red meat, lentils)",
            "Take prescribed iron or B12 supplements",
            "Avoid tea/coffee with meals (reduces iron absorption)",
            "Get regular blood count checks",
            "Treat underlying cause as directed by doctor",
        ],
        "specialist": "Hematologist",
        "severity": "Moderate",
    },
    "Acid Reflux (GERD)": {
        "symptoms": ["heartburn", "chest pain", "regurgitation", "difficulty swallowing",
                     "sour taste", "bloating", "nausea", "cough", "hoarseness"],
        "precautions": [
            "Avoid spicy, fatty, and acidic foods",
            "Eat smaller meals and avoid lying down after eating",
            "Elevate the head of your bed",
            "Avoid alcohol and caffeine",
            "Take antacids or prescribed medication",
        ],
        "specialist": "Gastroenterologist",
        "severity": "Low",
    },
    "Malaria": {
        "symptoms": ["high fever", "chills", "sweating", "headache", "nausea",
                     "vomiting", "muscle pain", "fatigue", "diarrhea"],
        "precautions": [
            "Take prescribed antimalarial medication immediately",
            "Use mosquito nets and repellents",
            "Stay hydrated",
            "Monitor for severe symptoms (confusion, seizures)",
            "Complete the full treatment course",
        ],
        "specialist": "Infectious Disease Specialist",
        "severity": "High",
    },
    "Arthritis": {
        "symptoms": ["joint pain", "joint swelling", "stiffness", "reduced range of motion",
                     "fatigue", "redness around joints", "warmth around joints"],
        "precautions": [
            "Apply hot or cold packs to affected joints",
            "Do low-impact exercises (swimming, walking)",
            "Take prescribed anti-inflammatory medication",
            "Maintain a healthy weight to reduce joint stress",
            "Use assistive devices if needed",
        ],
        "specialist": "Rheumatologist",
        "severity": "Moderate",
    },
    "Anxiety Disorder": {
        "symptoms": ["excessive worry", "restlessness", "fatigue", "difficulty concentrating",
                     "irritability", "muscle tension", "sleep problems", "rapid heartbeat",
                     "sweating", "trembling", "shortness of breath"],
        "precautions": [
            "Practice deep breathing and mindfulness daily",
            "Limit caffeine and alcohol intake",
            "Maintain a regular sleep schedule",
            "Exercise regularly to reduce stress hormones",
            "Seek therapy (CBT) or medication if symptoms persist",
        ],
        "specialist": "Psychiatrist",
        "severity": "Moderate",
    },
}

SEVERITY_COLOR = {
    "Low":      "success",
    "Moderate": "warning",
    "High":     "danger",
}

def predict(raw_input: str) -> dict | None:
    """
    Score each disease by counting how many of the user's symptoms
    appear in its symptom list. Return the best match with metadata.
    Returns None if no symptom matches at all.
    """
    # Normalise input into a list of cleaned tokens
    user_symptoms = [s.strip().lower() for s in raw_input.split(",") if s.strip()]
    if not user_symptoms:
        return None

    best_disease = None
    best_score   = 0
    best_matched = []

    for disease, data in DISEASE_DB.items():
        db_symptoms = [s.lower() for s in data["symptoms"]]
        matched = [s for s in user_symptoms
                   if any(s in db_s or db_s in s for db_s in db_symptoms)]
        score = len(matched) / len(db_symptoms)   # fraction of disease symptoms matched
        if score > best_score:
            best_score    = score
            best_disease  = disease
            best_matched  = matched

    if best_score == 0:
        return None

    data       = DISEASE_DB[best_disease]
    confidence = min(round(best_score * 100 * 1.5), 95)  # scale up slightly, cap at 95%
    severity   = data["severity"]

    return {
        "disease":     best_disease,
        "confidence":  confidence,
        "matched":     best_matched,
        "precautions": data["precautions"],
        "specialist":  data["specialist"],
        "severity":    severity,
        "color":       SEVERITY_COLOR[severity],
    }
