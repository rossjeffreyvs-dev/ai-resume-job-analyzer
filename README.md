# 🧠 Resume-Job Analyzer

**AI-powered web app** that compares a candidate’s resume with a job description to highlight strengths, gaps, and key matches.  
Built with **Python + Flask**, **OpenAI GPT-4o**, and **AWS Lightsail Docker** for simple and secure deployment.

---

## 🚀 Overview

Resume-Job Analyzer helps job seekers tailor their resumes by instantly evaluating how well they align with a given job description.

Simply:
1. Paste a **job description**
2. Upload your **resume (PDF)**
3. Get a visual, AI-generated comparison with ✅ matches and ❌ gaps

---

## 🧰 Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend** | HTML, CSS (Flask Jinja Templates), Tailwind-like responsive styling |
| **Backend** | Python 3.10, Flask, Gunicorn |
| **AI** | OpenAI GPT-4o API for text analysis |
| **File Parsing** | PyPDF2 |
| **Environment** | python-dotenv |
| **Containerization** | Docker + Lightsail Container Service |
| **Hosting** | AWS Lightsail (Docker Container) |

---

## 🖥️ Local Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/rossjeffreyvs-dev/resume-job-analyzer.git
cd resume-job-analyzer
```

### 2️⃣ Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate      # (Mac/Linux)
venv\Scripts\activate         # (Windows)
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Create a `.env` File
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 5️⃣ Run the Flask App Locally
```bash
python app.py
```
Visit 👉 [http://localhost:5000](http://localhost:5000)

---

## 🐳 Deploying to AWS Lightsail (Docker)

### 1️⃣ Build and Push the Image
```bash
./deploy.sh
```
This script:
- Builds the Docker image for `linux/amd64`
- Pushes it to AWS Lightsail’s container registry
- Deploys it using `lightsail.yaml`
- Monitors deployment status every 5 seconds

### 2️⃣ Environment Variables in Lightsail
Once deployed:
1. Open the AWS Lightsail Console  
2. Select your **container service → Deployment → Environment Variables**
3. Add:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### 3️⃣ Access Your App
After deployment reaches the **RUNNING** state, Lightsail will display a URL like:

```
https://ai-resume-match.<random>.us-east-1.cs.amazonlightsail.com/
```

---

## 📸 Screenshots

> _Add screenshots once deployed to demonstrate the UI and results section._

| Upload & Analyze | AI-Generated Comparison |
|------------------|--------------------------|
| ![Upload Screenshot](docs/screenshots/upload.png) | ![Match Screenshot](docs/screenshots/match.png) |

---

## 🔒 Security Notes
- Do **not** commit your `.env` file or API keys to GitHub.  
- `.gitignore` already excludes sensitive files (`.env`, `uploads/`, etc.)
- Use **environment variables** for all production secrets.

---

## 🧑‍💻 Author

**Jeff Ross**  
💼 [rossjeffreyvs-dev](https://github.com/rossjeffreyvs-dev)  
🚀 Technical Product Manager & Full-Stack Developer  
🌐 [jeffrey-ross.me](https://www.jeffrey-ross.me)

---

## ⭐ Support

If you find this project useful, please ⭐ the repo!  
Your feedback helps others discover it and keeps development going.

---

## 🗺️ Roadmap

- [ ] Add AI confidence scoring  
- [ ] Enable multi-file resume comparison  
- [ ] Save user session reports  
- [ ] Add LinkedIn job import

---

## 📜 License

This project is released under the **MIT License** — feel free to fork, modify, and build upon it.
