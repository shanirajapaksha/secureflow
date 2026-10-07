# Contributing to SecureFlow-AI

Thank you for your interest in contributing to SecureFlow-AI! This guide will help you contribute effectively.

---

## 🤝 Code of Conduct

- Be respectful and inclusive
- Use constructive communication
- Report bugs responsibly
- Give credit where deserved

---

## 📋 Getting Started

### **1. Setup Development Environment**
Follow [SETUP_GUIDE.md](./SETUP_GUIDE.md) first.

### **2. Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b bugfix/issue-description
```

### **3. Branch Naming Convention**
- `feature/dashboard-improvements`
- `bugfix/cors-error`
- `docs/api-documentation`
- `test/add-unit-tests`

---

## 🛠️ Development Guidelines

### **Backend (Python/FastAPI)**

#### **Code Style**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused

#### **Example Backend Function**
```python
from fastapi import APIRouter, UploadFile, File
import pandas as pd

router = APIRouter()

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Predict intrusions from uploaded CSV file.
    
    Args:
        file: CSV file with network traffic data
    
    Returns:
        dict: Predictions and statistics
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        # Process data...
        return {"predictions": [...]}
    except Exception as e:
        return {"error": str(e)}
```

#### **Testing**
```bash
# Run tests
pytest backend/tests/

# Check code style
pylint backend/app.py

# Type checking
mypy backend/
```

### **Frontend (React/TypeScript)**

#### **Code Style**
- Use functional components with hooks
- Use TypeScript for type safety
- Follow React best practices
- Use Tailwind CSS for styling

#### **Example Frontend Component**
```tsx
import { useState } from 'react';
import { Card } from '@/components/ui/card';

interface Props {
  title: string;
  onSubmit: (data: any) => Promise<void>;
}

export const Dashboard: React.FC<Props> = ({ title, onSubmit }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      await onSubmit({});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <h1>{title}</h1>
      {error && <div className="text-red-500">{error}</div>}
      {/* Component JSX */}
    </Card>
  );
};
```

#### **Testing**
```bash
# Run tests
npm test

# Run linter
npm run lint

# Build check
npm run build
```

### **Data Science (Python/Notebooks)**

#### **Notebook Standards**
- Clear markdown explanations
- Well-commented code
- One responsibility per cell
- Output visualization where applicable

#### **Example Notebook Structure**
```python
# Cell 1: Imports and setup
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Cell 2: Load data
df = pd.read_csv('data.csv')
print(f"Shape: {df.shape}")

# Cell 3: Exploratory Analysis
df.describe()
df.info()

# Cell 4: Preprocessing
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Cell 5: Model Training
# ... training code ...

# Cell 6: Evaluation
# ... evaluation code ...
```

---

## 📝 Commit Guidelines

### **Commit Message Format**

```
<type>(<scope>): <subject>

<body>

<footer>
```

### **Types**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build, dependencies

### **Examples**
```
feat(api): add file upload endpoint
fix(dashboard): resolve CORS error
docs(readme): update setup instructions
refactor(frontend): optimize state management
test(backend): add prediction tests
```

### **Commit Template**
```bash
git config commit.template .gitmessage  # If you create a template file

# Good commit
git commit -m "feat(api): add intrusion detection endpoint

- Implemented POST /predict endpoint
- Added CSV file validation
- Returns predictions and statistics"

# Bad commits (avoid)
git commit -m "fixed stuff"
git commit -m "update"
git commit -m "work in progress"
```

---

## 🧪 Testing Requirements

### **Before Submitting PR:**

**Backend:**
```bash
cd backend
python -m pytest --cov=.
pylint app.py
mypy app.py
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run build
npm test
```

### **Test Coverage**
- Aim for >80% coverage
- Test edge cases
- Mock external dependencies

### **Manual Testing**
- Run application end-to-end
- Test on different browsers (frontend)
- Check error handling

---

## 📤 Pull Request Process

### **Step 1: Create Pull Request**
```bash
# Push your branch
git push origin feature/your-feature

# Create PR on GitHub with:
# - Clear title
# - Description of changes
# - Reference to related issues (#123)
# - Screenshots if UI changes
```

### **Step 2: PR Template**
```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing Done
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
```

### **Step 3: Code Review**
- Respond to review comments
- Make requested changes
- Request re-review

### **Step 4: Merge**
- Ensure CI/CD passes
- Rebase if needed
- Delete feature branch after merge

---

## 🐛 Bug Report Template

```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Expected result
4. Actual result

## Environment
- OS: Windows/macOS/Linux
- Python: 3.9/3.10/3.11
- Node: 16/18/20
- Browser: Chrome/Firefox

## Error Message
```
Error stack trace here
```

## Screenshots
[Add screenshots if applicable]
```

---

## ✨ Feature Request Template

```markdown
## Is your feature request related to a problem?
Description of the problem.

## Describe the Solution
How should this feature work?

## Describe Alternatives
Any alternative solutions?

## Additional Context
Screenshots, links, or other context.
```

---

## 📚 Project Structure & Responsibilities

### **Backend** (`backend/app.py`)
- API endpoints
- Data validation
- Model prediction logic
- Error handling

### **Frontend** (`frontend/src/`)
- UI components
- State management
- API integration
- Styling

### **Data & Models**
- Model files: `models/`
- Datasets: `data/`
- Notebooks: `notebooks/`

### **Documentation**
- README.md - Project overview
- SETUP_GUIDE.md - Setup instructions
- CONTRIBUTING.md - This file

---

## 🔍 Code Review Checklist

**Reviewers, check:**
- [ ] Code follows project style
- [ ] No hardcoded values
- [ ] Proper error handling
- [ ] Tests included
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance acceptable
- [ ] Security considerations met

---

## 🚀 Common Contribution Areas

### **Backend Improvements**
- Add new ML models
- Optimize prediction performance
- Add more API endpoints
- Improve error handling

### **Frontend Enhancements**
- Add new dashboard charts
- Improve UX/responsiveness
- Add dark mode
- Optimize performance

### **Documentation**
- API documentation
- Tutorial guides
- Architecture diagrams
- Troubleshooting guides

### **Testing**
- Write unit tests
- Integration tests
- End-to-end tests
- Performance tests

---

## 📞 Questions or Help?

- **Issues**: Check GitHub Issues
- **Discussions**: Use GitHub Discussions
- **Team**: Contact project lead
- **Slack**: Post in #secureflow-ai channel

---

## 🙏 Recognition

Contributors will be recognized in:
- Contributors section of README
- Release notes
- Project website

---

## 📋 Additional Resources

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [React Best Practices](https://react.dev/learn)
- [Git Commit Best Practices](https://cbea.ms/git-commit/)
- [How to Make a Pull Request](https://opensource.guide/how-to-contribute/#opening-a-pull-request)

---

## 🎉 Thank You!

Your contributions make SecureFlow-AI better for everyone. Thank you for your time and effort!

---

**Last Updated**: March 2026  
**Version**: 1.0.0
