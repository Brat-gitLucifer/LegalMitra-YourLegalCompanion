# ⚖️ LegalMitra – AI-Powered Consumer Dispute Analysis & Legal Routing

> **UiPath AgentHack 2026 | Track: Maestro BPMN | Domain: Legal**

LegalMitra is an AI-powered legal assistant that analyzes consumer complaints, researches relevant legal precedents using Retrieval-Augmented Generation (RAG), and assists lawyers in deciding whether a case should proceed to court or be settled outside. Built on **UiPath Maestro BPMN**, it combines AI, automation, and human oversight to dramatically reduce legal research time while making legal assistance accessible in multiple Indian languages.

---

## 🚀 Problem Statement

India receives millions of consumer complaints every year, yet a significant percentage of complainants lack access to affordable legal assistance.

Common challenges include:

* Limited access to lawyers in Tier-2 and Tier-3 cities
* English-only legal communication
* Time-consuming legal research
* Difficulty determining whether a case is worth pursuing

LegalMitra addresses these challenges by automating legal research, generating grounded legal analysis, and keeping both victims and lawyers informed throughout the process.

---

# ✨ Key Features

* 📧 Automatic complaint intake from Gmail
* 🤖 AI-powered legal case analysis
* 📚 RAG-based retrieval from **100+ real NCDRC judgments**
* ⚖️ Applicable Consumer Protection Act provisions
* 📊 Deterministic confidence scoring
* 🧑‍⚖️ Human-in-the-loop lawyer review via UiPath Action Center
* 📱 Multi-language WhatsApp notifications
* 🗃️ Persistent case tracking using UiPath Data Fabric
* 📄 Structured legal reports for both victims and lawyers

---

# 🏗 Solution Architecture

```
Complaint Email
      │
      ▼
 Gmail Integration Service
      │
      ▼
Data Fabric Case Creation
      │
      ▼
LegalMitra AI Agent
(LangGraph + RAG)
      │
      ├──────────────┐
      ▼              ▼
Detailed Report   WhatsApp Summary
      │              │
      └──────┬───────┘
             ▼
 Victim Notification
             │
             ▼
 Lawyer Report
             │
             ▼
 Action Center Review
             │
      ┌──────┴────────┐
      ▼               ▼
Proceed          Settlement
      │               │
 Victim Updated   Case Closed
```

---

# 🧠 AI Agent Workflow

The LegalMitra AI Agent is implemented using **LangGraph** with a simple two-stage reasoning pipeline.

```
START
   │
   ▼
Retrieve Relevant Judgements
(Context Grounding)
   │
   ▼
Analyse Case
(Claude 4.5 Sonnet)
   │
   ▼
END
```

The agent performs:

* Semantic retrieval of similar consumer court judgments
* Legal reasoning
* Applicable law identification
* Confidence scoring
* Filing recommendation
* Structured JSON output

---

# 📚 Retrieval-Augmented Generation (RAG)

Knowledge Base:

* 100+ National Consumer Disputes Redressal Commission (NCDRC) judgments
* Stored as PDFs
* Indexed using UiPath Context Grounding
* Top-8 semantic matches retrieved for every complaint

Supported dispute categories include:

* Property possession delay
* Medical negligence
* Banking & CIBIL disputes
* E-commerce defects
* Health insurance claims
* Online education
* Telecom services
* Automobile defects
* Airline refunds
* Electricity billing

---

# ⚖️ Confidence Scoring

Each case is evaluated using five weighted legal criteria.

| Criterion               | Weight |
| ----------------------- | -----: |
| Case narration quality  |    30% |
| Precedent applicability |    25% |
| Legal provision clarity |    20% |
| Claim quantifiability   |    15% |
| Procedural compliance   |    10% |


# 📄 AI Output

For every complaint the agent produces:

* Case summary
* Applicable legal provisions
* Relevant precedents
* Legal analysis
* Key strengths
* Key weaknesses
* Recommended next steps
* Filing recommendation
* Confidence breakdown
* Filing decision rationale

---

# 🌍 Multi-Language Communication

Victims receive updates through WhatsApp in:

* English
* Hindi
* Native regional language

Regional language is automatically selected based on the detected city.

Examples include:

| City      | Language |
| --------- | -------- |
| Mumbai    | Marathi  |
| Pune      | Marathi  |
| Chennai   | Tamil    |
| Bengaluru | Kannada  |
| Hyderabad | Telugu   |
| Kolkata   | Bengali  |
| Ahmedabad | Gujarati |

---

# 👨‍⚖️ Human-in-the-Loop Review

The AI does **not** replace legal professionals.

Every medium-confidence case is routed to **UiPath Action Center**, where a lawyer decides whether to:

* Proceed with court filing
* Pursue an outside settlement

This keeps the final legal judgment with a human expert while allowing AI to automate research and documentation.

---

# 🛠 Technology Stack

## UiPath

* Maestro BPMN
* Integration Service(Twilio, Gmail)
* Context Grounding
* Data Fabric
* Action Center
* LLM Gateway

## AI

* LangGraph
* Claude 4.5 Sonnet
* Python

## Integrations

* Gmail
* Twilio WhatsApp
* Data Fabric
* DocuSign (future enhancement)

---

# 📂 Repository Structure

```
.
├── StudioWeb_Solutions/
├── main.py
└── README.md
```

---

# 📊 Results

| Activity             |        Before |          After |
| -------------------- | ------------: | -------------: |
| Legal research       |        90 min |         28 sec |
| Case analysis        |        60 min |         45 sec |
| Victim communication |        15 min |      Automated |
| Translation          | Manual / None |        Instant |
| **Total per case**   |  **~3 Hours** | **~8 Minutes** |

Overall reduction in processing time:

**≈95%**

---

# 🎯 Key Differentiators

* ✅ Grounded AI using real court judgments
* ✅ Human-in-the-loop legal review
* ✅ Multi-language legal communication
* ✅ End-to-end BPMN orchestration
* ✅ Automated legal research
* ✅ Explainable confidence scoring
* ✅ Persistent case lifecycle tracking

---

# 🔮 Future Enhancements

* Court document generation
* Legal notice generation using DocuSign
* Voice-based complaint registration
* Citizen portal for case tracking
* Additional Indian legal domains beyond consumer disputes

---

# 📜 License

This project was developed as part of **UiPath AgentHack 2026** for demonstration and educational purposes.

---

# 👨‍💻 Author

**Built by:** Ashish Rao

**Hackathon:** UiPath AgentHack 2026

**Track:** Maestro BPMN

**Domain:** Legal

---

> **LegalMitra — Every consumer deserves justice, regardless of where they live, which language they speak, or whether they can afford legal representation.**