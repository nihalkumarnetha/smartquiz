# SmartQuiz - Replit Deployment Guide

## Quick Setup for Replit

Replit makes it super easy to deploy your Flask app with a built-in database.

### Step 1: Push to GitHub

```bash
cd smartquiz/.smartquiz
git add .
git commit -m "Prepare for Replit deployment"
git push origin main
```

### Step 2: Create Replit Project

1. Go to **https://replit.com**
2. Click **"Create"** → **"Import from GitHub"**
3. Select your repository: `nihalkumarnetha/smartquiz`
4. Replit will auto-detect it's Python and set everything up

### Step 3: Configure Database

Replit includes **SQLite** by default (no MySQL setup needed).

Update your code to use SQLite instead of MySQL:

```python
# Option 1: Use SQLite (Recommended for Replit)
import sqlite3

DB_PATH = 'smartquiz.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

Or keep MySQL and add **postgresql** via Replit's database feature.

### Step 4: Install Dependencies

Replit automatically installs from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Step 5: Run Your App

In Replit, just click the **"Run"** button, or type:

```bash
python app.py
```

Your app will be live at: `https://smartquiz-<username>.replit.dev`

---

## Option A: Easy Setup (SQLite - Recommended)

This requires minimal changes to your `app.py`:

1. Install SQLite (usually pre-installed)
2. Replace MySQL connection with SQLite
3. Run and deploy

**Advantages:**
- ✅ No MySQL setup needed
- ✅ Fully free
- ✅ Data persists
- ✅ Easier for Replit

---

## Option B: Keep MySQL (More Complex)

Use Replit's PostgreSQL or external MySQL service:

1. Add PostgreSQL database via Replit UI
2. Update connection string
3. Deploy

**Advantages:**
- ✅ Keeps existing code structure
- ✅ More scalable
- ❌ Slightly more setup

---

## Quick Migration to SQLite (Easiest)

I can convert your `app.py` to use SQLite instead of MySQL. This is the **fastest way** to get live on Replit.

### What I'll do:
1. Update database connection to SQLite
2. Keep all functionality the same
3. Auto-create database on startup
4. Create `.replit` file for Replit config
5. Update requirements.txt if needed

**Do you want me to:**
- [ ] A) Convert to SQLite (5 min setup, deploy in 2 min) ← EASIEST
- [ ] B) Keep MySQL (15 min setup, more complex)
- [ ] C) Use Replit PostgreSQL (10 min setup)

**I recommend Option A (SQLite)** - you'll be live in minutes!

---

## After Deployment

Your app will be at: `https://smartquiz-<username>.replit.dev`

Features:
- ✅ Always online (free)
- ✅ Custom domain support (paid)
- ✅ Collaboration features
- ✅ Version control built-in
- ✅ Real-time logs

---

## Which Option?

Let me know and I'll:
1. Make the code changes needed
2. Create Replit config files
3. Give you exact deploy steps

**Just say:**
- "Convert to SQLite" → Fastest, easiest
- "Keep MySQL" → More complex but possible
- "PostgreSQL" → Middle ground
