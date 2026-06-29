from langchain_core.prompts import PromptTemplate
from uipath_langchain.chat.models import UiPathChat
from uipath_langchain.retrievers import ContextGroundingRetriever
from langgraph.graph import START, END, StateGraph, MessagesState
from dotenv import load_dotenv
from pydantic import BaseModel
import json
import re

load_dotenv()

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are LegalMitra, an expert Indian legal case analysis assistant specialising
in consumer protection law under the Consumer Protection Act 2019 (CPA 2019).

Your role is to assist independent lawyers and legal aid practitioners.
A complainant has emailed their dispute details in plain language.
They may not have attached formal documents — that is expected and normal.
Analyse what they have described and give a professional legal assessment.

════════════════════════════════════════════════════════════
MANDATORY OUTPUT FORMAT: JSON ONLY. NO TEXT OUTSIDE THIS.
════════════════════════════════════════════════════════════

Respond with ONLY the following JSON. No preamble. No markdown. No extra text.

{
  "case_summary": "<2-3 sentences: who is complaining, against whom, what happened, what relief is sought>",

  "applicable_legal_provisions": "<CPA 2019 sections that apply, each with a one-line explanation. Always include the deficiency/defect section, jurisdiction section, and relief section>",

  "relevant_precedents": "<summarise each retrieved judgement excerpt that applies to this case. Cite by case name and explain how it supports or weakens the case. If no excerpt is directly applicable, state the closest analogous principle>",

  "key_strengths": "<specific evidentiary, legal, and procedural strengths based on what the complainant has described. Reference actual facts from the case description>",

  "key_weaknesses": "<specific legal or factual gaps in the case narrative itself — not about missing attached documents. Focus on: weak causation, speculative damages, jurisdictional overlap, procedural non-compliance, or unclear facts>",

  "legal_analysis": "<substantive reasoning: how the law applies to these facts, what the precedents say, what a consumer forum would likely decide and why>",

  "recommended_next_steps": "<numbered action list: what the lawyer should do first, what to file, where, what to gather from the complainant if needed, what prayer clauses to include>",

  "recommended_action": "<one of exactly two values: DCDRC_FILE | LAWYER_NOTICE>",

  "recommended_action_reason": "<one sentence explaining this specific recommendation: why DCDRC directly vs why a lawyer notice first>",

  "confidence_scoring": {
    "case_narration_quality": <float 0.0-1.0: how specific, fact-rich, and detailed is the complaint description?>,
    "precedent_applicability": <float 0.0-1.0: how directly do retrieved judgements match this case type?>,
    "legal_provision_clarity": <float 0.0-1.0: how unambiguously does a CPA 2019 section apply?>,
    "claim_quantifiability": <float 0.0-1.0: are the losses clearly stated with amounts and basis?>,
    "procedural_compliance": <float 0.0-1.0: did the complainant follow pre-filing steps — complaint to company, legal notice if sent?>
  },

  "case_confidence": <float: (case_narration_quality*0.30) + (precedent_applicability*0.25) + (legal_provision_clarity*0.20) + (claim_quantifiability*0.15) + (procedural_compliance*0.10)>,

  "filing_decision": "<one of exactly three values: AUTO_FILE | HUMAN_REVIEW | REJECT>",

  "filing_decision_reason": "<one sentence explaining why this filing decision was reached>"
}

════════════════════════════════════════════════════════════
CONFIDENCE CRITERIA (score each criterion honestly)
════════════════════════════════════════════════════════════

case_narration_quality (weight 0.30):
  1.0 — Complainant provided specific dates, amounts, company name, what was
         purchased/contracted, what went wrong, prior complaint steps taken
  0.7 — Most facts present; 1-2 minor details vague
  0.4 — Key facts present but amounts, dates, or prior steps unclear
  0.1 — Vague narrative with no specific facts, amounts, or timeline

precedent_applicability (weight 0.25):
  1.0 — Retrieved excerpts directly address same dispute category, outcome favourable
  0.7 — Retrieved excerpts address analogous category with applicable principles
  0.4 — Retrieved excerpts from different category but establish general principle
  0.1 — No retrieved excerpt is applicable

legal_provision_clarity (weight 0.20):
  1.0 — Clear Section 2(7) defective goods OR 2(11) deficiency in service, unambiguous
  0.7 — Applicable section clear but jurisdictional overlap (RERA+CPA, RBI+CPA)
  0.4 — Section applies but scope contested
  0.1 — Unclear which provision applies

claim_quantifiability (weight 0.15):
  1.0 — Specific INR amounts stated for all loss heads
  0.7 — Primary amount stated; compensation/interest are reasonable estimates
  0.4 — Amounts vague or partially speculative
  0.1 — No specific amount mentioned

procedural_compliance (weight 0.10):
  1.0 — Complainant complained to company AND sent/implied legal notice, 30+ days elapsed
  0.7 — Complained to company, no formal legal notice yet but intent clear
  0.4 — Only informal complaint; unclear if company was given opportunity
  0.1 — No prior complaint to company mentioned

════════════════════════════════════════════════════════════
FILING DECISION THRESHOLDS (apply strictly)
════════════════════════════════════════════════════════════
  >= 0.80 -> AUTO_FILE   : Strong case, proceed per recommended_action without review
  0.55-0.79 -> HUMAN_REVIEW : Lawyer must review analysis before acting
  < 0.55 -> REJECT       : Advise against filing; explain why to complainant

════════════════════════════════════════════════════════════
RECOMMENDED ACTION (apply these rules)
════════════════════════════════════════════════════════════
  DCDRC_FILE   : Use when complainant has already sent legal notice (or 30 days
                 since company complaint), company has rejected or not responded,
                 and claim amount is within District Commission pecuniary limit
                 (up to Rs. 1 crore). Case is ready for direct forum filing.

  LAWYER_NOTICE: Use when no formal legal notice has been sent yet, OR when the
                 case needs a stronger pre-filing record, OR when the dispute
                 amount or complexity suggests a lawyer-drafted notice will
                 improve settlement chances before forum filing.
"""

# ── Schemas ───────────────────────────────────────────────────────────────────

class GraphInput(BaseModel):
    case_topic: str
    case_description: str

class GraphOutput(BaseModel):
    case_summary: str
    applicable_legal_provisions: str
    relevant_precedents: str
    key_strengths: str
    key_weaknesses: str
    legal_analysis: str
    recommended_next_steps: str
    recommended_action: str
    recommended_action_reason: str
    confidence_scoring: dict
    case_confidence: float
    filing_decision: str
    filing_decision_reason: str

class GraphState(MessagesState):
    case_topic: str
    case_description: str
    retrieved_context: str
    case_summary: str
    applicable_legal_provisions: str
    relevant_precedents: str
    key_strengths: str
    key_weaknesses: str
    legal_analysis: str
    recommended_next_steps: str
    recommended_action: str
    recommended_action_reason: str
    confidence_scoring: dict
    case_confidence: float
    filing_decision: str
    filing_decision_reason: str


# ── Node 1: retrieve_context ──────────────────────────────────────────────────

async def retrieve_context(state: GraphState) -> dict:
    """
    Queries CPACaseJudgements index (Shared folder) with k=8.
    Returns top-8 semantically similar judgement passages.
    Falls back gracefully — agent continues on retrieval failure.
    """
    retriever = ContextGroundingRetriever(
        index_name="CPACaseJudgements",
        folder_path="Shared",
        k=8
    )

    try:
        documents = await retriever.ainvoke(state["case_description"])
        if not documents:
            retrieved_context = (
                "No relevant judgement excerpts found. "
                "Set precedent_applicability to 0.1."
            )
        else:
            sections = []
            for i, doc in enumerate(documents, start=1):
                source = doc.metadata.get("source", f"Judgement excerpt {i}")
                sections.append(
                    f"[Excerpt {i} - Source: {source}]\n{doc.page_content}"
                )
            retrieved_context = "\n\n---\n\n".join(sections)
    except Exception as e:
        retrieved_context = (
            f"Retrieval error: {str(e)}. "
            "Set precedent_applicability to 0.1. "
            "Proceed on CPA 2019 general principles."
        )

    return {"retrieved_context": retrieved_context}


# ── Node 2: analyse_case ──────────────────────────────────────────────────────

def analyse_case(state: GraphState) -> dict:
    """
    Calls UiPathChat with system prompt, retrieved context, case_topic,
    case_description. Parses structured JSON into all 13 output fields.
    """
    llm = UiPathChat(
        model="anthropic.claude-sonnet-4-5-20250929-v1:0",
        temperature=0,
        max_tokens=16384,
        timeout=None,
        max_retries=2
    )

    prompt = PromptTemplate(
        input_variables=[
            "system_prompt", "case_topic",
            "case_description", "retrieved_context"
        ],
        template="""
{system_prompt}

CASE TOPIC:
{case_topic}

CASE DESCRIPTION:
{case_description}

RETRIEVED JUDGEMENT EXCERPTS:
(Score precedent_applicability honestly based on how directly these match.
Do not inflate if they are from a different dispute category.)

{retrieved_context}

Respond with ONLY the JSON object. No other text.
        """,
    )

    chain = prompt | llm
    response = chain.invoke({
        "system_prompt": SYSTEM_PROMPT,
        "case_topic": state["case_topic"],
        "case_description": state["case_description"],
        "retrieved_context": state["retrieved_context"],
    })

    response_text = (
        response.content if hasattr(response, "content") else str(response)
    )

    VALID_DECISIONS  = {"AUTO_FILE", "HUMAN_REVIEW", "REJECT"}
    VALID_ACTIONS    = {"DCDRC_FILE", "LAWYER_NOTICE"}

    try:
        cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", response_text).strip()
        parsed  = json.loads(cleaned)

        case_confidence = float(parsed.get("case_confidence", 0.0))
        case_confidence = max(0.0, min(1.0, case_confidence))

        filing_decision = parsed.get("filing_decision", "HUMAN_REVIEW").strip().upper()
        if filing_decision not in VALID_DECISIONS:
            if case_confidence >= 0.80:
                filing_decision = "AUTO_FILE"
            elif case_confidence >= 0.55:
                filing_decision = "HUMAN_REVIEW"
            else:
                filing_decision = "REJECT"

        recommended_action = parsed.get("recommended_action", "LAWYER_NOTICE").strip().upper()
        if recommended_action not in VALID_ACTIONS:
            recommended_action = "LAWYER_NOTICE"

        return {
            "case_summary":                 parsed.get("case_summary", ""),
            "applicable_legal_provisions":  parsed.get("applicable_legal_provisions", ""),
            "relevant_precedents":          parsed.get("relevant_precedents", ""),
            "key_strengths":                parsed.get("key_strengths", ""),
            "key_weaknesses":               parsed.get("key_weaknesses", ""),
            "legal_analysis":               parsed.get("legal_analysis", ""),
            "recommended_next_steps":       parsed.get("recommended_next_steps", ""),
            "recommended_action":           recommended_action,
            "recommended_action_reason":    parsed.get("recommended_action_reason", ""),
            "confidence_scoring":           parsed.get("confidence_scoring", {}),
            "case_confidence":              case_confidence,
            "filing_decision":              filing_decision,
            "filing_decision_reason":       parsed.get("filing_decision_reason", ""),
        }

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return {
            "case_summary":                 f"Parse error: {str(e)}",
            "applicable_legal_provisions":  "",
            "relevant_precedents":          "",
            "key_strengths":                "",
            "key_weaknesses":               "",
            "legal_analysis":               response_text,
            "recommended_next_steps":       "",
            "recommended_action":           "LAWYER_NOTICE",
            "recommended_action_reason":    "Defaulted due to parse error",
            "confidence_scoring":           {},
            "case_confidence":              0.0,
            "filing_decision":              "HUMAN_REVIEW",
            "filing_decision_reason":       f"Parse error during analysis: {str(e)}",
        }


# ── Graph ─────────────────────────────────────────────────────────────────────

builder = StateGraph(GraphState, input=GraphInput, output=GraphOutput)
builder.add_node("retrieve_context", retrieve_context)
builder.add_node("analyse_case", analyse_case)
builder.add_edge(START, "retrieve_context")
builder.add_edge("retrieve_context", "analyse_case")
builder.add_edge("analyse_case", END)
graph = builder.compile()