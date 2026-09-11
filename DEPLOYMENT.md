# AIRINDEX — Deployment & Hosting Guide 🚀

This document details how to host and deploy the **AIRINDEX** platform live to the web or run it using Docker containers.

---

## 🐋 Option 1: Docker & Docker Compose (Local or Cloud Server)

Run both backend API and React frontend in isolated Docker containers with a single command:

```bash
docker compose up --build -d
```

- **Frontend**: Available at `http://localhost:5173`
- **Backend API**: Available at `http://localhost:8000`
- **Swagger Docs**: Available at `http://localhost:8000/docs`

To stop the containers:
```bash
docker compose down
```

---

## ⚡ Option 2: Deploy Free on Vercel (Frontend) & Render (Backend)

### 1. Backend Deployment (Render.com)
1. Push your code to GitHub.
2. Go to [Render.com](https://render.com) -> New Web Service.
3. Connect your repository and select the `render.yaml` blueprint or set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Copy your live backend URL (e.g., `https://airindex-backend.onrender.com`).

### 2. Frontend Deployment (Vercel)
1. Go to [Vercel.com](https://vercel.com) -> Add New Project.
2. Select your GitHub repository and set:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Environment Variable**: `VITE_API_BASE_URL` = `https://airindex-backend.onrender.com`
3. Click **Deploy**!

---

## 🖥️ Option 3: Local Windows Startup

Use the pre-configured 1-click batch scripts:
* `backend/start_backend.bat`
* `frontend/start_frontend.bat`
