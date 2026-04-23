import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from utils import generate_bulk_data, preprocess_df

def train_models():
    # 1. Generate Data
    print("Generating bulk data for training...")
    df = generate_bulk_data(10000)
    
    # 2. Preprocess Data
    X = df.drop('Class', axis=1)
    y = df['Class']
    
    X_processed, le_dict, scaler = preprocess_df(X)
    
    # 3. Handle Imbalance using SMOTE
    print("Handling imbalance using SMOTE...")
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X_processed, y)
    
    # 4. Train Models
    X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)
    
    # Logistic Regression
    print("Training Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train, y_train)
    
    # Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Anomaly Detection (Isolation Forest)
    print("Training Isolation Forest for anomaly detection...")
    # Isolation Forest is trained only on "Genuine" data or bulk data for anomalies
    iso_forest = IsolationForest(contamination=0.02, random_state=42)
    iso_forest.fit(X_processed)
    
    # Evaluate RF (Main Model)
    y_pred = rf_model.predict(X_test)
    print("\nRandom Forest Evaluation:")
    print(classification_report(y_test, y_pred))
    
    # Create models directory
    if not os.path.exists('models'):
        os.makedirs('models')
        
    # 5. Save Models and Encoders
    joblib.dump(rf_model, 'models/rf_model.pkl')
    joblib.dump(lr_model, 'models/lr_model.pkl')
    joblib.dump(iso_forest, 'models/iso_forest.pkl')
    joblib.dump(le_dict, 'models/le_dict.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    
    print("\nModels and preprocessing objects saved to 'models/' directory.")

if __name__ == "__main__":
    train_models()
