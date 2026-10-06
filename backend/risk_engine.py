"""Simple, explainable rule-based risk scoring. Tune thresholds with an expert."""

def is_healthy(label: str) -> bool:
    return "healthy" in label.lower()

def assess(label: str, confidence: float, humidity=None, rain_prob=None) -> dict:
    reasons = []
    if is_healthy(label):
        return {"risk": "Low", "reasons": ["Leaf appears healthy."]}

    score = 0
    if confidence >= 0.85:
        score += 2; reasons.append("High model confidence in disease detection.")
    elif confidence >= 0.60:
        score += 1; reasons.append("Moderate model confidence in disease detection.")
    if humidity is not None and humidity > 80:
        score += 2; reasons.append(f"High humidity ({humidity:.0f}%) favours fungal spread.")
    if rain_prob is not None and rain_prob > 60:
        score += 1; reasons.append(f"High chance of rain ({rain_prob:.0f}%).")
    if humidity is None and rain_prob is None:
        reasons.append("Weather data unavailable: risk based on image only.")

    risk = "High" if score >= 4 else "Medium" if score >= 2 else "Low"
    return {"risk": risk, "reasons": reasons}
