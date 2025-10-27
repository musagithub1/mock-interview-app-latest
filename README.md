# 🎯 AI-Powered Mock Interviewer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Your Personal AI Interview Coach - Practice Smarter, Perform Better**

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [📖 Documentation](#-how-to-use) • [🤝 Contributing](#-contributing)

![App Screenshot](https://i.imgur.com/your-screenshot-url.png)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Installation Methods](#-installation-methods)
  - [Docker (Recommended)](#1-docker-recommended)
  - [Docker Hub](#2-docker-hub-image)
  - [Local Development](#3-local-development)
- [Configuration](#-configuration)
- [How to Use](#-how-to-use)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎓 About

**AI-Powered Mock Interviewer** is an intelligent, interactive interview preparation platform that leverages cutting-edge AI models to simulate realistic job interviews. Whether you're preparing for your dream role or honing your interview skills, this tool provides personalized questions, instant feedback, and comprehensive evaluations to help you succeed.

### Why This App?

- ✅ **Practice Anytime, Anywhere** - No scheduling needed
- ✅ **Adaptive Learning** - AI adjusts to your responses
- ✅ **Safe Environment** - Make mistakes and learn without consequences
- ✅ **Comprehensive Feedback** - Detailed insights on every answer
- ✅ **Track Progress** - Review past interviews and measure improvement

---

## ✨ Features

### 🤖 **Intelligent AI Interviewer**
Powered by OpenRouter, access state-of-the-art models including:
- GPT-4, Claude 3.5 Sonnet, Llama 3, Gemini Pro, and more
- Context-aware questioning based on your job title
- Natural conversation flow with follow-up questions

### 🎯 **Multiple Interview Modes**

| Mode | Description | Best For |
|------|-------------|----------|
| 🌐 **General** | Broad questions covering various topics | Entry-level positions, career changers |
| 💻 **Technical** | Role-specific technical challenges | Developers, engineers, data scientists |
| 🎭 **Behavioral** | STAR format situational questions | Leadership roles, experienced professionals |

### 💬 **Modern Chat Interface**
- Clean, intuitive chatbot-style UI
- Real-time conversation history
- Smooth scrolling and message threading

### 📊 **Dual Feedback System**
1. **Instant Feedback** - Get immediate coaching after each answer
2. **Final Evaluation** - Comprehensive report at interview completion
   - Overall performance score
   - Strengths identified
   - Areas for improvement
   - Actionable recommendations

### 💾 **Persistent Storage**
- All sessions automatically saved to Firebase
- Searchable interview history
- Transcript preservation
- Performance tracking over time

### 📜 **History Dashboard**
- Browse all past interviews
- Filter by date, type, or performance
- Review transcripts and feedback
- Track your improvement journey

---

## 🛠️ Tech Stack

<div align="center">

| Category | Technology |
|----------|------------|
| **Frontend** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) |
| **AI Engine** | ![OpenRouter](https://img.shields.io/badge/OpenRouter-000000?style=flat&logo=openai&logoColor=white) |
| **Database** | ![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black) |
| **Containerization** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) |
| **Language** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) |

</div>

---

## 🚀 Quick Start

Get up and running in **less than 5 minutes**!

### Prerequisites

- ✅ Docker & Docker Compose installed
- ✅ OpenRouter API key ([Get one here](https://openrouter.ai/keys))
- ✅ Firebase project with Realtime Database enabled

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/musagithub1/mock-interview-app-latest.git
cd mock-interview-app-latest

# Create secrets file (see Configuration section)
mkdir -p .streamlit
nano .streamlit/secrets.toml

# Launch the app
docker-compose up
```

**🎉 That's it!** Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📦 Installation Methods

### 1. Docker (Recommended)

**Perfect for:** Quick setup, consistent environment, easy deployment

#### Step 1: Create Secrets File

```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

Add your configuration (see [Configuration](#-configuration) section below).

#### Step 2: Launch

```bash
docker-compose up
```

To run in detached mode:
```bash
docker-compose up -d
```

To stop:
```bash
docker-compose down
```

---

### 2. Docker Hub Image

**Perfect for:** Using pre-built images, CI/CD pipelines

Pull and run the latest image:

```bash
docker pull musagithub1/mock-interview-app:latest

docker run -p 8501:8501 \
  -v "$(pwd)/.streamlit/secrets.toml:/app/.streamlit/secrets.toml" \
  musagithub1/mock-interview-app:latest
```

**Windows PowerShell:**
```powershell
docker run -p 8501:8501 `
  -v "${PWD}/.streamlit/secrets.toml:/app/.streamlit/secrets.toml" `
  musagithub1/mock-interview-app:latest
```

---

### 3. Local Development

**Perfect for:** Contributing, customization, debugging

#### Step 1: Clone & Setup Environment

```bash
git clone https://github.com/musagithub1/mock-interview-app-latest.git
cd mock-interview-app-latest

# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Configure Secrets

Create `.streamlit/secrets.toml` (see [Configuration](#-configuration)).

#### Step 4: Run

```bash
streamlit run app.py
```

---

## ⚙️ Configuration

Create a `.streamlit/secrets.toml` file with the following structure:

```toml
# OpenRouter API Configuration
# Get your key from: https://openrouter.ai/keys
OPENROUTER_API_KEY = "sk-or-v1-YOUR_KEY_HERE"

# Firebase Realtime Database URL
# Found in Firebase Console > Realtime Database
FIREBASE_DATABASE_URL = "https://your-project.firebaseio.com/"

# Firebase Service Account Credentials
# Generate from: Firebase Console > Project Settings > Service Accounts
[firebase_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_CONTENT_HERE
-----END PRIVATE KEY-----
"""
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "123456789012345678901"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"
```

### 🔐 Security Notes

- ⚠️ **Never commit `secrets.toml` to version control**
- ⚠️ Add `.streamlit/secrets.toml` to your `.gitignore`
- ⚠️ Use environment variables in production
- ⚠️ Rotate API keys regularly

---

## 📖 How to Use

### Starting Your First Interview

1. **🌐 Open the App**  
   Navigate to [http://localhost:8501](http://localhost:8501)

2. **📝 Configure Interview Settings** (Sidebar)
   - **Job Title**: Enter your target position (e.g., "Senior Software Engineer")
   - **Interview Type**: Choose from General, Technical, or Behavioral
   - **Number of Questions**: Select 3, 5, or 7 questions
   - **AI Model**: Pick your preferred model (Claude, GPT-4, etc.)

3. **🚀 Start Interview**  
   Click the "Start Interview" button

4. **💭 Answer Questions**
   - Read each question carefully
   - Type your response in the chat input
   - Press Enter to submit

5. **🧑‍🏫 Review Feedback**
   - Instant feedback appears after each answer
   - Learn from suggestions and tips
   - Apply improvements to next answers

6. **📊 Final Evaluation**
   - Complete all questions to receive your comprehensive report
   - Review strengths and areas for improvement
   - Save the session for future reference

### Reviewing Past Interviews

1. Click **"My Interview History"** in the sidebar
2. Browse through your completed sessions
3. Click on any interview to view:
   - Full transcript
   - All feedback received
   - Final evaluation scores
   - Timestamps and metadata

---

## 📁 Project Structure

```
mock-interview-app/
├── 📄 app.py                    # Main Streamlit application
├── 📄 requirements.txt          # Python dependencies
├── 📄 Dockerfile               # Docker container configuration
├── 📄 docker-compose.yml       # Docker Compose orchestration
├── 📄 README.md                # This file
├── 📄 .gitignore              # Git ignore rules
├── 📂 .streamlit/
│   └── 📄 secrets.toml        # API keys & credentials (not tracked)
├── 📂 utils/                   # Utility modules (if applicable)
└── 📂 assets/                  # Images, icons, etc. (if applicable)
```

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, feature additions, or documentation improvements.

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/mock-interview-app-latest.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests if applicable

4. **Commit Your Changes**
   ```bash
   git commit -m "✨ Add amazing feature"
   ```

5. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**

### Development Guidelines

- 📝 Write clear commit messages
- 🧪 Test your changes thoroughly
- 📚 Update documentation as needed
- 🎨 Follow Python PEP 8 style guide

---

## 🐛 Troubleshooting

### Common Issues

**Problem:** Docker container won't start  
**Solution:** Ensure `secrets.toml` exists and is properly formatted

**Problem:** API errors from OpenRouter  
**Solution:** Verify your API key and check you have credits

**Problem:** Firebase connection fails  
**Solution:** Double-check service account JSON and database URL

**Problem:** Port 8501 already in use  
**Solution:** Change port in `docker-compose.yml` or stop conflicting service

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Mussa khan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 📧 Contact

**Musa**

- 🐙 GitHub: [@musagithub1](https://github.com/musagithub1)
- 📧 Email: your.email@example.com *(optional - add if you want)*
- 💼 LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile) *(optional)*

---

## 🌟 Acknowledgments

- 🤖 [OpenRouter](https://openrouter.ai/) for providing access to multiple AI models
- 🔥 [Firebase](https://firebase.google.com/) for reliable database services
- 🎨 [Streamlit](https://streamlit.io/) for the amazing web framework
- 💙 All contributors and users of this project

---

## 📈 Roadmap

- [ ] Add voice interview mode
- [ ] Multi-language support
- [ ] Interview recording and playback
- [ ] Performance analytics dashboard
- [ ] Mobile app version
- [ ] Integration with job boards
- [ ] Resume parsing for personalized questions

---

<div align="center">

**⭐ If you find this project helpful, please give it a star! ⭐**

Made with ❤️ by [Musa](https://github.com/musagithub1)

[⬆ Back to Top](#-ai-powered-mock-interviewer)

</div>
