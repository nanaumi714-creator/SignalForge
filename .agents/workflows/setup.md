---
description: How to setup the development environment for SignalForge
---

# Setup SignalForge Development Environment

Follow these steps to set up your local environment.

// turbo
1. Create a virtual environment
```powershell
python -m venv .venv
```

// turbo
2. Activate the virtual environment
```powershell
.\.venv\Scripts\activate
```

// turbo
3. Install dependencies
```powershell
pip install -r requirements.txt
```

4. Create .env file (copy from .env.example)
```powershell
cp .env.example .env
```

5. Run the application
```powershell
uvicorn main:app --reload --port 8000
```
