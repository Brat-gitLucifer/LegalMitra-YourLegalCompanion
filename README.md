# ⚖️ LegalMitra – AI-Powered Consumer Dispute Analysis & Legal Routing

> **UiPath AgentHack 2026 | Track: Maestro BPMN | Domain: Legal**

LegalMitra is an AI-powered legal assistant that analyzes consumer complaints, researches relevant legal precedents using Retrieval-Augmented Generation (RAG), and assists lawyers in deciding whether a case should proceed to court or be settled outside. Built on **UiPath Maestro BPMN**, it combines a UiPath Coded Agent, platform-native AI services, and human-in-the-loop review to dramatically reduce legal research time while making legal assistance accessible in multiple Indian languages.

---

## 🚀 Project Description — Problem & Solution

India receives roughly 5 million consumer complaints every year, and a large share of complainants — especially in Tier-2 and Tier-3 cities — have no practical access to legal help. The barriers are not legal, they are structural:

* Limited access to affordable lawyers outside major cities
* Legal communication happens almost entirely in English
* Legal research (finding applicable law and precedent) takes hours per case
* No structured way to know upfront whether a complaint is even worth pursuing

**LegalMitra solves this end-to-end.** A victim emails their complaint. A UiPath Coded Agent reads the complaint, retrieves the most relevant judgments from a curated knowledge base of 100+ real NCDRC (National Consumer Disputes Redressal Commission) cases using Retrieval-Augmented Generation, and produces a structured legal analysis — applicable law, precedent, strengths, weaknesses, a confidence score, and a filing recommendation. The victim is immediately notified in plain language over WhatsApp in **English, Hindi, and their regional language**. The lawyer receives the full structured report and reviews it in **UiPath Action Center**, deciding whether to proceed to court or pursue settlement. The victim is notified of the outcome and the case lifecycle is tracked end-to-end in **UiPath Data Fabric**.

The result: legal research and drafting that took ~3 hours per case now completes in ~8 minutes — with a qualified human still making the final legal call.

---

## 🧩 UiPath Components Used

| Component | Role in the Solution |
|---|---|
| **UiPath Maestro (BPMN)** | End-to-end process orchestration — intake, agent invocation, notification fan-out, lawyer review gateway, closure |
| **Coded Agents** | The LegalMitra AI Agent — a Python LangGraph agent performing RAG-based legal analysis (see *Agent Type* below) |
| **UiPath Apps** | `VictimCaseReview.uiapp` — the Action Center interface lawyers use for the human-in-the-loop review and Proceed/Settle decision |
| **Integration Service — Gmail** | Trigger on incoming complaint email; sends case reports and notifications to victim and lawyer |
| **Integration Service — Twilio** | Sends multi-language (English/Hindi/Regional) WhatsApp summaries to the victim |
| **Integration Service — Data Fabric** | Persistent case entity — stores complaint details, agent output, lawyer decision, and case status across the entire lifecycle |
| **Context Grounding** | Hosts the `CPACaseJudgements` semantic index over 100+ NCDRC judgment PDFs; the agent retrieves top-8 relevant precedents per case |
| **Gen AI Activities / LLM Gateway** | Routes the agent's LLM calls (Claude) through UiPath's managed LLM Gateway |
| **Orchestrator** | Hosts the Storage Bucket, the Context Grounding Index, the published Coded Agent, and the deployed UiPath App |

---

## 🤖 Agent Type

**This solution uses a Coded Agent — not a Low-Code Agent.**

The LegalMitra AI Agent (`main.py`) is built with **LangGraph** as a two-node Python graph (`retrieve_context` → `analyse_case`), using `uipath-langchain` to connect to UiPath's Context Grounding (RAG retrieval) and LLM Gateway (Claude). It is packaged and published as a UiPath Coded Agent via the `uipath` CLI and invoked from the Maestro BPMN process as an agent task.

No Low-Code/Agent Builder agents are used in this solution.

---

## 🏗 Solution Architecture

```
Complaint Email
      │
      ▼
 Gmail Integration Service (trigger)
      │
      ▼
Data Fabric Case Creation
      │
      ▼
LegalMitra Coded Agent
(LangGraph + Context Grounding RAG)
      │
      ├──────────────┐
      ▼              ▼
Detailed Report   WhatsApp Summary
 (Victim email)   (EN / HI / Regional)
      │              │
      └──────┬───────┘
             ▼
      Lawyer Report (Email)
             │
             ▼
 UiPath App — Action Center Review
             │
      ┌──────┴────────┐
      ▼               ▼
  Proceed         Settlement
      │               │
Victim Notified   Case Closed
(Email + WhatsApp)  (Data Fabric)
```

---

## 🧠 Coded Agent — Internal Workflow

```
START
   │
   ▼
retrieve_context
(Context Grounding — top-8 semantic matches)
   │
   ▼
analyse_case
(Claude via UiPath LLM Gateway)
   │
   ▼
END
```

The agent performs:

* Semantic retrieval of similar consumer court judgments
* Legal reasoning grounded in retrieved precedent
* Applicable Consumer Protection Act 2019 provision identification
* Five-criterion weighted confidence scoring
* Filing recommendation (proceed / settle)
* Structured JSON output consumed directly by the Maestro process

---

## 📚 Retrieval-Augmented Generation (RAG)

**Knowledge Base:**

* 100+ National Consumer Disputes Redressal Commission (NCDRC) judgments
* Stored as PDFs in a UiPath Storage Bucket
* Indexed using UiPath Context Grounding (`CPACaseJudgements`)
* Top-8 semantic matches retrieved for every complaint

**Supported dispute categories:**

Property possession delay · Medical negligence · Banking & CIBIL disputes · E-commerce defects · Health insurance claims · Online education · Telecom services · Automobile defects · Airline refunds · Electricity billing

---

## ⚖️ Confidence Scoring

Each case is evaluated using five weighted legal criteria:

| Criterion | Weight |
|---|---:|
| Case narration quality | 30% |
| Precedent applicability | 25% |
| Legal provision clarity | 20% |
| Claim quantifiability | 15% |
| Procedural compliance | 10% |

---

## 📄 Agent Output

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

## 🌍 Multi-Language Communication

Victims receive updates via WhatsApp in English, Hindi, and their native regional language — automatically selected based on the detected city (e.g. Mumbai/Pune → Marathi, Chennai → Tamil, Bengaluru → Kannada, Hyderabad → Telugu, Kolkata → Bengali, Ahmedabad → Gujarati).

---

## 👨‍⚖️ Human-in-the-Loop Review

The AI does **not** replace legal professionals. Every case is routed to a lawyer in the **UiPath App (Action Center)**, where they review the agent's full analysis and decide to **Proceed with court filing** or **Pursue an outside settlement**. The final legal judgment always rests with a human; the AI automates research, analysis, and documentation only.

---

## 🛠 Technology Stack

**UiPath:** Maestro (BPMN) · Coded Agents · UiPath Apps · Integration Service (Gmail, Twilio, Data Fabric) · Context Grounding · Gen AI Activities / LLM Gateway · Orchestrator

**AI / Code:** LangGraph · `uipath-langchain` · Claude (via UiPath LLM Gateway) · Python

**External Integrations:** Gmail · Twilio WhatsApp · DocuSign (future enhancement)

---

## 📂 Repository Structure

```
.
├── StudioWeb_Solutions/
│   ├── LegalMitra-YourLegalCompanion.uis    # Maestro BPMN process
│   ├── VictimCaseReview.uiapp               # Lawyer review UiPath App
│   └── [Coded Agent package]                # Published agent NuGet package
├── main.py                                  # Coded Agent source (LangGraph)
├── input.json                               # Sample input for local agent test run
└── README.md
```

---

## ⚙️ Setup Instructions — How to Run This Solution

Follow these steps in order. This solution requires an active UiPath Automation Cloud tenant with Orchestrator, Integration Service, Context Grounding, and Maestro enabled.

### 1. Set up the RAG knowledge base
1. In **Orchestrator → Shared folder**, create a **Storage Bucket** (any name of your choice).
2. Upload all files from `All_Case_Documents_ForIndexing.zip` into that bucket.
3. Access `All_Case_Documents_ForIndexing.zip` via https://drive.google.com/file/d/1HfdKbZwCZNa6urc8mpQbh0EKHkWh3Da3/view?usp=drive_link
4. In **Orchestrator → Shared folder**, create a **Context Grounding Index** named exactly **`CPACaseJudgements`**, sourced from the Storage Bucket created above.
   > Both the Storage Bucket and the Index **must** be created in the **Shared** folder — the agent references the index by this exact name and folder.

### 2. Create Integration Service connections
In **Integration Service**, create connections for:
* **Gmail** (used for complaint intake trigger and email notifications)
* **Twilio** (used for WhatsApp notifications)
* **Data Fabric** (used for case entity persistence)

### 3. Set up and publish the Coded Agent
1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install dependencies, including `uipath-langchain`.
4. Authenticate the UiPath CLI:
   ```bash
   uipath auth --base-url [YOUR ENVIRONMENT URL]
   ```
5. Initialize the agent project:
   ```bash
   uipath init
   ```
6. (Optional — local test before publishing) Run the agent locally against the provided sample input:
   ```bash
   uipath run agent -f input.json
   ```
7. Package the agent:
   ```bash
   uipath pack
   ```
8. Publish the agent to Orchestrator:
   ```bash
   uipath publish -f [FOLDER PATH]
   ```
   > A pre-built Coded Agent NuGet package is also included in `StudioWeb_Solutions/` — you may publish this directly instead of building from source if you prefer.

### 4. Deploy the UiPath App
Deploy `VictimCaseReview.uiapp` (located in `StudioWeb_Solutions/`) to your Orchestrator tenant. This app powers the lawyer's human-in-the-loop review step.

### 5. Import and configure the Maestro process
1. In **Studio Web**, import `LegalMitra-YourLegalCompanion.uis` from `StudioWeb_Solutions/`.
2. Once the Coded Agent and UiPath App are deployed, configure the corresponding nodes in the imported process:
   * Bind the **Coded Agent** task to the agent published in Step 3.
   * Bind the **UiPath App** task to `VictimCaseReview` deployed in Step 4.
   * Bind the **Gmail**, **Twilio**, and **Data Fabric** connections created in Step 2.
3. Hit **Debug** — the end-to-end process will now run in your environment: complaint email in → Coded Agent analysis → multi-language WhatsApp + email notifications → lawyer review in the UiPath App → final routing and case closure.

---

## 📊 Results

| Activity | Before | After |
|---|---:|---:|
| Legal research | 90 min | 28 sec |
| Case analysis | 60 min | 45 sec |
| Victim communication | 15 min | Automated |
| Translation | Manual / None | Instant |
| **Total per case** | **~3 hours** | **~8 minutes** |

**Overall reduction in processing time: ≈95%**

---

## 🎯 Key Differentiators

* ✅ Grounded AI using real court judgments (Context Grounding RAG, not model memory)
* ✅ Human-in-the-loop legal review via UiPath App / Action Center
* ✅ Multi-language legal communication (English, Hindi, regional)
* ✅ End-to-end Maestro BPMN orchestration
* ✅ Coded Agent architecture — transparent, debuggable, version-controlled
* ✅ Explainable, weighted confidence scoring
* ✅ Persistent case lifecycle tracking in Data Fabric

---

## 🔮 Future Enhancements

* Court document generation
* Legal notice generation and e-signature via DocuSign
* Voice-based complaint registration
* Citizen portal for case tracking
* Additional Indian legal domains beyond consumer disputes

---

## 🧰 Coding Tools Used in Development

* **Claude Chat** — solution planning, architecture design, LangChain/LangGraph code development
* **ChatGPT** — document preparation
* **Gemini Images** — YouTube and project thumbnail generation
* **Claude & Antigravity** — coded agent local run and debugging
* **UiPath Studio Web Autopilot (Helix, Claude Opus)** — assisted design of the Maestro BPMN flow diagram

---

## 📜 License

This project was developed as part of **UiPath AgentHack 2026** for demonstration and educational purposes.

---

## 👨‍💻 Author

**Built by:** Ashish Rao
**Hackathon:** UiPath AgentHack 2026
**Track:** Maestro BPMN
**Domain:** Legal

---

> **LegalMitra — Every consumer deserves justice, regardless of where they live, which language they speak, or whether they can afford legal representation.**