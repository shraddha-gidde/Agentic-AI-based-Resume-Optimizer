# 🤖 Agentic AI Resume Optimizer

> An AI-powered platform that helps job seekers beat ATS systems by analyzing resume–job fit using LLM-based semantic matching and vector similarity search.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![NLP](https://img.shields.io/badge/NLP-LLM%20%7C%20Vector%20Search-green)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🚀 What It Does

Most resumes get rejected before a human ever reads them — by ATS (Applicant Tracking Systems) that scan for keyword and semantic matches. This platform solves that by:

- Analyzing how well your resume matches a specific job description
- Scoring it across multiple dimensions (keyword coverage, semantic similarity, completeness)
- Giving you actionable, data-driven suggestions to improve your match rate

---

## ✨ Features

- 📄 **Resume–Job Match Score** — semantic similarity using LLM-based embeddings
- 🔑 **Keyword Coverage Score** — how well your resume covers JD keywords
- 📊 **Profile Completeness Score** — structured evaluation of resume quality
- 🔍 **JD Analysis** — extracts key requirements from any job description
- 🛠️ **Resume Rewriter** — suggests improved bullet points based on the JD
- 🧠 **Multi-Agent Architecture** — orchestrated agents handle each analysis task independently
- 📈 **Visual Analytics** — charts and scores to track improvement over time

---

## 🏗️ Architecture

```
User Input (Resume + JD)
        ↓
  Orchestrator Agent
   ├── JD Analysis Agent       → extracts requirements
   ├── Resume Critique Agent   → identifies gaps
   ├── Resume Rewriter Agent   → suggests improvements
   ├── Final Scorer Agent      → calculates match scores
   └── Visual Analytics        → renders results
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| AI / NLP | LLMs, Vector Search, TF-IDF, Cosine Similarity |
| ML | Scikit-learn, Sentence Transformers |
| UI | Streamlit |
| File Processing | PyPDF2, python-docx |
| Other | Pandas, NumPy |

---

## ⚙️ Getting Started

### Prerequisites
```bash
Python 3.9+
pip
```

### Installation
```bash
# Clone the repo
git clone https://github.com/Shraddhaaa05/Agentic-AI-based-Resume-Optimizer.git
cd Agentic-AI-based-Resume-Optimizer

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📁 Project Structure

```
├── app.py                    # Main Streamlit entry point
├── orchestrator.py           # Agent orchestration logic
├── agent_manager.py          # Agent management
├── jd_analysis_agent.py      # Job description parser
├── resume_critique_agent.py  # Resume gap analysis
├── resume_rewriter_agent.py  # Bullet point optimizer
├── final_scorer_agent.py     # KPI scoring engine
├── visual_analytics.py       # Charts and visualizations
├── file_processor.py         # PDF/DOCX parsing
└── requirements.txt
```

---

## 📊 Key KPIs Tracked

| Metric | Description |
|---|---|
| Resume–Job Match % | Semantic similarity between resume and JD |
| Keyword Coverage Score | % of JD keywords present in resume |
| Profile Completeness Score | Structural quality of the resume |

---

## 👩‍💻 Author

**Shraddha Gidde**
- 🔗 [LinkedIn](https://www.linkedin.com/in/shraddha-gidde-063506242/)
- 💻 [GitHub](https://github.com/Shraddhaaa05)
