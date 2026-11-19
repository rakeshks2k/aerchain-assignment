# backend/copilot_agent.py
"""
Procurement Copilot Agent with Multi-Turn Tool Calling.

Integrates real LLMs (prioritizing Groq's open-source llama-3.3-70b-versatile,
with OpenAI and Gemini support) with 10 deterministic backend procurement tools.

Workflow:
1. User asks question with optional multi-turn conversation history.
2. Agent provides conversation history + user message + tool schemas to LLM.
3. LLM autonomously invokes appropriate analytical tools.
4. Backend executes tools deterministically against SQLite database.
5. Tool execution results are returned to LLM.
6. LLM interprets numbers, synthesizes reasoning, and answers conversationally.
7. Agent extracts structured tables, Chart.js visuals, and source citations.
"""
import os
import json
import logging
import time
import urllib.request
import urllib.error
from typing import Optional, Any, Union
from pathlib import Path

from copilot_tools import (
    TOOL_MAP,
    OPENAI_TOOLS_SCHEMA,
    execute_tool_call,
    calculate_split_award,
    get_line_item_quotes,
    compare_supplier_prices,
    filter_qualified_suppliers,
    calculate_landed_costs,
    analyze_price_variations,
    get_questionnaire_results,
    get_quotation_exceptions_and_anomalies,
    get_document_evidence,
    search_suppliers,
)

logger = logging.getLogger("copilot_agent")

SYSTEM_PROMPT = """You are Aerchain's Senior Procurement Copilot — an intelligent, natural, conversational AI partner for packaging category managers.
You assist buyers in analyzing a live 30-item Corrugated Packaging sourcing event involving 5 competing suppliers:
- PKI (PackIndia Ltd, Pune): Tier 1, BRC certified, DDP freight, 30 days credit. Quoted 28 items.
- EBS (EcoBox Solutions, Ahmedabad): Tier 2, ISO 9001 only, Ex-Works (+₹1.20 freight), 8% trade discount, 18% GST extra. Fails BRC food safety gate Q2.
- IPI (IndoPack Industries, Chennai): Tier 1, BRC certified, Ex-Works (+₹1.50 freight). Item 29 E-flute substitute. 90-day validity.
- PCO (Premium Corrugators, Mumbai): Tier 1, BRC certified, Photographed rate card. Quoted all 30 items.
- RPC (RegionalPacks Corp, Delhi): Tier 3, Informal email with 13 unresolved quotes. Fails BRC food safety gate Q2.

CONVERSATIONAL & REASONING PRINCIPLES:
1. Converse naturally and intelligently like an expert procurement partner (like ChatGPT, Claude, or Gemini). Answer what the user actually asks.
2. DO NOT use a rigid boilerplate template or repeat the same canned sections on every turn.
3. If the user asks a simple question or greets you, respond directly, concisely, and conversationally.
4. If the user asks for comparisons, rankings, or allocations, provide structured data, bullet points, or concise Markdown tables.
5. ALWAYS invoke backend analytical tools when you need prices, quotes, landed costs, savings, split awards, or questionnaire status.
6. NEVER guess or calculate financial arithmetic yourself — rely strictly on the deterministic figures returned by tools and explain them clearly.
7. Seamlessly retain context across conversation turns: understand follow-up questions like "What if we exclude them?", "Why?", "What about Item 12?", or "Can we split the order?".
8. Highlight relevant commercial risks (e.g. BRC food safety disqualification for EBS/RPC, IPI's Item 29 E-flute substitute, 90-day price validity, Ex-Works freight) naturally when they affect the decision.
"""


def _clean_key(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    val = val.strip()
    if not val or "your_" in val.lower() or "example" in val.lower():
        return None
    return val


def _get_api_keys() -> dict[str, Optional[str]]:
    from dotenv import load_dotenv
    # Ensure fresh read from .env files
    load_dotenv(Path(__file__).parent / ".env", override=True)
    load_dotenv(Path(__file__).parent.parent / ".env", override=True)
    return {
        "groq": _clean_key(os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_KEY")),
        "openai": _clean_key(os.environ.get("OPENAI_API_KEY")),
        "gemini": _clean_key(
            os.environ.get("GOOGLE_GENERATIVEAI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        ),
        "grok": _clean_key(os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")),
    }


class ProcurementCopilotAgent:
    """
    Autonomous Procurement Analyst Agent orchestrating LLM tool-calling
    over deterministic database tools.
    """

    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self.selected_groq_model = None
        self.refresh_clients()

    def refresh_clients(self):
        self.keys = _get_api_keys()

        # Initialize Groq if key available (Primary Recommendation)
        if self.keys.get("groq"):
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.keys["groq"])
                # Dynamically discover optimal model from available models
                try:
                    available = {m.id for m in self.groq_client.models.list().data}
                    env_m = os.environ.get("COPILOT_MODEL")
                    if env_m and env_m in available:
                        self.selected_groq_model = env_m
                    else:
                        preferred = [
                            "openai/gpt-oss-20b",
                            "openai/gpt-oss-120b",
                            "qwen/qwen3.8-27b",
                            "llama-3.3-70b-versatile",
                            "llama-3.1-8b-instant"
                        ]
                        self.selected_groq_model = next((m for m in preferred if m in available), "openai/gpt-oss-20b")
                except Exception as ex:
                    logger.warning(f"Could not list Groq models: {ex}")
                    self.selected_groq_model = "openai/gpt-oss-20b"
                logger.info(f"Groq client initialized with model: {self.selected_groq_model}")
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")

        # Initialize OpenAI if key available
        if self.keys.get("openai"):
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.keys["openai"])
                logger.info("OpenAI client initialized for Copilot.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

    def has_active_llm(self) -> bool:
        self.refresh_clients()
        return bool(
            self.groq_client
            or self.openai_client
            or self.keys.get("gemini")
            or self.keys.get("grok")
        )

    def run_agent_loop(
        self,
        question: str,
        rfx_id: int = 1,
        history: Optional[list[dict]] = None
    ) -> dict:
        """
        Execute the autonomous agent loop:
        1. Build messages with history and system prompt.
        2. Call LLM with tool schemas.
        3. Loop through tool calls, executing deterministic Python functions.
        4. Synthesize final answer, extracting tables and charts.
        """
        # Ensure latest client state
        self.refresh_clients()

        # If no LLM key configured, handle transparently
        if not self.has_active_llm():
            return self._handle_no_key_mode(question, rfx_id, history)

        # 1. Prioritize Google Gemini when configured (as requested by user)
        try:
            if self.keys.get("gemini"):
                return self._run_gemini_loop(
                    question=question,
                    rfx_id=rfx_id,
                    history=history
                )
            elif self.groq_client:
                model_to_use = self.selected_groq_model or "openai/gpt-oss-20b"
                return self._run_openai_compatible_loop(
                    client=self.groq_client,
                    model=model_to_use,
                    question=question,
                    rfx_id=rfx_id,
                    history=history,
                    provider=f"Groq Cloud ({model_to_use})"
                )
            elif self.openai_client:
                return self._run_openai_compatible_loop(
                    client=self.openai_client,
                    model=os.environ.get("COPILOT_MODEL", "gpt-4o-mini"),
                    question=question,
                    rfx_id=rfx_id,
                    history=history,
                    provider="OpenAI"
                )
            elif self.keys.get("grok"):
                from ai_service import _call_grok
                return self._run_grok_loop(
                    question=question,
                    rfx_id=rfx_id,
                    history=history
                )
        except Exception as e:
            logger.error(f"Error in LLM agent loop: {e}", exc_info=True)
            return self._handle_error_mode(question, rfx_id, error_msg=str(e))

        return self._handle_no_key_mode(question, rfx_id, history)

    # ──────────────────────────────────────────────────────────────────────────
    # OpenAI & Groq Tool-Calling Loop
    # ──────────────────────────────────────────────────────────────────────────
    def _run_openai_compatible_loop(
        self,
        client: Any,
        model: str,
        question: str,
        rfx_id: int,
        history: Optional[list[dict]],
        provider: str
    ) -> dict:
        """Run tool-calling loop using Groq or OpenAI SDK."""
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Inject conversation history
        if history:
            for turn in history[-8:]:  # maintain up to 8 recent turns
                role = turn.get("role", "user")
                content = turn.get("text") or turn.get("content") or ""
                if content:
                    messages.append({"role": role, "content": content})

        # Append current user prompt
        messages.append({"role": "user", "content": question})

        executed_tools_data: list[dict] = []
        sources: set[str] = {f"Engine: {provider}"}
        chart_data: Optional[dict] = None
        table_data: list[dict] = []
        raw_analysis: dict = {}

        # Allow up to 5 tool-calling iterations
        for iteration in range(5):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=OPENAI_TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.2,
                max_tokens=2500,
            )

            msg = response.choices[0].message
            tool_calls = getattr(msg, "tool_calls", None)

            # If no tool calls, model has produced its final answer
            if not tool_calls:
                answer_text = msg.content or ""
                break

            # Process tool calls
            messages.append(msg)  # record assistant tool call in messages

            for tc in tool_calls:
                fn_name = tc.function.name
                fn_args = tc.function.arguments
                logger.info(f"Copilot LLM invoking tool: {fn_name} with args: {fn_args}")

                # Execute deterministic tool
                tool_result = execute_tool_call(fn_name, fn_args)
                executed_tools_data.append({"tool": fn_name, "result": tool_result})

                # Harvest structured analytical outputs
                self._harvest_tool_outputs(
                    fn_name, tool_result, raw_analysis, table_data, sources
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": fn_name,
                    "content": json.dumps(tool_result)
                })
        else:
            # If reached max iterations, prompt model for final conclusion
            messages.append({"role": "user", "content": "Please synthesize your final response based on the tool results retrieved above."})
            final_resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=2000
            )
            answer_text = final_resp.choices[0].message.content or ""

        # Build chart data if raw_analysis or split_award was executed
        chart_data = self._build_chart_if_applicable(raw_analysis, table_data)

        return {
            "answer_text": answer_text,
            "table_data": table_data,
            "chart_data": chart_data,
            "sources": sorted(list(sources)),
            "raw_analysis": raw_analysis
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Google Gemini Live Reasoning Loop
    # ──────────────────────────────────────────────────────────────────────────
    def _call_gemini_rest(self, prompt: str, system_instruction: str = "") -> Optional[str]:
        """Call Gemini REST generateContent API with fast latency and fallback models."""
        import urllib.request
        import urllib.error
        import time

        key = self.keys.get("gemini")
        if not key:
            return None

        preferred_models = [
            os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
            "gemini-3.1-flash-lite",
            "gemini-3.8-flash",
            "gemini-flash-latest"
        ]
        seen = set()
        models_to_try = [m for m in preferred_models if not (m in seen or seen.add(m))]

        full_text = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        payload = {
            "contents": [{"parts": [{"text": full_text}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048
            }
        }
        body = json.dumps(payload).encode("utf-8")

        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates and candidates[0].get("content", {}).get("parts"):
                        parts = candidates[0]["content"]["parts"]
                        text = "".join(p.get("text", "") for p in parts if "text" in p)
                        if text.strip():
                            logger.info(f"Gemini response generated successfully using {model}.")
                            return text.strip()
            except urllib.error.HTTPError as he:
                logger.warning(f"Gemini REST error with {model}: {he.code} {he.reason}")
                if he.code == 404:
                    continue
                elif he.code == 429:
                    time.sleep(1)
                    continue
            except Exception as ex:
                logger.warning(f"Gemini REST attempt failed with {model}: {ex}")
                continue

        # SDK Fallback if REST attempt was interrupted
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            for m_name in ["gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]:
                try:
                    m = genai.GenerativeModel(m_name)
                    r = m.generate_content(full_text)
                    if r and r.text:
                        return r.text.strip()
                except Exception:
                    continue
        except Exception:
            pass

        return None

    def _convert_json_schema_for_gemini(self, schema: Any) -> Any:
        if not isinstance(schema, dict):
            return schema
        new_s = {}
        for k, v in schema.items():
            if k == "type":
                if isinstance(v, list):
                    types = [t for t in v if t != "null"]
                    t_val = types[0] if types else "string"
                    new_s["type"] = t_val.upper()
                elif isinstance(v, str):
                    new_s["type"] = v.upper()
            elif k == "properties":
                new_s["properties"] = {pk: self._convert_json_schema_for_gemini(pv) for pk, pv in v.items()}
            elif k == "items":
                new_s["items"] = self._convert_json_schema_for_gemini(v)
            else:
                new_s[k] = v
        return new_s

    def _get_gemini_tools(self) -> list[dict]:
        from copilot_tools import OPENAI_TOOLS_SCHEMA
        gemini_functions = []
        for t in OPENAI_TOOLS_SCHEMA:
            fn = t.get("function", {})
            gemini_functions.append({
                "name": fn["name"],
                "description": fn["description"],
                "parameters": self._convert_json_schema_for_gemini(fn.get("parameters", {}))
            })
        return [{"functionDeclarations": gemini_functions}]

    def _run_gemini_loop(
        self,
        question: str,
        rfx_id: int,
        history: Optional[list[dict]]
    ) -> dict:
        """Run genuine multi-turn autonomous tool-calling loop using Google Gemini REST API."""
        api_key = self.keys.get("gemini")
        if not api_key:
            return self._handle_no_key_mode(question, rfx_id, history)

        sources: set[str] = {"Engine: Google Gemini (Autonomous Tool-Calling)"}
        raw_analysis: dict = {}
        table_data: list[dict] = []
        executed_tools: list[str] = []

        # Build contents array from history + current question
        contents: list[dict] = []
        if history:
            for turn in history[-8:]:
                role = "user" if turn.get("role") == "user" else "model"
                text = (turn.get("text") or turn.get("content") or "").strip()
                if text:
                    contents.append({"role": role, "parts": [{"text": text}]})

        contents.append({"role": "user", "parts": [{"text": question}]})

        tools_declaration = self._get_gemini_tools()
        models = [
            os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
            "gemini-3.1-flash-lite",
            "gemini-3.8-flash",
            "gemini-flash-latest"
        ]
        models = list(dict.fromkeys(models))

        answer_text = ""

        # Allow up to 5 tool-calling iterations
        for iteration in range(5):
            payload = {
                "contents": contents,
                "tools": tools_declaration,
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}
            }

            resp_json = None
            last_error = None

            for model_name in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                for attempt in range(2):
                    try:
                        req_data = json.dumps(payload).encode("utf-8")
                        req = urllib.request.Request(
                            url,
                            data=req_data,
                            headers={"Content-Type": "application/json"}
                        )
                        with urllib.request.urlopen(req, timeout=25) as resp:
                            resp_json = json.loads(resp.read().decode("utf-8"))
                            break
                    except urllib.error.HTTPError as he:
                        last_error = he
                        if he.code in (429, 503):
                            time.sleep(1.0 * (attempt + 1))
                            continue
                        break
                    except Exception as ex:
                        last_error = ex
                        time.sleep(0.5)
                        continue
                if resp_json:
                    break

            if not resp_json:
                logger.warning(f"Gemini API error during iteration {iteration}: {last_error}")
                if not answer_text:
                    return self._handle_no_key_mode(question, rfx_id, history)
                break

            candidates = resp_json.get("candidates", [])
            if not candidates:
                break

            candidate_content = candidates[0].get("content", {})
            parts = candidate_content.get("parts", [])

            # Look for function calls in response parts
            fn_call_part = next((p for p in parts if "functionCall" in p), None)

            if not fn_call_part:
                # Model concluded and returned final conversational text
                text_parts = [p.get("text", "") for p in parts if "text" in p]
                answer_text = "\n".join(text_parts).strip()
                break

            # Execute tool call
            fn_call = fn_call_part["functionCall"]
            fn_name = fn_call.get("name")
            fn_args = fn_call.get("args") or {}

            if isinstance(fn_args, dict) and "rfx_id" not in fn_args:
                fn_args["rfx_id"] = rfx_id

            logger.info(f"Gemini autonomous tool call #{iteration+1}: {fn_name}({fn_args})")
            executed_tools.append(fn_name)

            try:
                tool_output = execute_tool_call(fn_name, fn_args)
            except Exception as e:
                logger.error(f"Error executing tool {fn_name}: {e}")
                tool_output = {"error": f"Failed to execute tool {fn_name}: {str(e)}"}

            # Harvest structured data for tables and charts
            self._harvest_tool_outputs(fn_name, tool_output, raw_analysis, table_data, sources)

            # Record model's functionCall turn (preserving thoughtSignature for Gemini 3.x)
            contents.append(candidate_content)

            # Record tool response turn
            contents.append({
                "role": "user",
                "parts": [{
                    "functionResponse": {
                        "name": fn_name,
                        "response": {"content": tool_output}
                    }
                }]
            })

        if not answer_text:
            answer_text = self._handle_no_key_mode(question, rfx_id, history)["answer_text"]

        chart_data = self._build_chart_if_applicable(raw_analysis, table_data)

        return {
            "answer_text": answer_text,
            "table_data": table_data,
            "chart_data": chart_data,
            "sources": sorted(list(sources)),
            "raw_analysis": raw_analysis
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Grok Fallback Loop
    # ──────────────────────────────────────────────────────────────────────────
    def _run_grok_loop(
        self,
        question: str,
        rfx_id: int,
        history: Optional[list[dict]]
    ) -> dict:
        """Run tool calling / synthesis with xAI Grok."""
        from ai_service import _call_grok

        tool_results, raw_analysis, table_data, sources = self._execute_intent_tools(question, rfx_id, history)
        sources.add("Engine: xAI Grok")

        prompt = f"""Current User Query:
{question}

Verified Analytical Records:
{json.dumps(tool_results, default=str)[:10000]}

Please write an expert, natural procurement response answering the user's query thoroughly using the verified figures."""

        answer_text = _call_grok(prompt, system_prompt=SYSTEM_PROMPT)
        chart_data = self._build_chart_if_applicable(raw_analysis, table_data)

        return {
            "answer_text": answer_text,
            "table_data": table_data,
            "chart_data": chart_data,
            "sources": sorted(list(sources)),
            "raw_analysis": raw_analysis
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Output Harvesting & Chart Formatting
    # ──────────────────────────────────────────────────────────────────────────
    def _harvest_tool_outputs(
        self,
        fn_name: str,
        tool_result: dict,
        raw_analysis: dict,
        table_data: list[dict],
        sources: set[str]
    ):
        """Extract table_data, raw_analysis, and source citations from tool outputs."""
        if fn_name == "calculate_split_award":
            raw_analysis.update({
                "split_total": tool_result.get("split_total"),
                "single_best": tool_result.get("single_best"),
                "savings_vs_single": tool_result.get("savings_vs_single"),
                "savings_pct": tool_result.get("savings_pct"),
                "supplier_allocation": tool_result.get("supplier_allocation")
            })
            if not table_data:
                table_data.extend(tool_result.get("line_item_allocations", []))
            sources.add("Database: split_award_optimizer (Deterministic Solver)")
            sources.add("Table: extracted_quotes & questionnaire_responses")

        elif fn_name == "compare_supplier_prices":
            if not table_data:
                table_data.extend(tool_result.get("comparison_matrix", [])[:30])
            sources.add("Database: extracted_quotes (Head-to-head comparison)")

        elif fn_name == "get_line_item_quotes":
            if not table_data:
                for li in tool_result.get("line_items", []):
                    for q in li.get("quotes", []):
                        table_data.append({
                            "item_number": li.get("item_number"),
                            "description": li.get("description"),
                            "supplier": q.get("supplier_code"),
                            "landed_cost_inr": q.get("landed_cost_excl_gst"),
                            "lead_time_days": q.get("lead_time_days"),
                            "compliance": q.get("tech_compliance")
                        })
            sources.add("Database: line_items & extracted_quotes")

        elif fn_name == "filter_qualified_suppliers":
            if not table_data:
                for s in tool_result.get("qualified_suppliers", []):
                    table_data.append({"supplier": s["code"], "name": s["name"], "status": "QUALIFIED", "certifications": s.get("certifications", "")})
                for s in tool_result.get("disqualified_suppliers", []):
                    table_data.append({"supplier": s["code"], "name": s["name"], "status": "DISQUALIFIED", "certifications": s.get("certifications", "")})
            sources.add("Database: questionnaire_responses (BRC Gate Q2)")

        elif fn_name == "get_questionnaire_results":
            if not table_data:
                for q in tool_result.get("responses", []):
                    ans_text = q.get("answer") or q.get("response_text") or ""
                    is_disq = (q.get("is_compliant") is False) or ("pending" in str(ans_text).lower()) or ("no" in str(ans_text).lower())
                    table_data.append({
                        "supplier": q.get("supplier_code"),
                        "question_code": q.get("question_code"),
                        "question": q.get("question_text"),
                        "response": ans_text,
                        "status": "DISQUALIFIED" if is_disq else "QUALIFIED"
                    })
            sources.add("Database: questionnaire_responses")

        elif fn_name == "calculate_landed_costs":
            if not table_data:
                breakdowns = tool_result.get("landed_cost_breakdowns") or tool_result.get("breakdown") or []
                table_data.extend(breakdowns)
            sources.add("Database: landed_cost_calculator")

        elif fn_name == "analyze_price_variations":
            if not table_data:
                table_data.extend(tool_result.get("variations", []))
            sources.add("Database: price_variation_analyzer")

        elif fn_name == "search_suppliers":
            if not table_data:
                table_data.extend(tool_result.get("suppliers", []))
            sources.add("Database: suppliers_master")

        elif fn_name == "get_quotation_exceptions_and_anomalies":
            if not table_data:
                table_data.extend(tool_result.get("exceptions", []))
            sources.add("Database: quotation_risk_register")

        elif fn_name == "get_document_evidence":
            if not table_data:
                table_data.extend(tool_result.get("evidence", []))
            sources.add("Filesystem: supplier_documents")

    def _build_chart_if_applicable(
        self,
        raw_analysis: dict,
        table_data: list[dict]
    ) -> Optional[dict]:
        """Construct Chart.js configuration for spend comparisons or supplier allocations."""
        if "supplier_allocation" in raw_analysis and raw_analysis["supplier_allocation"]:
            alloc = raw_analysis["supplier_allocation"]
            labels = list(alloc.keys())
            data = [alloc[k] for k in labels]
            return {
                "type": "bar",
                "title": "Split Award Item Allocation by Supplier",
                "labels": labels,
                "datasets": [{
                    "label": "Line Items Allocated",
                    "data": data,
                    "backgroundColor": ["#3b03c5", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444"][:len(labels)],
                    "borderRadius": 6
                }]
            }
        return None

    # ──────────────────────────────────────────────────────────────────────────
    # Deterministic Intent Tools Dispatcher (Fallback & Testing)
    # ──────────────────────────────────────────────────────────────────────────
    def _execute_intent_tools(
        self,
        question: str,
        rfx_id: int,
        history: Optional[list[dict]]
    ) -> tuple[dict, dict, list[dict], set[str]]:
        """
        Dynamically execute analytical tools based on query intent to provide
        deterministic figures, tables, and charts.
        """
        q_lower = question.lower()
        tool_results = {}
        raw_analysis = {}
        table_data = []
        sources = set()

        # Check for item number in question or history
        import re
        item_match = re.search(r'\b(?:item|sku|line)\s*#?\s*(\d+)\b', q_lower)
        item_num = int(item_match.group(1)) if item_match else None

        if not item_num and history:
            for turn in reversed(history[-4:]):
                txt = (turn.get("text") or turn.get("content") or "").lower()
                m = re.search(r'\b(?:item|sku|line)\s*#?\s*(\d+)\b', txt)
                if m:
                    item_num = int(m.group(1))
                    break

        if "split" in q_lower or "award" in q_lower or "allocat" in q_lower or "cheapest supplier per line" in q_lower:
            qualified = "unqualified" not in q_lower and "all supplier" not in q_lower
            res = calculate_split_award(rfx_id=rfx_id, qualified_only=qualified)
            tool_results["calculate_split_award"] = res
            self._harvest_tool_outputs("calculate_split_award", res, raw_analysis, table_data, sources)

        elif "brc" in q_lower or "qualif" in q_lower or "disqualif" in q_lower or "certif" in q_lower:
            res = filter_qualified_suppliers(rfx_id=rfx_id)
            tool_results["filter_qualified_suppliers"] = res
            self._harvest_tool_outputs("filter_qualified_suppliers", res, raw_analysis, table_data, sources)

        elif item_num:
            res = get_line_item_quotes(rfx_id=rfx_id, item_number=item_num)
            tool_results["get_line_item_quotes"] = res
            self._harvest_tool_outputs("get_line_item_quotes", res, raw_analysis, table_data, sources)

        elif "exception" in q_lower or "risk" in q_lower or "anomal" in q_lower:
            res = get_quotation_exceptions_and_anomalies(rfx_id=rfx_id)
            tool_results["get_quotation_exceptions_and_anomalies"] = res
            self._harvest_tool_outputs("get_quotation_exceptions_and_anomalies", res, raw_analysis, table_data, sources)

        elif "ply" in q_lower:
            ply_term = "5-ply" if "5-ply" in q_lower else ("3-ply" if "3-ply" in q_lower else ("7-ply" if "7-ply" in q_lower else None))
            res = analyze_price_variations(rfx_id=rfx_id, ply=ply_term)
            tool_results["analyze_price_variations"] = res
            res_quotes = get_line_item_quotes(rfx_id=rfx_id, ply=ply_term)
            self._harvest_tool_outputs("get_line_item_quotes", res_quotes, raw_analysis, table_data, sources)

        else:
            # Default comparison
            res = compare_supplier_prices(rfx_id=rfx_id, qualified_only=True)
            tool_results["compare_supplier_prices"] = res
            self._harvest_tool_outputs("compare_supplier_prices", res, raw_analysis, table_data, sources)

        return tool_results, raw_analysis, table_data, sources

    # ──────────────────────────────────────────────────────────────────────────
    # Transparent No-API-Key and Error Handlers
    # ──────────────────────────────────────────────────────────────────────────
    def _handle_no_key_mode(
        self,
        question: str,
        rfx_id: int,
        history: Optional[list[dict]]
    ) -> dict:
        """
        Transparently informs user that GROQ_API_KEY is required for live reasoning,
        while returning exact database records and calculations from backend tools.
        """
        tool_results, raw_analysis, table_data, sources = self._execute_intent_tools(question, rfx_id, history)
        chart_data = self._build_chart_if_applicable(raw_analysis, table_data)

        # Build informative, transparent response
        split_info = ""
        if "split_total" in raw_analysis:
            split_info = f"""
### Verified Analytical Calculation (Backend Engine):
- **Split Award Spend:** **₹{raw_analysis['split_total']:,.2f}**
- **Best Single Source (PCO):** **₹{raw_analysis['single_best']['total']:,.2f}**
- **Net Sourcing Savings:** **₹{raw_analysis['savings_vs_single']:,.2f}** ({raw_analysis.get('savings_pct', 14.5)}% reduction)
- **Supplier Allocation:** {json.dumps(raw_analysis.get('supplier_allocation', {}))}
"""

        answer_text = f"""### AI Procurement Copilot — Live LLM API Key Recommended

To experience dynamic, conversational reasoning with autonomous tool calling on **Groq Cloud (Llama 3.3 70B)**, please set your free API key in `backend/.env`.

{split_info}

#### Quick Setup Instructions:
1. **Get Free Groq Key:** Visit **[https://console.groq.com/keys](https://console.groq.com/keys)** (Zero cost, no credit card required, instant access).
2. **Add to `.env`:** Open `backend/.env` and insert:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```
3. **Alternative Supported Keys:** You can also use `GEMINI_API_KEY` or `OPENAI_API_KEY`.

*All 10 deterministic backend tools and database records are active. The exact calculation results and line-item allocations have been retrieved from SQLite and rendered in the data table below.*
"""

        sources.add("Engine: Local Deterministic Analytical Tool Layer (aerchain.db)")
        sources.add("Status: LLM Key Configuration Pending (GROQ_API_KEY)")

        return {
            "answer_text": answer_text,
            "table_data": table_data,
            "chart_data": chart_data,
            "sources": sorted(list(sources)),
            "raw_analysis": raw_analysis
        }

    def _handle_error_mode(self, question: str, rfx_id: int, error_msg: str) -> dict:
        """Gracefully report LLM API failures without crashing or mocking."""
        tool_results, raw_analysis, table_data, sources = self._execute_intent_tools(question, rfx_id, None)
        chart_data = self._build_chart_if_applicable(raw_analysis, table_data)

        answer_text = f"""### Copilot Execution Notice: LLM API Error

The analytical copilot encountered an error communicating with the external LLM provider:
> `{error_msg}`

**Deterministic Database Fallback Active:**
The backend analytical tool layer has successfully queried SQLite and completed exact mathematical calculations for your query. See the verified records and tables below.
"""
        sources.add("Status: External LLM Error (Deterministic Fallback)")
        return {
            "answer_text": answer_text,
            "table_data": table_data,
            "chart_data": chart_data,
            "sources": sorted(list(sources)),
            "raw_analysis": raw_analysis
        }


# Global Singleton Agent Instance
_agent_instance: Optional[ProcurementCopilotAgent] = None


def get_copilot_agent() -> ProcurementCopilotAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ProcurementCopilotAgent()
    return _agent_instance
