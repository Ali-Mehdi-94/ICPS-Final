# GitHub Repository Setup Guide

## Quick Checklist

### ✅ Files to UPLOAD (Include):
- ✅ All Python source files (`.py`)
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `manage.py`
- ✅ All migration files (`core/migrations/*.py`)
- ✅ `.gitignore`
- ✅ `.env.example` (template for environment variables)
- ✅ Documentation files (`.md` files)
- ✅ Django project structure (ICPS/, core/, etc.)

### ❌ Files to SKIP (Exclude):
- ❌ `venv/` or `env/` (virtual environment)
- ❌ `__pycache__/` folders
- ❌ `*.pyc` files
- ❌ `db.sqlite3` (database file)
- ❌ `.env` (contains secrets - NEVER upload!)
- ❌ `logs/` directory
- ❌ `*.log` files
- ❌ IDE files (`.vscode/`, `.idea/`)
- ❌ Test scripts (optional - you can include or exclude)

---

## Step-by-Step Instructions

### Step 1: Verify .gitignore is Complete

Your `.gitignore` file should already be set up correctly. It includes:
- ✅ Virtual environments (`venv/`, `env/`)
- ✅ Python cache (`__pycache__/`, `*.pyc`)
- ✅ Database files (`db.sqlite3`)
- ✅ Environment files (`.env`)
- ✅ Logs (`logs/`, `*.log`)
- ✅ IDE files

**Your current `.gitignore` looks good!** ✅

### Step 2: Create .env.example File

I've created a `.env.example` file for you. This shows what environment variables are needed without exposing actual secrets.

**Important:** Make sure you have a `.env` file locally (with real values) but it should NOT be committed to GitHub (it's already in `.gitignore`).

### Step 3: Initialize Git Repository (if not already done)

```bash
# Navigate to your project directory
cd "C:\New folder"

# Initialize git (if not already done)
git init

# Check current status
git status
```

### Step 4: Add Files to Git

```bash
# Add all files (gitignore will automatically exclude ignored files)
git add .

# Check what will be committed
git status
```

**Verify the output:** You should NOT see:
- ❌ `venv/`
- ❌ `db.sqlite3`
- ❌ `.env`
- ❌ `__pycache__/`
- ❌ `logs/`

### Step 5: Create Initial Commit

```bash
# Create your first commit
git commit -m "Initial commit: ICPS Django project with ProQual features and notification system"
```

### Step 6: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in:
   - **Repository name**: `icps-django` (or your preferred name)
   - **Description**: "ICPS - Student Registration & Course Management System"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (you already have these)
4. Click **"Create repository"**

### Step 7: Connect Local Repository to GitHub

GitHub will show you commands. Use these:

```bash
# Add GitHub remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename default branch to main (if needed)
git branch -M main

# Push your code
git push -u origin main
```

**If you get authentication errors**, you may need to:
- Use a Personal Access Token instead of password
- Or set up SSH keys

---

## What Gets Uploaded (Summary)

### ✅ Included Files:

```
ICPS/
├── ICPS/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── permissions.py
│   ├── services.py
│   ├── signals.py
│   ├── dashboard.py
│   ├── utils.py
│   ├── notifications.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── *.py (all migration files)
│   └── management/
│       └── commands/
│           └── *.py
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── CHANGELOG.md
├── EMAIL_SETUP_GUIDE.md
├── NOTIFICATION_SYSTEM.md
└── GITHUB_SETUP_GUIDE.md (this file)
```

### ❌ Excluded Files (automatically ignored):

```
venv/                    # Virtual environment
__pycache__/            # Python cache
*.pyc                   # Compiled Python files
db.sqlite3             # Database
.env                    # Environment variables (SECRET!)
logs/                   # Log files
*.log                   # Log files
.vscode/                # IDE settings
.idea/                  # IDE settings
```

---

## Optional: Clean Up Test Files

You may want to exclude test scripts from the repository. They're useful for development but not needed in production.

**Option 1: Keep them** (recommended for open source)
- They help other developers understand the system
- Useful for documentation

**Option 2: Remove them** (if you want a cleaner repo)
Add to `.gitignore`:
```
# Test scripts
test_*.py
check_errors.py
simple_test.py
```

Then:
```bash
git rm --cached test_*.py check_errors.py simple_test.py
git commit -m "Remove test scripts from repository"
```

---

## Security Checklist

Before pushing to GitHub, verify:

- [ ] ✅ `.env` file is NOT in the repository (check with `git status`)
- [ ] ✅ `SECRET_KEY` is not hardcoded in `settings.py` (it should use environment variables)
- [ ] ✅ Database credentials are not in code
- [ ] ✅ Email passwords are not in code
- [ ] ✅ `.env.example` exists (template without real values)

---

## After Uploading

### 1. Add Repository Description

On GitHub, add a description and topics:
- `django`
- `django-rest-framework`
- `student-management`
- `education`

### 2. Update README

Make sure your `README.md` includes:
- Installation instructions
- Environment variable setup (reference `.env.example`)
- How to run the project

### 3. Add a License (Optional)

If making it public, consider adding a license file (MIT, Apache, etc.)

---

## Common Issues

### Issue: "venv/ is being tracked"

**Solution:**
```bash
# Remove from git cache
git rm -r --cached venv/

# Verify it's in .gitignore
# Then commit
git commit -m "Remove venv from tracking"
```

### Issue: "db.sqlite3 is being tracked"

**Solution:**
```bash
git rm --cached db.sqlite3
git commit -m "Remove database from tracking"
```

### Issue: "Authentication failed"

**Solutions:**
1. Use Personal Access Token instead of password
2. Set up SSH keys
3. Use GitHub CLI: `gh auth login`

---

## Quick Command Reference

```bash
# Check what will be committed
git status

# See what's being ignored
git status --ignored

# Add all files (respects .gitignore)
git add .

# Commit
git commit -m "Your commit message"

# Push to GitHub
git push -u origin main

# Check remote
git remote -v
```

---

## Next Steps After Uploading

1. **Clone on another machine** to test:
   ```bash
   git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
   cd REPO_NAME
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with real values
   python manage.py migrate
   python manage.py runserver
   ```

2. **Set up CI/CD** (optional):
   - GitHub Actions for automated testing
   - Automated deployment

3. **Add collaborators** (if working in a team)

---

## Summary

✅ **DO Upload:**
- Source code (`.py` files)
- Configuration templates (`.env.example`)
- Documentation (`.md` files)
- `requirements.txt`
- Migration files

❌ **DON'T Upload:**
- Virtual environment (`venv/`)
- Database files (`db.sqlite3`)
- Environment variables (`.env`)
- Cache files (`__pycache__/`)
- Log files (`*.log`)

Your `.gitignore` is already configured correctly! Just follow the steps above to push to GitHub. 🚀

