# GitHub Upload - Quick Start

## 🚀 Quick Steps

### 1. Initialize Git (if not done)
```bash
git init
```

### 2. Check what will be uploaded
```bash
git status
```

**Verify these are NOT listed:**
- ❌ `venv/`
- ❌ `db.sqlite3`
- ❌ `.env`
- ❌ `__pycache__/`

### 3. Add files
```bash
git add .
```

### 4. Commit
```bash
git commit -m "Initial commit: ICPS Django project"
```

### 5. Create GitHub Repository
- Go to https://github.com/new
- Create repository (don't initialize with README)
- Copy the repository URL

### 6. Connect and Push
```bash
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## ✅ Files That WILL Be Uploaded

- ✅ All `.py` files (source code)
- ✅ `requirements.txt`
- ✅ `README.md` and all `.md` files
- ✅ `.gitignore`
- ✅ `.env.example` (template, no secrets)
- ✅ Migration files
- ✅ Django project structure

## ❌ Files That WON'T Be Uploaded (Auto-Excluded)

- ❌ `venv/` (virtual environment)
- ❌ `db.sqlite3` (database)
- ❌ `.env` (your secrets - NEVER upload!)
- ❌ `__pycache__/` (Python cache)
- ❌ `logs/` (log files)
- ❌ `*.log` files

---

## ⚠️ Security Check

Before pushing, make sure:
- [ ] `.env` file is NOT in the repository
- [ ] No passwords/secrets in `settings.py`
- [ ] `.env.example` exists (template only)

---

## 📖 Full Guide

See `GITHUB_SETUP_GUIDE.md` for detailed instructions.

