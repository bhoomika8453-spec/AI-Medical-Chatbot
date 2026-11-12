"""
chat_engine.py — Conversational AI brain for the medical chatbot.
No external ML libraries required.
"""

from predictor import predict, DISEASE_DB

# ── Emergency keywords ────────────────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "can't breathe", "cannot breathe", "not breathing", "heart attack",
    "stroke", "unconscious", "unresponsive", "severe chest pain",
    "crushing chest", "coughing blood", "vomiting blood", "seizure",
    "convulsion", "overdose", "suicide", "kill myself", "poisoning",
    "severe bleeding", "won't stop bleeding", "paralysis", "collapsed",
    "passing out", "fainted", "anaphylaxis", "allergic reaction severe",
]

# ── Medicine / drug precaution knowledge base ─────────────────────────────────
MEDICINE_INFO = {
    "paracetamol": {
        "use": "Fever, mild to moderate pain",
        "precautions": ["Do not exceed 4g/day", "Avoid alcohol", "Caution in liver disease"],
        "avoid": "Liver disease, heavy alcohol use",
    },
    "ibuprofen": {
        "use": "Pain, inflammation, fever",
        "precautions": ["Take with food", "Avoid on empty stomach", "Not for kidney disease"],
        "avoid": "Peptic ulcer, kidney disease, pregnancy (3rd trimester)",
    },
    "amoxicillin": {
        "use": "Bacterial infections",
        "precautions": ["Complete full course", "Check for penicillin allergy", "May cause diarrhea"],
        "avoid": "Penicillin allergy",
    },
    "metformin": {
        "use": "Type 2 diabetes",
        "precautions": ["Take with meals", "Monitor kidney function", "Avoid alcohol"],
        "avoid": "Kidney disease, liver disease",
    },
    "aspirin": {
        "use": "Pain, fever, blood thinning",
        "precautions": ["Not for children under 16", "Take with food", "Risk of bleeding"],
        "avoid": "Children, peptic ulcer, bleeding disorders",
    },
    "omeprazole": {
        "use": "Acid reflux, GERD, stomach ulcers",
        "precautions": ["Take 30 min before meals", "Long-term use may affect magnesium levels"],
        "avoid": "Hypersensitivity to proton pump inhibitors",
    },
    "cetirizine": {
        "use": "Allergies, hay fever, hives",
        "precautions": ["May cause drowsiness", "Avoid driving", "Avoid alcohol"],
        "avoid": "Severe kidney disease",
    },
    "salbutamol": {
        "use": "Asthma, bronchospasm",
        "precautions": ["Shake inhaler before use", "Rinse mouth after use", "Do not overuse"],
        "avoid": "Hypersensitivity to salbutamol",
    },
}

# ── Flat symptom list from predictor for detection ───────────────────────────
ALL_SYMPTOMS = sorted({s for d in DISEASE_DB.values() for s in d["symptoms"]})

# ── Intent patterns ───────────────────────────────────────────────────────────
GREETING_WORDS   = {"hi", "hello", "hey", "good morning", "good evening", "good afternoon", "howdy"}
THANKS_WORDS     = {"thanks", "thank you", "thank", "thx", "ty"}
BYE_WORDS        = {"bye", "goodbye", "see you", "exit", "quit"}
APPT_WORDS       = {"appointment", "book", "schedule", "doctor visit", "consult"}
MEDICINE_WORDS   = {"medicine", "medication", "drug", "tablet", "pill", "dose", "paracetamol",
                    "ibuprofen", "amoxicillin", "metformin", "aspirin", "omeprazole",
                    "cetirizine", "salbutamol"}
HISTORY_WORDS    = {"history", "previous", "past symptoms", "what did i say", "my symptoms"}

# ── Conversational fillers ────────────────────────────────────────────────────
GREET_REPLIES = [
    "Hello! 👋 I'm MediBot, your AI health assistant. Tell me your symptoms and I'll help you understand what might be going on.",
    "Hi there! I'm MediBot. Describe your symptoms and I'll suggest possible conditions, precautions, and the right specialist for you.",
    "Hey! Good to see you. Share your symptoms and I'll do my best to help. Remember, I'm not a substitute for a real doctor!",
]

THANKS_REPLIES = [
    "You're welcome! Stay healthy. 💊 Let me know if you have more symptoms.",
    "Happy to help! Don't forget to consult a real doctor for a proper diagnosis.",
    "Anytime! Take care of yourself. 🌿",
]

BYE_REPLIES = [
    "Take care! Remember to consult a doctor if symptoms persist. 👨‍⚕️",
    "Goodbye! Stay healthy and hydrated. 💧",
    "See you! Book an appointment if you need professional help.",
]

FALLBACK_REPLIES = [
    "I'm not sure I understood that. Could you describe your symptoms? For example: 'I have fever, headache and fatigue'.",
    "Could you tell me more about how you're feeling? List your symptoms separated by commas.",
    "I'm here to help with medical questions. Please describe your symptoms or ask about a medicine.",
]

import random

def _classify_intent(text: str) -> str:
    t = text.lower().strip()
    words = set(t.split())

    if any(kw in t for kw in EMERGENCY_KEYWORDS):
        return "emergency"
    if words & GREETING_WORDS or t in GREETING_WORDS:
        return "greeting"
    if words & THANKS_WORDS:
        return "thanks"
    if words & BYE_WORDS:
        return "bye"
    if words & APPT_WORDS:
        return "appointment"
    if words & MEDICINE_WORDS:
        return "medicine"
    if words & HISTORY_WORDS:
        return "history"

    # Check if any known symptom appears in the text
    detected = _detect_symptoms(t)
    if detected:
        return "symptom"

    return "smalltalk"


def _detect_symptoms(text: str) -> list[str]:
    """Return all known symptoms found in the free-text message."""
    t = text.lower()
    found = []
    for s in ALL_SYMPTOMS:
        if s in t:
            found.append(s)
    return found


def _medicine_reply(text: str) -> dict:
    t = text.lower()
    for drug, info in MEDICINE_INFO.items():
        if drug in t:
            lines = [
                f"<b>{drug.capitalize()}</b>",
                f"<b>Used for:</b> {info['use']}",
                "<b>Precautions:</b><ul>" +
                "".join(f"<li>{p}</li>" for p in info["precautions"]) + "</ul>",
                f"<b>Avoid if:</b> {info['avoid']}",
            ]
            return {
                "intent": "medicine",
                "text": "\n".join(lines),
                "drug": drug,
            }
    # Generic medicine query
    known = ", ".join(MEDICINE_INFO.keys())
    return {
        "intent": "medicine",
        "text": (f"I have precaution info for: <b>{known}</b>. "
                 "Which medicine would you like to know about?"),
    }


def _symptom_reply(text: str, prior_symptoms: list[str]) -> dict:
    """Run prediction and build a rich structured reply."""
    detected = _detect_symptoms(text)

    # Merge with prior symptoms from this session for better accuracy
    combined = list(dict.fromkeys(prior_symptoms + detected))  # deduplicated, ordered
    combined_str = ", ".join(combined)

    result = predict(combined_str) if combined else None

    if not result:
        return {
            "intent": "symptom",
            "text": ("I noticed some symptoms but couldn't match a specific condition. "
                     "Please add more details or <a href='/appointments/book'>book an appointment</a>."),
            "symptoms_detected": detected,
        }

    severity_emoji = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}.get(result["severity"], "⚪")

    precaution_html = "<ul>" + "".join(f"<li>{p}</li>" for p in result["precautions"]) + "</ul>"

    text_parts = [
        f"Based on your symptoms, this could be <b>{result['disease']}</b> "
        f"{severity_emoji} <span class='badge bg-{result['color']}'>{result['severity']} severity</span> "
        f"— <b>{result['confidence']}% confidence</b>.",
        "",
        f"<b>Matched symptoms:</b> {', '.join(result['matched']) or 'none'}.",
        "",
        f"<b>Recommended precautions:</b>{precaution_html}",
        f"<b>Suggested specialist:</b> 👨‍⚕️ <b>{result['specialist']}</b>",
    ]

    if len(combined) > len(detected):
        text_parts.append(
            f"<small class='text-muted'>ℹ️ Analysis includes your earlier symptoms: "
            f"{', '.join(prior_symptoms)}.</small>"
        )

    return {
        "intent":            "symptom",
        "text":              "\n".join(text_parts),
        "disease":           result["disease"],
        "confidence":        result["confidence"],
        "severity":          result["severity"],
        "severity_color":    result["color"],
        "specialist":        result["specialist"],
        "symptoms_detected": detected,
        "all_symptoms":      combined,
    }


def process(message: str, prior_symptoms: list[str]) -> dict:
    """
    Main entry point.
    Returns a dict with at minimum: intent, text, symptoms_detected (list).
    """
    intent = _classify_intent(message)

    if intent == "emergency":
        return {
            "intent": "emergency",
            "text": (
                "🚨 <b>EMERGENCY DETECTED</b> 🚨<br>"
                "Please call emergency services <b>immediately (911 / 112)</b>.<br>"
                "Do not wait — go to the nearest emergency room or call an ambulance now.<br>"
                "<a href='/emergency' class='btn btn-danger btn-sm mt-2'>"
                "<i class='bi bi-hospital'></i> Find Nearest Hospital</a>"
            ),
            "symptoms_detected": [],
            "is_emergency": True,
        }

    if intent == "greeting":
        return {"intent": "greeting", "text": random.choice(GREET_REPLIES), "symptoms_detected": []}

    if intent == "thanks":
        return {"intent": "thanks", "text": random.choice(THANKS_REPLIES), "symptoms_detected": []}

    if intent == "bye":
        return {"intent": "bye", "text": random.choice(BYE_REPLIES), "symptoms_detected": []}

    if intent == "appointment":
        return {
            "intent": "appointment",
            "text": ("I can help you book an appointment! "
                     "<a href='/appointments/book' class='btn btn-primary btn-sm ms-2'>"
                     "<i class='bi bi-calendar-plus'></i> Book Now</a>"),
            "symptoms_detected": [],
        }

    if intent == "medicine":
        return _medicine_reply(message)

    if intent == "history":
        if prior_symptoms:
            return {
                "intent": "history",
                "text": (f"Your reported symptoms this session: "
                         f"<b>{', '.join(prior_symptoms)}</b>. "
                         f"<a href='/predict'>Run full prediction →</a>"),
                "symptoms_detected": [],
            }
        return {
            "intent": "history",
            "text": "No symptoms recorded yet in this session. Tell me how you're feeling!",
            "symptoms_detected": [],
        }

    if intent == "symptom":
        return _symptom_reply(message, prior_symptoms)

    # smalltalk / fallback
    return {"intent": "smalltalk", "text": random.choice(FALLBACK_REPLIES), "symptoms_detected": []}
