from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import xgboost as xgb
import pickle
import shap
import logging
import os
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def hash_api_key(key):
    return hashlib.sha256(key.encode()).hexdigest()

API_KEY = "12345-SECURE-KEY"
HASHED_API_KEY = hash_api_key(API_KEY)

db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keystrokeSpeed = db.Column(db.Float, nullable=False)
    mouseMovement = db.Column(db.Float, nullable=False)
    label = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

model_file = "xgboost_model.pkl"
if os.path.exists(model_file):
    try:
        with open(model_file, "rb") as f:
            model = pickle.load(f)
        logging.info("Loaded XGBoost model from disk.")
    except Exception as e:
        logging.error("Error loading model: %s", e)
        model = xgb.XGBClassifier()
else:
    model = xgb.XGBClassifier()
    model.fit(np.array([[0, 0], [1, 1]]), np.array([0, 1]))
    with open(model_file, "wb") as f:
        pickle.dump(model, f)
    logging.info("Initialized a new XGBoost model.")

def validate_data(keystrokeSpeed, mouseMovement, label=None):
    try:
        ks = float(keystrokeSpeed) if keystrokeSpeed is not None else None
        mm = float(mouseMovement) if mouseMovement is not None else None
    except ValueError:
        return False
    if ks is not None and not (0 <= ks <= 1000):
        return False
    if mm is not None and not (0 <= mm <= 5000):
        return False
    if label is not None and label not in [0, 1]:
        return False
    return True

def impute_missing_data(keystrokeSpeed, mouseMovement):
    feedback_entries = Feedback.query.all()
    if not feedback_entries:
        return keystrokeSpeed or 100, mouseMovement or 500
    ks_values = [entry.keystrokeSpeed for entry in feedback_entries if entry.keystrokeSpeed is not None]
    mm_values = [entry.mouseMovement for entry in feedback_entries if entry.mouseMovement is not None]
    ks_median = np.median(ks_values) if ks_values else 100
    mm_median = np.median(mm_values) if mm_values else 500
    return keystrokeSpeed or ks_median, mouseMovement or mm_median

@app.route('/xgboost-score', methods=['POST'])
def predict_risk():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload."}), 400
    keystrokeSpeed, mouseMovement = impute_missing_data(data.get("keystrokeSpeed"), data.get("mouseMovement"))
    features = np.array([[keystrokeSpeed, mouseMovement]])
    try:
        prob = model.predict_proba(features)[0][1]
    except Exception as e:
        logging.error("Prediction error: %s", e)
        return jsonify({"error": "Prediction failed."}), 500
    risk = "HIGH" if prob > 0.7 else "LOW"
    explainer = shap.Explainer(model)
    shap_values = explainer(features)
    feature_importance = dict(zip(["keystrokeSpeed", "mouseMovement"], shap_values.values[0]))
    return jsonify({"risk": risk, "score": prob, "explanation": feature_importance})

@app.route('/feedback', methods=['POST'])
def feedback():
    api_key = request.headers.get("API-Key")
    if not api_key or hash_api_key(api_key) != HASHED_API_KEY:
        return jsonify({"error": "Unauthorized access"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload."}), 400
    keystrokeSpeed, mouseMovement = impute_missing_data(data.get("keystrokeSpeed"), data.get("mouseMovement"))
    label = data.get("label")
    if not validate_data(keystrokeSpeed, mouseMovement, label):
        return jsonify({"error": "Invalid input values."}), 400
    feedback_entry = Feedback(keystrokeSpeed=keystrokeSpeed, mouseMovement=mouseMovement, label=int(label))
    db.session.add(feedback_entry)
    db.session.commit()
    X_feedback = np.array([[keystrokeSpeed, mouseMovement]])
    y_feedback = np.array([label])
    try:
        model.fit(X_feedback, y_feedback, xgb_model=model)
        with open(model_file, "wb") as f:
            pickle.dump(model, f)
        logging.info("Adaptive learning updated the model with new feedback.")
    except Exception as e:
        logging.error("Adaptive learning failed: %s", e)
    return jsonify({"message": "Feedback recorded and model updated adaptively."})

if __name__ == '__main__':
    app.run(port=5002, debug=False)
