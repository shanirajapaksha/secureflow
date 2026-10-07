# SecureFlow-AI: Network Intrusion Detection System (NIDS)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-green)
![React](https://img.shields.io/badge/React-18%2B-61dafb)
![TypeScript](https://img.shields.io/badge/TypeScript-Latest-blue)

##  Project Overview

**SecureFlow-AI** is an advanced AI-powered Network Intrusion Detection System (NIDS) that uses machine learning to identify and classify network traffic anomalies and cyber threats in real-time.

### Key Features:
-  **ML-Based Detection**: Uses trained models to identify intrusions
-  **Interactive Dashboard**: Real-time visualization of network threats
-  **Attack Classification**: Categorizes different attack types
-  **Performance Metrics**: Comprehensive evaluation reports
-  **REST API**: Full-featured backend API
-  **Real-Time Capture**: Wireshark/TShark capture with CICFlowMeter flow extraction
-  **Production Ready**: Scalable architecture

---

##  Tech Stack

### **Frontend**
- React 18 with TypeScript
- Vite (Fast build tool)
- Tailwind CSS (Styling)
- Shadcn UI (Component library)
- Chart.js (Data visualization)

### **Backend**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Pandas & NumPy (Data processing)
- Scikit-learn (Machine Learning)
- Joblib (Model serialization)

### **Data Science**
- Jupyter Notebooks
- Scikit-learn (ML models)
- CICIDS2017 Dataset

---

##  Project Structure

`
SecureFlow-AI-main/
 backend/                      # FastAPI backend
    app.py                   # Main FastAPI application
 frontend/                     # React frontend
    src/
       components/          # React components
       pages/               # Page components
       lib/                 # Utilities
    vite.config.ts
    package.json
 models/                      # Pre-trained ML models
    best_nids_model.joblib
 data/                        # Data directory
    raw/                     # Original datasets
    processed/               # Preprocessed data
    predictions/             # Model predictions
    evaluation/              # Metrics & reports
 notebooks/                   # Jupyter notebooks
    01.download_dataset.ipynb
    02.clean_dataset.ipynb
    03.preprocess_dataset.ipynb
    04.train_model.ipynb
    05.predict_intrusion.ipynb
    06.evaluate_best_model.ipynb
 requirements.txt             # Python dependencies
 README.md                    # This file
`

---

##  Quick Start

### **Prerequisites**
- Python 3.9+
- Node.js 16+
- npm or bun

### **Installation**

#### 1. **Clone the Repository**
`ash
git clone https://github.com/yourusername/SecureFlow-AI.git
cd SecureFlow-AI-main
`

#### 2. **Backend Setup**
`ash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install runtime dependencies
pip install -r requirements.txt

# Optional: install tests and notebook/model development tools
pip install -r requirements-test.txt
# pip install -r requirements-dev.txt
`

#### 3. **Frontend Setup**
`ash
cd ../frontend

# Install dependencies
npm install
`

---

##  Running the Project

### **Start Backend**
`ash
# Run from the repository root
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
`

Backend runs at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs

### **Start Frontend**
`ash
cd frontend
npm run dev
`

Frontend runs at: **http://localhost:8080**

### **Configuration**

Copy `.env.example` to `.env` for backend settings. Copy
`frontend/.env.example` to `frontend/.env` to change the frontend API URL.

### **Run Tests and Checks**

```bash
python -m pytest -q
cd frontend
npm run lint
npm run build
```

---

##  API Documentation

### **Base URL**: http://localhost:8000

### **Endpoints**

#### **1. Predict Intrusion**
`http
POST /predict
Content-Type: multipart/form-data

Body: file (CSV format)
`

**Example Request:**
`ash
curl -X POST  http://localhost:8000/predict \
  -F file=@network_data.csv
`

**Example Response:**
`json
{
  total_rows: 100,
  summary: {
    BENIGN: 95,
    DoS: 3,
    Probe: 2
  },
  predictions: [
    {Predicted_Label: BENIGN, Traffic_Status: BENIGN},
    {Predicted_Label: DoS, Traffic_Status: ATTACK}
  ]
}
`

---

##  Dashboard Features

-  **Network Traffic Analysis**: Real-time traffic visualization
-  **Threat Alerts**: Alert management and history
-  **Geographic Map**: Threat distribution map
-  **Attack Types Chart**: Attack classification breakdown
-  **Statistics Cards**: Key metrics and KPIs
-  **Capture Controls**: Interface selection, timed capture, start/stop, status, and live alert polling

---

##  Data Pipeline

### **Workflow:**
1. **Download** - Fetch CICIDS2017 dataset
2. **Clean** - Handle missing values and duplicates
3. **Preprocess** - Feature scaling and encoding
4. **Train** - Train ML models
5. **Evaluate** - Assess performance
6. **Predict** - Make predictions

### **Run Notebooks:**
`ash
cd notebooks
jupyter notebook
`

Run notebooks in order: 01  02  03  04  05  06

---

##  Dataset Information

- **Dataset**: CICIDS2017 (Canadian Institute for Cybersecurity)
- **Records**: ~2.8M network flows
- **Features**: 84 network flow features
- **Classes**: 15 types (BENIGN + 14 attack types)

### **Attack Types**
- DoS (Denial of Service)
- Probe (Network Reconnaissance)
- R2L (Remote to Local)
- U2R (User to Root)
- BENIGN (Normal Traffic)

---

##  Model Information

### **Pre-trained Model**
- **Location**: models/best_nids_model.joblib
- **Type**: Ensemble/XGBoost
- **Accuracy**: ~95%+ (check evaluation reports)

### **Evaluation Reports**
See data/evaluation/ directory:
- classification_report.csv - Precision, Recall, F1-Score
- overall_metrics.csv - Overall accuracy
- label_wise_metrics.csv - Per-class metrics

---

##  Contributing

1. **Create a branch**: git checkout -b feature/your-feature
2. **Make changes** and commit
3. **Push**: git push origin feature/your-feature
4. **Create Pull Request**

---

##  Troubleshooting

### **Backend: Port 8000 already in use**
`ash
python -m uvicorn backend.app:app --port 8001
`

### **Backend: Model not found**
Ensure these files exist:
- models/best_nids_model.joblib
- data/processed/preprocessing_artifacts.joblib

### **Frontend: npm permission error**
`ash
sudo chown -R desktop-he9lado\hp ~/.npm
npm install
`

---

##  Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Scikit-learn Guide](https://scikit-learn.org/)
- [CICIDS2017 Dataset](https://www.unb.ca/cic/datasets/ids-2017.html)

---

##  Team Members

| Role | Responsibility |
|------|-----------------|
| Lead Developer | Backend architecture & API |
| Frontend Developer | UI/Dashboard |
| Data Scientist | ML models & evaluation |
| DevOps Engineer | Deployment & monitoring |

---

##  Support

- **Issues**: GitHub Issues
- **Email**: your-email@example.com
- **Documentation**: See README sections above

---

##  Roadmap

- [ ] Real-time streaming data processing
- [ ] Deep Learning models (LSTM, CNN)
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Mobile app for alerts
- [ ] Advanced threat intelligence

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**License**: MIT

---

Made with  by SecureFlow-AI Team
