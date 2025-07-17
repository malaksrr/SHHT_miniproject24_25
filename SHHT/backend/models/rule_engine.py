# models/rule_engine.py

def classify_burnout(study_hours, sleep_hours, break_frequency, concentration_level):
    """
    Returns burnout level based on total risk score.
    """
    score = sum([
        study_hours > 8,
        sleep_hours < 6,
        break_frequency < 25,
        concentration_level < 3
    ]) * 2

    return (
        "🚨 High" if score >= 6 else
        "⚠️ Moderate" if score >= 3 else
        "✅ Low"
    )

def analyze_study_session(data):
    study_hours = data.get('study_hours', 0)
    sleep_hours = data.get('sleep_hours', 0)
    break_freq = data.get('break_frequency', 60)
    concentration = data.get('concentration_level', 3)

    warnings, recommendations = [], []

    # --- Study Hours ---
    if study_hours > 9:
        warnings.append("📚 Studying over 9 hours may lead to fatigue.")
        recommendations.append("📉 Try to limit study time to 8–9 hours.")
    elif study_hours < 3:
        recommendations.append("⏳ Try to study at least 4–6 hours if possible.")

    # --- Sleep Hours ---
    if sleep_hours < 5.5:
        warnings.append("😴 Less than 6 hours of sleep affects focus.")
        recommendations.append("🛌 Aim for at least 7–8 hours of sleep.")
    
    # --- Break Frequency ---
    if break_freq < 20:
        warnings.append("🔁 Too few breaks can reduce concentration.")
        recommendations.append("⏱️ Take short breaks every 30–45 minutes.")

    # --- Concentration Level ---
    if concentration <= 2:
        warnings.append("⚠️ Low concentration reported.")
        recommendations.append("📵 Minimize distractions or try a new study time.")
    elif concentration == 3:
        recommendations.append("📘 Average focus—short breaks may help.")

    # --- Combined Conditions ---
    if study_hours > 9 and sleep_hours < 6:
        warnings.append("⚠️ High study time and low sleep—risk of burnout.")
        recommendations.append("🛑 Prioritize sleep to recover well.")
    elif concentration < 3 and sleep_hours < 6:
        warnings.append("⚠️ Low focus & low sleep combined.")
        recommendations.append("💡 Try a nap or improve sleep routine.")

    burnout = classify_burnout(study_hours, sleep_hours, break_freq, concentration)

    return {
        "summary": {
            "burnout_risk": burnout,
            "status": {
                "✅ Low": "You're doing great! Keep your routine balanced.",
                "⚠️ Moderate": "Some signs of stress. Small tweaks can help.",
                "🚨 High": "Risk detected. Review your habits soon."
            }[burnout]
        },
        "warnings": warnings,
        "recommendations": recommendations
    }
