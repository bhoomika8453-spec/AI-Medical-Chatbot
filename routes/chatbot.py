from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ChatMessage
from chat_engine import process

chatbot_bp = Blueprint("chatbot", __name__)


def _session_symptoms(user_id: int) -> list[str]:
    """Collect all unique symptoms detected across the current user's chat history."""
    rows = ChatMessage.query.filter_by(user_id=user_id).all()
    seen, result = set(), []
    for row in rows:
        if row.symptoms_detected:
            for s in row.symptoms_detected.split(","):
                s = s.strip()
                if s and s not in seen:
                    seen.add(s)
                    result.append(s)
    return result


@chatbot_bp.route("/")
@login_required
def chat():
    history  = (ChatMessage.query
                .filter_by(user_id=current_user.id)
                .order_by(ChatMessage.timestamp)
                .all())
    symptoms = _session_symptoms(current_user.id)
    return render_template("chatbot/chat.html", history=history, session_symptoms=symptoms)


@chatbot_bp.route("/send", methods=["POST"])
@login_required
def send():
    data    = request.get_json()
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "empty"}), 400

    prior    = _session_symptoms(current_user.id)
    result   = process(message, prior)

    symptoms_str = ",".join(result.get("symptoms_detected") or [])

    record = ChatMessage(
        user_id           = current_user.id,
        message           = message,
        response          = result["text"],
        intent            = result.get("intent"),
        symptoms_detected = symptoms_str,
    )
    db.session.add(record)
    db.session.commit()

    # Updated symptom list after this turn
    updated_symptoms = _session_symptoms(current_user.id)

    return jsonify({
        "response":         result["text"],
        "intent":           result.get("intent"),
        "is_emergency":     result.get("is_emergency", False),
        "disease":          result.get("disease"),
        "confidence":       result.get("confidence"),
        "severity":         result.get("severity"),
        "severity_color":   result.get("severity_color"),
        "specialist":       result.get("specialist"),
        "symptoms_detected": result.get("symptoms_detected", []),
        "session_symptoms": updated_symptoms,
    })


@chatbot_bp.route("/clear", methods=["POST"])
@login_required
def clear():
    ChatMessage.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"status": "cleared"})
