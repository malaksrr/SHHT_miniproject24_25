from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from models import rule_engine
from models.burnout_model import predict_burnout
from database import save_study_session, get_user_sessions, clear_user_history
import sqlite3
from database import init_db

from dotenv import load_dotenv
import os
from openai import OpenAI

# --- Load Environment ---
load_dotenv()
#client = OpenAI(api_key="sk-proj-cJaruE5CV5A7ORT_bLIQe12PLnT0_a5rc4ZZc4FJRgMf6eNwJjMa2jjJIlHI6_-4swjEzHM9_GT3BlbkFJNUzyH7WZUGiz8WwwkOemD__1MEtEoQQI21WsHYMnVpq-ODqyNJSBDBfvL51Z6qGCMDY-tJtEI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
init_db()
DB_PATH = "study_habits.db"

app = Flask(__name__)
CORS(app, resources={
    r"/analyze": {"origins": "http://localhost:3000"},
    r"/history": {"origins": "http://localhost:3000"},
    r"/clear-history": {"origins": "http://localhost:3000"}
})

def get_chatgpt_advice(input_data, rule_result, ml_result):
    try:
        prompt = (
            f"Student Data:\n"
            f"- Study Hours: {input_data.get('study_hours')}\n"
            f"- Sleep Hours: {input_data.get('sleep_hours')}\n"
            f"- Break Frequency: {input_data.get('break_frequency')} min\n"
            f"- Concentration: {input_data.get('concentration_level')}/5\n\n"
            f"Rule-based Output:\n"
            f"- Warnings: {rule_result.get('warnings')}\n"
            f"- Recommendations: {rule_result.get('recommendations')}\n\n"
            f"ML Predicted Burnout Risk: {ml_result.get('risk_score', 0):.1f}%\n\n"
            f"Give brief, motivational, and actionable advice (2–3 sentences) to help improve their study habits."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful study coach."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ ChatGPT error: {str(e)}"

# --- ROUTES ---
@app.route('/usernames', methods=['GET'])
def get_usernames():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT username FROM study_sessions ORDER BY username")
        usernames = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"status": "success", "data": usernames})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        if not data.get('username'):
            return jsonify({"error": "Username is required"}), 400

        ml_result = {
            "risk_score": 0.0,
            "model_version": "2.1",
            "error": None
        }
        rule_result = {
            "warnings": [],
            "recommendations": []
        }

        rule_result = rule_engine.analyze_study_session(data)

        try:
            ml_result = predict_burnout(data)
            risk_score = ml_result.get("risk_score", 0)

            if risk_score > 70:
                rule_result["recommendations"].append(
                    f"🚨 Critical burnout risk ({risk_score:.1f}%). Consider immediate rest and consultation."
                )
            elif risk_score > 50:
                rule_result["recommendations"].append(
                    f"⚠️ High burnout risk ({risk_score:.1f}%). Schedule downtime soon."
                )
        except Exception as e:
            ml_result["error"] = str(e)

        combined_recommendations = list(set(rule_result["recommendations"]))

        # 💬 Get ChatGPT Advice
        chatgpt_advice = get_chatgpt_advice(data, rule_result, ml_result)

        # Save to DB
        db_data = {
            "username": data['username'],
            "study_hours": data.get("study_hours", 0),
            "sleep_hours": data.get("sleep_hours", 0),
            "break_frequency": data.get("break_frequency", 0),
            "concentration_level": data.get("concentration_level", 0),
            "risk_score": ml_result.get("risk_score")
        }
        save_study_session(db_data)

        return jsonify({
            "status": "success",
            "input_data": data,
            "rule_based_analysis": rule_result,
            "ml_prediction": ml_result,
            "recommendations": combined_recommendations,
            "chatgpt_advice": chatgpt_advice
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "ml_prediction": {
                "risk_score": 0.0,
                "error": str(e)
            }
        }), 500


@app.route('/history', methods=['GET'])
def get_history():
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({"error": "Username is required"}), 400
        range_param = request.args.get('range', 'week')
        sessions = get_user_sessions(username, range_param)

        return jsonify({
            "status": "success",
            "username": username,
            "count": len(sessions),
            "data": sessions
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/clear-history', methods=['DELETE'])
def clear_history_route():
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({"error": "Username is required"}), 400
        time_range = request.args.get('range', 'all')
        deleted_count = clear_user_history(username, time_range)

        return jsonify({
            "status": "success",
            "username": username,
            "message": f"History cleared successfully for range: {time_range}",
            "deleted_count": deleted_count,
            "range": time_range
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
