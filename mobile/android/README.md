# Android App & Google Play Store — Complete 20-Phase Roadmap

This guide explains how to turn the RAG Chatbot backend into a published Android app.
Written for beginners and intermediate Python developers.

## Recommended Approach: Android WebView

**Why WebView for this project?**
You already have a working React web frontend. The fastest path to the Play Store
is wrapping it in an Android WebView — no Dart, no React Native rewrites needed.

| Option | Pros | Cons | Rating |
|--------|------|------|--------|
| **WebView (recommended)** | Reuses React UI, fastest | Needs internet | ⭐⭐⭐⭐⭐ |
| Flutter | Native feel, iOS+Android | Learn Dart, full rewrite | ⭐⭐⭐⭐ |
| React Native | JS skills | Partial UI rewrite | ⭐⭐⭐ |
| Kivy (Python) | Python | Poor Play Store support | ⭐⭐ |

---

## Phase 1 — Finish Backend

1. Copy `backend/.env.example` → `backend/.env`
2. Add your `GOOGLE_API_KEY` from https://aistudio.google.com
3. Generate SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(64))"`
4. Start backend: `uvicorn app.main:app --reload`
5. Test at http://localhost:8000/docs
6. Run tests: `pytest tests/ -v`

✅ **Done when**: All tests pass, full RAG flow works.

---

## Phase 2 — Deploy Backend

**Recommended: Railway.app (free tier, beginner-friendly)**

1. Sign up at https://railway.app
2. Install CLI: `npm install -g @railway/cli`
3. `railway login` → `railway init` → `railway up`
4. Add environment variables in Railway dashboard
5. Get your HTTPS URL: `https://your-app.railway.app`

Other options: Render.com, Fly.io, Google Cloud Run.

✅ **Done when**: `https://your-app.railway.app/health` returns `{"status":"healthy"}`.

---

## Phase 3 — Build Mobile UI

1. Download Android Studio: https://developer.android.com/studio
2. Install: Android SDK API 34, Emulator, AVD (Pixel 6 emulator)
3. New Project → **Empty Views Activity**
   - Language: Java
   - Min SDK: API 24 (Android 7.0)
   - Package: `com.yourname.ragchatbot`

✅ **Done when**: Hello World runs on emulator.

---

## Phase 4 — Connect App to API

**`res/layout/activity_main.xml`:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/an
