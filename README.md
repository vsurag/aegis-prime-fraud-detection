# AEGIS PRIME | Real-Time AI Fraud Intelligence

AEGIS PRIME is an industry-standard, high-fidelity Fraud Detection System designed for real-time monitoring and analysis of financial transactions. It utilizes a dual-layer AI approach combining pattern-recognition classification with statistical anomaly detection.

## 🚀 Key Features
- **Real-Time Simulation**: Integrated behavioral generator mimicking complex human spending patterns.
- **Dual-Model Brain**: 
  - **Random Forest Classifier**: Trained with SMOTE for high-accuracy pattern recognition.
  - **Isolation Forest**: Statistical anomaly detector for "stealthy" fraud detection.
- **Cyber-Neon Dashboard**: 
  - **Behavioral Fingerprint**: Radar charts for multi-dimensional transaction analysis.
  - **Temporal Fraud Pulse**: Sunburst charts for merchant-location risk mapping.
  - **Network Risk Pressure**: Live volatility monitoring.
- **Enterprise Backend**: High-performance FastAPI engine for millisecond-latency predictions.

## 🛠️ Tech Stack
- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: Streamlit, Custom CSS
- **Machine Learning**: Scikit-Learn, Imbalanced-Learn (SMOTE)
- **Data & Viz**: Pandas, Plotly, NumPy

## 📂 Project Structure
- `app.py`: FastAPI Backend API.
- `dashboard.py`: Cyber-Neon Operational Frontend.
- `model.py`: Training pipeline (RF + ISO-F + SMOTE).
- `utils.py`: Behavioral simulation and preprocessing helpers.

## 🏃 How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Train the AI**:
   ```bash
   python model.py
   ```

3. **Start the Backend Engine**:
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8000
   ```

4. **Launch the Dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

---
*Built with AEGIS Intelligence Core v3.0*
