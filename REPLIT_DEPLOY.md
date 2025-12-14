# Replit Deployment - Fast & Easy

## The Fastest Way (5 Minutes)

### Step 1: Go to Replit
https://replit.com

### Step 2: Import Project
Click **"Create"** → **"Import from GitHub"**

Paste: `https://github.com/nihalkumarnetha/smartquiz`

### Step 3: Configure Replit

Edit `.replit` file to:
```
run = "python app_sqlite.py"
entrypoint = "app_sqlite.py"
```

### Step 4: Click "Run"

That's it! Your app is live at: `https://smartquiz-USERNAME.replit.dev`

---

## Database Options

### Option A: SQLite (Already Set Up - Recommended)
- File: `app_sqlite.py`
- No external database needed
- Data persists in `smartquiz.db`
- **✅ EASIEST - Use this**

### Option B: Keep Using MySQL
- Keep using original `app.py`
- Add MySQL to Replit via Database tab
- More setup required

---

## What's Included

✅ `app_sqlite.py` - SQLite version of your app
✅ `.replit` - Replit configuration
✅ `requirements.txt` - All dependencies
✅ All templates and HTML files

---

## Deployment Steps

### 1. Push Latest Code to GitHub
```bash
cd smartquiz/.smartquiz
git add .
git commit -m "Add Replit deployment"
git push origin main
```

### 2. Import on Replit
- Go to https://replit.com
- Click Create → Import from GitHub
- Select your smartquiz repo
- Click Import

### 3. Run
Click the **RUN** button at the top

### 4. Access
Your app is live at: `https://smartquiz-<your-username>.replit.dev`

---

## Default Login

- **Username**: admin
- **Password**: admin123

⚠️ **Change this immediately after login!**

---

## Features Available

✅ User registration (Student/Lecturer)
✅ Admin dashboard
✅ Quiz creation
✅ Quiz taking
✅ Results tracking
✅ User management
✅ All databases auto-created

---

## Replit Features (Free)

- ✅ Always online (no sleep)
- ✅ Custom domain (paid)
- ✅ Collaboration
- ✅ Version control
- ✅ 5GB storage
- ✅ Real-time logs

---

## Troubleshooting

### App won't start
1. Click "Stop"
2. Click "Run" again
3. Check logs for errors

### Database errors
1. Delete `smartquiz.db` if corrupted
2. It will recreate on next run

### Import fails
1. Check repository is public
2. Make sure GitHub is linked
3. Try again

---

## That's It!

You now have a free, fully-functional quiz app online!

Questions? Check Replit docs: https://docs.replit.com
