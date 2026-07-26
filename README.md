# AceTrack 🚀

**AI-Powered Educational Productivity Platform, Mock Test Generator & Adaptive Study Planner**

AceTrack is a full-stack, Gen AI-powered educational platform designed to transform how students prepare for competitive exams (such as **JEE, NEET, UPSC, GATE, UGC NET**). 

The platform leverages **Large Language Models (LLMs)** to dynamically parse raw syllabus data, generate customized multi-format mock tests, evaluate student answers with detailed feedback and book recommendations, and construct weightage-aware, adaptive study schedules.

![Dashboard](assets/image.png)

🎬 **Application Demo Video:** [Watch Video on Google Drive](https://drive.google.com/drive/folders/1B2Wr9QyxyT2U75F2fcvXjoNOYSOnkJmv?usp=sharing)

---

## 🌐 Live Deployment & Demo Credentials

* **Frontend App:** [https://innova-hack-fawn.vercel.app/](https://innova-hack-fawn.vercel.app/)
* **Backend API Docs:** [https://innova-hack-3u50.onrender.com/docs](https://innova-hack-3u50.onrender.com/docs)

---

## ⚡ Quick Evaluation & How-to-Run Steps

### 🔑 Option 1: Instant Evaluation via Pre-Configured Demo Account (Recommended)
For fast evaluation without manually creating data, use the default demo credentials:
* **Email:** `demo@gmail.com`
* **Password:** `AceTrack`

> **Note:** The demo account comes pre-loaded with onboarded exam details, active study schedules, and uploaded syllabus data so you can immediately test the **Mock Test Generator**, **Interactive Test Evaluation**, and **Adaptive Study Planner**.

---

### 🆕 Option 2: New Account Setup Flow
If you wish to test creating a brand new account from scratch:
1. **Sign Up:** Click **Sign Up** on the app landing page to create a new user account.
2. **Log In:** Log in with your new credentials.
3. **Onboarding:** Complete the step-by-step onboarding wizard (target exam, exam date, daily available study hours, and weak subjects).
4. **Upload Syllabus:** Go to the **Syllabus** tab and upload a syllabus `.xlsx` or `.xls` file.
   * *Sample syllabus Excel files are provided in the backend directory:* [`backend/data/Syllabus.xlsx`](backend/data/Syllabus.xlsx) or [`backend/data/UGCSyllabus.xlsx`](backend/data/UGCSyllabus.xlsx).

---

## ✨ Key Features

### 🔐 Authentication & Personalized Onboarding
* **JWT-Based Authentication:** Secure registration and login with token-based session security.
* **Smart Onboarding Flow:** Captures target exam, target exam date, daily study hour availability, and weak subjects to personalize the dashboard and algorithm calculations.

### 🧠 AI-Powered Mock Test Generator
* **12 Question Formats:** Supports a rich variety of question types beyond basic MCQs:
  * Single Choice MCQs (`MCQ`) & Single-Liners (`SL`)
  * Assertion & Reasoning (`AR`)
  * Match the Following (`MTF`)
  * Two to Five-Statement Analysis (`2S`, `3S`, `4S`, `5S`)
  * Case Study / Comprehension (`CS`)
  * Chronological Ordering (`CH`)
  * Fill in the Blanks (`FU`) & Numerical Answer Types (`NU`)
* **Flexible Generation & Export:** Specify question counts per format, chunk size, and export directly as clean **PDF** or **DOCX** files.
* **Cloud Storage Integration:** Persistent asset storage powered by **Cloudinary**.

### 📊 In-App Test Evaluation & AI Feedback Engine
* **Interactive Test Taking:** Students can attempt tests directly inside the web interface.
* **Instant Auto-Evaluation:** Automatically scores answers and highlights correct vs. incorrect responses.
* **Structured AI Feedback:** Generates feedback identifying:
  * **Strengths:** Praise for mastered concepts.
  * **Gaps:** Clear breakdown of specific weak topics/concepts missed.
  * **Resource Recommendations:** Standard, widely recognized reference books (e.g., *H.C. Verma*, *R.D. Sharma*, *O.P. Tandon*) tailored to identified weak areas.

### 📅 Adaptive AI Study Planner
* **Weightage-Aware Hour Budgeting:** Automatically calculates required study hours per topic based on syllabus weightage, adding a **25% study time boost** to user-flagged weak subjects.
* **LLM-Sequenced Calendar:** Generates interleaved daily study schedules across subjects to optimize retention and avoid burnout.
* **Adaptive Rebalancing & Mastery Tracking:**
  * **Rule-Based Fast Rebalancing:** Overdue or missed tasks are redistributed across remaining days without additional LLM API costs.
  * **Mastery Levels:** Calculates subject progress (*Strong*, *Moderate*, *Weak*) based on completion metrics.

### 📘 Dynamic Syllabus Management
* Upload syllabus files in `.xlsx` or `.xls` format.
* Dynamic extraction of subjects, topics, and weightage metrics, avoiding hardcoded data.

---

## 🏗️ Technical Architecture

AceTrack uses a decoupled, containerized architecture designed for cloud scalability and high performance.

```mermaid
flowchart TD
    A["🌐 React + Vite + Tailwind CSS\n(Frontend on Vercel)"] <-->|REST API / JWT| B["⚡ FastAPI Backend\n(Backend on Render)"]
    
    B <--> C[("🐘 PostgreSQL (Aiven)\nPrimary Relational DB")]
    B <--> D[("🍃 MongoDB Atlas\nAI Logs & Fine-Tuning DB")]
    B <--> E["☁️ Cloudinary\nPDF & Document Storage"]
    B <--> F["🤖 OpenAI API (GPT-4o)\nTest & Schedule Generation"]
```

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, Lucide Icons |
| **Backend** | Python, FastAPI, Uvicorn |
| **Primary Database** | PostgreSQL (hosted on Aiven) with SQLAlchemy ORM |
| **Logging & AI Cache** | MongoDB Atlas |
| **AI / LLM Engine** | OpenAI API (GPT-4o / GPT-4 Turbo) |
| **File / Media Storage** | Cloudinary |
| **Containerization** | Docker & Docker Compose |
| **Deployment** | Vercel (Frontend), Render (Backend Web Service) |

---

## 📂 Project Structure

```text
INNOVA_HACK/
├── backend/                    # FastAPI backend application
│   ├── data/                   # Sample syllabus files & generated exports
│   │   ├── Syllabus.xlsx
│   │   └── UGCSyllabus.xlsx
│   ├── services/
│   │   ├── mocktest/           # Mock test generation & prompt templates
│   │   │   ├── Generation.py
│   │   │   ├── PromptsDict.py
│   │   │   └── ChapterTest.py
│   │   └── studyPlanner/       # Hour budgeting & schedule sequencing
│   │       ├── StudyPlanGenerator.py
│   │       └── PromptsDict.py
│   ├── utils/
│   │   └── syllabus_parser.py  # Syllabus extraction utilities
│   ├── auth.py                 # JWT authentication & password hashing
│   ├── crud.py                 # Database CRUD operations
│   ├── database.py             # SQLAlchemy configuration
│   ├── main.py                 # FastAPI application routes & endpoints
│   ├── models.py               # Database models (User, Plan, Tasks, etc.)
│   ├── schemas.py              # Pydantic schemas
│   ├── Dockerfile              # Production Docker build for backend
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/         # UI Components (Dashboard, StudyPlan, etc.)
│   │   │   ├── Dashboard.tsx
│   │   │   ├── StudyPlanPage.tsx
│   │   │   ├── SyllabusPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   └── OnboardingPage.tsx
│   │   ├── App.tsx             # Main router and state management
│   │   └── main.tsx            # Entry point
│   ├── index.html              # Base HTML template
│   ├── vite.config.ts          # Vite build config
│   ├── vercel.json             # Vercel SPA routing rules
│   └── package.json            # Frontend dependencies
│
├── docker-compose.yml          # Local multi-container orchestration
└── README.md                   # Project documentation
```

---

## 🛠️ Local Setup & Installation

### Prerequisites
* [Docker](https://www.docker.com/) and Docker Compose
* Node.js (v18+) & Python 3.12+ (if running without Docker)
* API credentials for OpenAI, PostgreSQL, and Cloudinary

### Option A: Running with Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HarshKumarSahni/INNOVA_HACK.git
   cd INNOVA_HACK
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the `backend/` directory based on `.env.example`:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/dbname?sslmode=require
   OPENAI_API_KEY=your_openai_api_key
   CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
   SECRET_KEY=your_jwt_secret_key
   MONGO_URI=your_mongodb_uri # optional
   ```

3. **Start services:**
   ```bash
   docker-compose up --build
   ```

4. **Access Applications:**
   * **Frontend:** `http://localhost:5173`
   * **Backend API Docs:** `http://localhost:10000/docs`

---

## 🚀 Deployment Guide

### Backend (Render)
1. Create a **Web Service** on Render pointing to your repository.
2. Set **Root Directory** to `backend`.
3. Select **Docker** as the Runtime environment.
4. Add environment variables (`DATABASE_URL`, `OPENAI_API_KEY`, `CLOUDINARY_URL`, `SECRET_KEY`).

### Frontend (Vercel)
1. Import repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework preset: `Vite`.
4. Set Environment Variable: `VITE_API_BASE_URL=https://innova-hack-3u50.onrender.com`.

---

## 📝 License

Distributed under the **MIT License**.
