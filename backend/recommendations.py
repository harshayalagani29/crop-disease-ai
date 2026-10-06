"""PLACEHOLDER guidance. Replace/verify with ICAR or state agriculture university advisories
before real use. Always encourage consulting a local agricultural officer."""

GENERAL = {
    "en": "This is a preliminary AI assessment and may be wrong. Please confirm with a local agricultural officer before applying any treatment.",
    "kn": "ಇದು ಪ್ರಾಥಮಿಕ AI ಮೌಲ್ಯಮಾಪನವಾಗಿದ್ದು ತಪ್ಪಾಗಿರಬಹುದು. ಯಾವುದೇ ಚಿಕಿತ್ಸೆ ಮಾಡುವ ಮೊದಲು ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ.",
}

HEALTHY = {
    "en": "The leaf looks healthy. Keep monitoring regularly and maintain good field hygiene.",
    "kn": "ಎಲೆ ಆರೋಗ್ಯವಾಗಿ ಕಾಣುತ್ತದೆ. ನಿಯಮಿತವಾಗಿ ಗಮನಿಸುತ್ತಿರಿ ಮತ್ತು ಹೊಲದ ಸ್ವಚ್ಛತೆ ಕಾಪಾಡಿ.",
}

DISEASE = {
    "en": {
        "Low": "Possible disease signs. Remove affected leaves, avoid overhead watering and monitor for 3-5 days.",
        "Medium": "Disease likely. Remove affected leaves, improve air flow, and consult an expert about suitable treatment.",
        "High": "High risk of spread. Isolate affected plants, avoid working in wet fields, and contact an agricultural officer soon.",
    },
    "kn": {
        "Low": "ರೋಗದ ಸಾಧ್ಯತೆ ಇದೆ. ಬಾಧಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ, ಮೇಲಿನಿಂದ ನೀರು ಹಾಕುವುದನ್ನು ತಪ್ಪಿಸಿ ಮತ್ತು 3-5 ದಿನ ಗಮನಿಸಿ.",
        "Medium": "ರೋಗ ಇರುವ ಸಾಧ್ಯತೆ ಹೆಚ್ಚು. ಬಾಧಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ, ಗಾಳಿ ಹರಿವು ಸುಧಾರಿಸಿ ಮತ್ತು ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "High": "ರೋಗ ಹರಡುವ ಅಪಾಯ ಹೆಚ್ಚು. ಬಾಧಿತ ಗಿಡಗಳನ್ನು ಪ್ರತ್ಯೇಕಿಸಿ, ಒದ್ದೆ ಹೊಲದಲ್ಲಿ ಕೆಲಸ ತಪ್ಪಿಸಿ ಮತ್ತು ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಶೀಘ್ರ ಸಂಪರ್ಕಿಸಿ.",
    },
}

def get(label: str, risk: str, lang: str = "en") -> str:
    lang = lang if lang in GENERAL else "en"
    body = HEALTHY[lang] if "healthy" in label.lower() else DISEASE[lang][risk]
    return f"{body} {GENERAL[lang]}"
