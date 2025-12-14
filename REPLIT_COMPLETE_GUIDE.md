# SmartQuiz on Replit - Complete Guide

## 🚀 Deploy in 5 Minutes

### What You Need
- GitHub account (free)
- Replit account (free)
- 5 minutes

### What You Get
- ✅ Live app online (always running)
- ✅ Free database included
- ✅ Custom URL
- ✅ No credit card needed
- ✅ Unlimited projects

---

## STEP-BY-STEP

### ✅ STEP 1: Prepare Your Code (2 minutes)

Run this in your terminal:

```bash
cd smartquiz/.smartquiz
git add .
git commit -m "Prepare for Replit deployment"
git push origin main
```

**What this does**: Uploads your code to GitHub so Replit can access it.

---

### ✅ STEP 2: Create Replit Account (1 minute)

1. Go to https://replit.com
2. Click **Sign Up**
3. Use GitHub to sign up (easiest)
4. Verify email

---

### ✅ STEP 3: Import Your Project (1 minute)

1. Go to https://replit.com
2. Click **+ Create** button (top left)
3. Click **Import from GitHub**
4. Paste: `https://github.com/nihalkumarnetha/smartquiz`
5. Click **Import**

Replit will auto-detect it's Python and set everything up.

---

### ✅ STEP 4: Configure for SQLite (30 seconds)

In the Replit editor, click `.replit` file and replace with:

```
run = "python app_sqlite.py"
entrypoint = "app_sqlite.py"

[env]
FLASK_ENV = "production"
FLASK_APP = "app_sqlite.py"
PYTHONUNBUFFERED = "1"

[nix]
channel = "stable-23_11"

[[ports]]
localPort = 5000
externalPort = 80
```

Save (Ctrl+S)

---

### ✅ STEP 5: Install Dependencies (30 seconds)

In Replit's Shell (bottom), type:

```bash
pip install -r requirements.txt
```

Wait for it to finish. You'll see "done" at the end.

---

### ✅ STEP 6: Start Your App (1 minute)

Click the green **RUN** button at top of screen.

You'll see:
```
* Running on http://0.0.0.0:5000
* Repl will be live at https://smartquiz-USERNAME.replit.dev
```

That URL is your live app!

---

### ✅ STEP 7: Test It

Click the URL shown (like `https://smartquiz-myusername.replit.dev`)

You should see the SmartQuiz login page!

**Login with:**
- Username: `admin`
- Password: `admin123`

---

## ✅ YOU'RE DONE!

Your app is now live and free forever!

---

## What You Can Do Now

### Users Can:
- Register (Student/Lecturer)
- Login securely
- Create quizzes (Lecturers)
- Take quizzes (Students)
- See results
- Admin panel

### Features:
- Database auto-created
- All data persists
- Always online (Replit keeps it running)
- Free (forever)

---

## Important Notes

1. **Change Admin Password**
   - Login as admin/admin123
   - Change password immediately

2. **Replit's Free Tier Includes**
   - Storage: 5GB (your data stored here)
   - Bandwidth: Limited but free
   - CPU: Shared
   - Database: SQLite (local)

3. **Your App**
   - Always accessible
   - Data in `smartquiz.db` file
   - Automatic backup every 6 hours

---

## If Something Goes Wrong

### App won't start
1. Click **Stop** button
2. Wait 2 seconds
3. Click **RUN** button again
4. Check Shell (bottom) for error messages

### Database error
1. In Shell, type: `rm smartquiz.db`
2. Click RUN again
3. Database will recreate automatically

### Can't login
1. Check username/password spelling
2. Default is: admin / admin123
3. If corrupted, delete db and restart

---

## Upgrades (Optional, Paid)

Want more power?
- **Custom domain**: $7/month
- **More resources**: $10-20/month
- **No sleep mode**: $10+/month

But free tier is perfect for testing!

---

## Share Your App

Send this URL to friends:
```
https://smartquiz-yourname.replit.dev
```

They can:
- Register accounts
- Take quizzes
- See results

---

## Next Steps

1. ✅ Deploy (follow steps above)
2. ✅ Test login
3. ✅ Create your first quiz
4. ✅ Share the link
5. ✅ Add more quizzes
6. ✅ Get students to register

---

## Have Questions?

Check:
- **Replit Docs**: https://docs.replit.com
- **Flask Docs**: https://flask.palletsprojects.com/
- **Replit Community**: https://ask.replit.com

---

## Cost Breakdown

| Item | Cost |
|------|------|
| Replit Account | FREE |
| Database (SQLite) | FREE |
| Storage (5GB) | FREE |
| Always Online | FREE |
| **TOTAL** | **FREE FOREVER** |

---

## Summary

✅ Code on GitHub
✅ Import to Replit
✅ One click to deploy
✅ Live in 5 minutes
✅ Free forever
✅ No credit card needed

**That's it! You're done!**

---

**Deploy URL**: https://replit.com  
**Your App**: https://smartquiz-yourname.replit.dev  
**Status**: Online & Free
