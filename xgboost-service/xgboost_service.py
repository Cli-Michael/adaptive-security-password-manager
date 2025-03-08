from flask import Flask, request, jsonify
import xgboost as xgb
import numpy as np
import os

app = Flask(__name__)

MODEL_PATH = "xgb_model.json"


def train_dummy_model():
    # Create dummy training data
    # Features: keystrokeSpeed, mouseMovement, geoLocation
    X = np.array([
        [100, 20, 50],
        [110, 25, 55],
        [90, 18, 48],
        [130, 35, 70],
        [80, 15, 40]
    ])
    y = np.array([0, 0, 0, 1, 1])  # 0: low risk, 1: high risk
    
    dtrain = xgb.DMatrix(X, label=y)
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'logloss'
    }
    num_round = 10
    bst = xgb.train(params, dtrain, num_round)
    bst.save_model(MODEL_PATH)
    return bst

if os.path.exists(MODEL_PATH):
    model = xgb.Booster()
    model.load_model(MODEL_PATH)
else:
    model = train_dummy_model()

@app.route('/xgboost-score', methods=['POST'])
def xgboost_score():
    data = request.json
    # Expecting keys: keystrokeSpeed, mouseMovement, geoLocation
    features = np.array([[data['keystrokeSpeed'], data['mouseMovement'], data['geoLocation']]])
    dmatrix = xgb.DMatrix(features)
    prediction = model.predict(dmatrix)[0]
    risk = "HIGH" if prediction > 0.5 else "LOW"
    return jsonify({'risk': risk, 'score': float(prediction)})

if __name__ == '__main__':
    app.run(port=5002)
