# Setup Guide - SecureFlow-AI

Complete step-by-step guide for setting up the SecureFlow-AI project on your machine.

## ✅ Pre-Requirements Check

Before starting, ensure you have:

- [ ] **Python 3.9 or higher** - [Download](https://www.python.org/downloads/)
  ```bash
  python --version
  ```

- [ ] **Node.js 16 or higher** - [Download](https://nodejs.org/)
  ```bash
  node --version
  npm --version
  ```

- [ ] **Git** - [Download](https://git-scm.com/)
  ```bash
  git --version
  ```

---

## 📥 Clone Repository

```bash
# Clone the project
git clone https://github.com/yourusername/SecureFlow-AI.git

# Navigate to project
cd SecureFlow-AI-main

# Verify structure
ls -la  # On macOS/Linux
dir    # On Windows
```

---

## 🔧 Backend Setup (Python)

### **Step 1: Navigate to Backend**
```bash
# Stay in the repository root for backend commands
```

### **Step 2: Create Virtual Environment**

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **Step 3: Verify Activation**
Your terminal should show `(venv)` prefix.

### **Step 4: Install Dependencies**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Troubleshooting:**
- If you get `Microsoft Visual C++ 14.0 is required`, install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- If specific package fails, try: `pip install --only-binary :all: package-name`

### **Step 5: Verify Installation**
```bash
# Check if FastAPI is installed
python -c "import fastapi; print(fastapi.__version__)"

# Check if scikit-learn is installed
python -c "import sklearn; print(sklearn.__version__)"
```

---

## 🎨 Frontend Setup (Node.js)

### **Step 1: Navigate to Frontend**
```bash
cd ../frontend
```

### **Step 2: Install Dependencies**

**Using npm:**
```bash
npm install
```

**Using bun (faster):**
```bash
bun install
```

**Troubleshooting:**
- If npm error: Clear cache with `npm cache clean --force`
- If permission error: `sudo chown -R $(whoami) ~/.npm`

### **Step 3: Verify Installation**
```bash
npm --version
npm list react
```

---

## 🚀 Running the Application

### **Option A: Run in Development Mode**

**Terminal 1 - Start Backend:**
```bash
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
✅ Model and artifacts loaded successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

**Expected Output:**
```
> vite_react_shadcn_ts@0.0.0 dev
> vite

  VITE v5.4.21  ready in 763 ms

  ➜  Local:   http://localhost:8080/
```

### **Access the Application:**
- **Frontend Dashboard**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📝 Configuration

### **Environment Variables**

Create `.env` file in `backend/` directory (optional):

```bash
# .env (repository root; see .env.example)
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:8080
MAX_UPLOAD_BYTES=10485760
MAX_CSV_ROWS=100000
MIN_FEATURE_COVERAGE=0.80
```

---

## 📊 Data & Models

### **Verify Model Files**

Ensure these files exist:

```bash
# Check model file
ls models/best_nids_model.joblib

# Check preprocessing artifacts
ls data/processed/preprocessing_artifacts.joblib
```

**If files missing:**
- Run the Jupyter notebooks in `notebooks/` folder in order (01 → 06)
- Or download pre-trained models from releases

---

## 🧪 Testing the Setup

### **Test Backend API**

```bash
# Test health check (if available)
curl http://localhost:8000/

# Test with Swagger UI
# Open: http://localhost:8000/docs
```

### **Test Frontend**

- Open http://localhost:8080 in your browser
- Check console for errors: `F12` → `Console`
- Verify API calls are working

---

## 🐛 Common Issues & Solutions

### **Issue 1: "ModuleNotFoundError: No module named 'fastapi'"**
**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall requirements
pip install -r requirements.txt
```

### **Issue 2: "Port 8000 already in use"**
**Solution:**
```bash
# Change port in command
python -m uvicorn backend.app:app --port 8001

# Or kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### **Issue 3: "Port 8080 already in use"**
**Solution:**
```bash
# Edit frontend/vite.config.ts
# Change port to 8081 or other available port

# Or use different port directly
npm run dev -- --port 8081
```

### **Issue 4: "npm ERR! code EACCES"**
**Solution:**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
npm install
```

### **Issue 5: "Model not found" error**
**Solution:**
1. Verify files exist: `models/best_nids_model.joblib`
2. Check file permissions are readable
3. Run training notebooks if files don't exist

### **Issue 6: "CORS Error" in browser**
**Solution:**
- Backend already has CORS enabled in `app.py`
- Ensure frontend URL is in `allow_origins`
- Clear browser cache (Ctrl+Shift+Delete)

---

## 📚 Jupyter Notebooks

If you need to train or analyze:

```bash
# Navigate to notebooks
cd notebooks

# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

**Run notebooks in order:**
1. `01.download_dataset.ipynb` - Download CICIDS2017 dataset
2. `02.clean_dataset.ipynb` - Clean and prepare data
3. `03.preprocess_dataset.ipynb` - Feature engineering
4. `04.train_model.ipynb` - Train ML models
5. `05.predict_intrusion.ipynb` - Make predictions
6. `06.evaluate_best_model.ipynb` - Evaluate performance

---

## 🔄 Development Workflow

### **Making Code Changes**

**Backend:**
- Edit files in `backend/app.py`
- Server auto-reloads with `--reload` flag
- Check console for errors

**Frontend:**
- Edit files in `frontend/src/`
- Vite auto-refreshes (HMR - Hot Module Replacement)
- Check browser console (F12) for errors

### **Git Workflow**

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes...

# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature

# Create Pull Request on GitHub
```

---

## 📦 Production Deployment

### **Build Frontend for Production**

```bash
cd frontend

# Create optimized build
npm run build

# Output goes to: frontend/dist/

# Preview build
npm run preview
```

### **Run Backend in Production**

```bash
# Run without reload flag
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Using Docker (Optional)**

```bash
# Build image
docker build -t secureflow-ai .

# Run container
docker run -p 8000:8000 secureflow-ai
```

---

## 🆘 Getting Help

### **Documentation**
- See [README.md](../README.md) for project overview
- Check [requirements.txt](../requirements.txt) for dependencies
- Review code comments in source files

### **Debugging**
1. Check terminal output for error messages
2. Look at browser console (F12 → Console tab)
3. Enable debug mode: Set `DEBUG=True` in env
4. Check logs: `backend/app.py` prints key info

### **Need More Help?**
- Ask team members
- Check project issues on GitHub
- Consult documentation links in README.md

---

## ✨ Next Steps

After successful setup:

1. **Familiarize yourself** with the codebase
2. **Run the notebooks** to understand data pipeline
3. **Make API calls** to backend from frontend
4. **Create a feature branch** for your contribution
5. **Submit pull request** with your changes

---

## 📋 Checklist for First TimeSetup

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] Repository cloned
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:8080
- [ ] API documentation accessible
- [ ] Dashboard loads properly
- [ ] No console errors

---

**Congratulations! You're all set! 🎉**

For questions, contact the team lead or check GitHub Issues.

---

**Last Updated**: March 2026  
**Version**: 1.0.0
