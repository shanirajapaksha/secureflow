# API Documentation - SecureFlow-AI Backend

Complete API reference for SecureFlow-AI backend.

---

## 🌐 Base URL

```
http://localhost:8000
```

---

## 📚 Interactive Documentation

Access interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔐 Authentication

Currently, no authentication is required. For production, consider adding:
- API keys
- JWT tokens
- OAuth 2.0

---

## 📡 Endpoints

### **1. Predict Intrusion**

Make predictions on network traffic data using the trained ML model.

#### **Request**

```http
POST /predict
Content-Type: multipart/form-data
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | CSV file with network traffic data |

#### **CSV Format Requirements**

The uploaded CSV should contain network flow features. Example columns:
- `Flow Duration`
- `Total Fwd Packets`
- `Total Bwd Packets`
- `Fwd Packet Length Mean`
- `Bwd Packet Length Mean`
- ... (84 features total in CICIDS2017 dataset)

**Note**: The backend handles feature selection and scaling automatically.

#### **Response**

**Status**: `200 OK`

```json
{
  "total_rows": 100,
  "summary": {
    "BENIGN": 90,
    "DoS": 5,
    "Probe": 3,
    "R2L": 1,
    "U2R": 1
  },
  "predictions": [
    {
      "Predicted_Label": "BENIGN",
      "Traffic_Status": "BENIGN"
    },
    {
      "Predicted_Label": "DoS",
      "Traffic_Status": "ATTACK"
    },
    {
      "Predicted_Label": "BENIGN",
      "Traffic_Status": "BENIGN"
    }
  ]
}
```

#### **Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `total_rows` | integer | Total number of rows processed |
| `summary` | object | Count of each attack type |
| `predictions` | array | Per-row predictions |
| `Predicted_Label` | string | Specific attack type or BENIGN |
| `Traffic_Status` | string | BENIGN or ATTACK (grouped) |

#### **Example - cURL**

```bash
# Simple prediction
curl -X POST "http://localhost:8000/predict" \
  -F "file=@network_data.csv"

# With pretty JSON output
curl -X POST "http://localhost:8000/predict" \
  -F "file=@network_data.csv" | python -m json.tool
```

#### **Example - Python**

```python
import requests

# Read CSV file
with open('network_data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/predict', files=files)

# Parse response
predictions = response.json()
print(f"Total rows: {predictions['total_rows']}")
print(f"Summary: {predictions['summary']}")
print(f"First prediction: {predictions['predictions'][0]}")
```

#### **Example - JavaScript/Fetch**

```javascript
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);

fetch('http://localhost:8000/predict', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Total rows:', data.total_rows);
  console.log('Summary:', data.summary);
  console.log('Predictions:', data.predictions);
});
```

#### **Error Responses**

**Status**: `400 Bad Request`
```json
{
  "error": "No file provided"
}
```

**Status**: `422 Unprocessable Entity`
```json
{
  "error": "Invalid file format. Expected CSV"
}
```

**Status**: `500 Internal Server Error`
```json
{
  "error": "Model prediction failed: [error details]"
}
```

---

## 🏥 Health Check (Optional)

**Endpoint**: `GET /` or `GET /health`

Useful for checking if the backend is running and model is loaded.

#### **Response**

```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

## 📊 Attack Types Classification

The model identifies the following attack types:

| Label | Type | Description |
|-------|------|-------------|
| `BENIGN` | Normal | Legitimate network traffic |
| `DoS` | Attack | Denial of Service attacks |
| `DDoS` | Attack | Distributed Denial of Service |
| `Probe` | Attack | Network reconnaissance/scanning |
| `R2L` | Attack | Remote to Local attacks |
| `U2R` | Attack | User to Root privilege escalation |

### **Attack Status Grouping**

- **BENIGN** → `Traffic_Status: "BENIGN"`
- All others → `Traffic_Status: "ATTACK"`

---

## 🔄 Data Flow

```
┌─────────────┐
│ CSV File    │ (Network flow data)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Validation      │ (Check format, columns)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Preprocessing   │ (Scaling, Feature Selection)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ ML Model        │ (Trained NIDS Model)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Predictions     │ (Labels for each row)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ JSON Response   │ (Return results)
└─────────────────┘
```

---

## ⚙️ Backend Configuration

### **Important Files**

| File | Purpose |
|------|---------|
| `app.py` | Main FastAPI application |
| `models/best_nids_model.joblib` | Trained ML model |
| `data/processed/preprocessing_artifacts.joblib` | Scaler, encoder, feature info |

### **Environment Variables** (Optional)

```env
# Set in .env at the repository root (see .env.example)
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:8080
MODEL_PATH=../models/best_nids_model.joblib
ARTIFACTS_PATH=../data/processed/preprocessing_artifacts.joblib
```

### **CORS Configuration**

Currently allows requests from all origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For production**, restrict to specific origins:
```python
allow_origins=[
    "http://localhost:8080",
    "https://yourdomain.com"
]
```

---

## 🧪 Testing the API

### **Test with Swagger UI**

1. Open http://localhost:8000/docs
2. Click on `/predict` endpoint
3. Click "Try it out"
4. Upload a CSV file
5. Click "Execute"

### **Test with cURL**

```bash
# Simple test
curl -X POST "http://localhost:8000/predict" \
  -F "file=@test_data.csv"

# With verbose output
curl -v -X POST "http://localhost:8000/predict" \
  -F "file=@test_data.csv"

# Save response to file
curl -X POST "http://localhost:8000/predict" \
  -F "file=@test_data.csv" > response.json
```

### **Test with Python**

```python
import requests
import json

# Make request
url = "http://localhost:8000/predict"
files = {'file': open('test_data.csv', 'rb')}

response = requests.post(url, files=files)
print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
```

### **Test with JavaScript**

```javascript
const testAPI = async () => {
  const formData = new FormData();
  formData.append('file', fileElement.files[0]);

  const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  console.log(data);
};

testAPI();
```

---

## 🔍 Response Examples

### **Example 1: Mixed Traffic**

```json
{
  "total_rows": 10,
  "summary": {
    "BENIGN": 6,
    "DoS": 3,
    "Probe": 1
  },
  "predictions": [
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "DoS", "Traffic_Status": "ATTACK"},
    {"Predicted_Label": "DoS", "Traffic_Status": "ATTACK"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "Probe", "Traffic_Status": "ATTACK"},
    {"Predicted_Label": "DoS", "Traffic_Status": "ATTACK"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"}
  ]
}
```

### **Example 2: All Benign Traffic**

```json
{
  "total_rows": 5,
  "summary": {
    "BENIGN": 5
  },
  "predictions": [
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"},
    {"Predicted_Label": "BENIGN", "Traffic_Status": "BENIGN"}
  ]
}
```

---

## ⚠️ Troubleshooting

### **"Model not found" Error**

**Cause**: Model files not in expected location.

**Solution**:
1. Check file exists: `ls models/best_nids_model.joblib`
2. Verify path in `app.py`
3. Ensure file is readable

### **"Invalid file format" Error**

**Cause**: CSV format not recognized.

**Solution**:
1. Save file as UTF-8 CSV
2. Ensure no special characters in headers
3. Use proper column names from CICIDS2017

### **"Prediction failed" Error**

**Cause**: Feature mismatch or invalid data.

**Solution**:
1. Check that CSV has required columns
2. Ensure numeric values (no text in data columns)
3. Check no NaN/NULL values

### **CORS Error in Browser**

**Cause**: Frontend-backend origin mismatch.

**Solution**:
1. Add frontend URL to `allow_origins` in `app.py`
2. Ensure frontend uses correct backend URL
3. Check browser console for exact error

---

## 📈 Performance

### **Typical Response Times**

| Request Size | Response Time |
|--------------|---------------|
| 100 rows | ~50-100ms |
| 1,000 rows | ~200-300ms |
| 10,000 rows | ~1-2s |
| 100,000 rows | ~5-10s |

*Times vary based on system specs and model complexity*

---

## 🔒 Security Considerations

### **Current Implementation**
- No authentication required
- CORS is restricted through the `ALLOWED_ORIGINS` setting
- CSV upload size, row count, and feature schema are validated
- Capture processing is limited to `.pcap`/`.pcapng` files inside `data/live`
- No rate limiting

### **Production Recommendations**
1. Add API authentication (JWT, API keys)
2. Implement rate limiting
3. Restrict CORS to known origins
4. Add request validation/sanitization
5. Implement logging and monitoring
6. Use HTTPS instead of HTTP

---

## 📞 Support

- **API Issues**: Check Swagger docs at `/docs`
- **Code**: Review `backend/app.py`
- **Questions**: See [README.md](./README.md)
- **Setup Help**: See [SETUP_GUIDE.md](./SETUP_GUIDE.md)

---

**Last Updated**: March 2026  
**API Version**: 1.0.0  
**Backend Version**: FastAPI 0.135.1
