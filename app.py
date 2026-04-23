from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from utils import preprocess_df
import os

app = FastAPI(title="Aegis - Fraud Intelligence API", version="3.0.0")

# 1. Load models and encoders
try:
    rf_model = joblib.load('models/rf_model.pkl')
    iso_forest = joblib.load('models/iso_forest.pkl')
    le_dict = joblib.load('models/le_dict.pkl')
    scaler = joblib.load('models/scaler.pkl')
except Exception as e:
    print(f"Error loading models: {e}. Run model.py first.")
    # Fallback to avoid crashes during startup if models don't exist yet
    rf_model = None
    iso_forest = None
    le_dict = None
    scaler = None

# 2. Pydantic Model for incoming transaction data
class Transaction(BaseModel):
    Time: float
    Amount: float
    Location: str
    MerchantType: str
    SpendingHabit: str
    Avg30dAmount: float
    Velocity24h: int
    DistanceFromHome: float
    IsNewDevice: int
    IsOnline: int
    IsLateNight: int
    FailedAttempts: int
    Threshold: float = 0.5 # Optional threshold tuning

@app.get("/")
def home():
    return {"message": "Aegis API is live."}

@app.post("/predict")
def predict_fraud(transaction: Transaction):
    if rf_model is None:
        raise HTTPException(status_code=500, detail="Models not found. Train models first.")
    
    # Convert transaction data to DataFrame
    data_dict = transaction.dict()
    threshold = data_dict.pop('Threshold')
    df = pd.DataFrame([data_dict])
    
    # 3. Preprocess incoming data
    X_processed, _, _ = preprocess_df(df, le_dict=le_dict, scaler=scaler)
    
    # 4. Predict (Random Forest)
    # Predict probabilities for fraud (class 1)
    probs = rf_model.predict_proba(X_processed)[0]
    fraud_prob = probs[1]
    
    # Decision based on threshold
    prediction = 1 if fraud_prob >= threshold else 0
    
    # 5. Anomaly Detection (Isolation Forest)
    # Isolation Forest returns -1 for anomalies, 1 for normal
    iso_score = iso_forest.decision_function(X_processed)[0] # Low score = anomaly
    is_anomaly = True if iso_score < 0 else False
    
    # 6. Combined Risk Score
    # We combine model probability with anomaly score for a more dynamic range
    # Normalize anomaly score to 0-1 range (approx) where 1 is anomaly
    normalized_anomaly_score = 1 / (1 + np.exp(iso_score * 5))
    
    # Final Risk Score is a weighted average
    risk_score = (fraud_prob * 0.7 + normalized_anomaly_score * 0.3) * 100
    
    if risk_score > 70 or is_anomaly:
        risk_level = "High"
    elif risk_score > 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"
        
    return {
        "prediction": "Fraud" if prediction == 1 else "Genuine",
        "fraud_probability": round(fraud_prob, 4),
        "is_anomaly": is_anomaly,
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
