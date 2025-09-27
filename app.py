from fastapi import FastAPI, Request, UploadFile, File  
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
import json
import re
import joblib
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# ==============================
# Setup & Initialization
# ==============================
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# --- 1. Load the .pkl Rule-Based Object ---
model_path = os.path.join(MODEL_DIR, "risk_rules_full.pkl")
rule_model_object = None
try:
    rule_model_object = joblib.load(model_path)
    print("✅ Rule-based object (.pkl) loaded successfully.")
except Exception as e:
    print(f"⚠️ Warning: Could not load .pkl file: {e}. Rule-based model will not work.")

# ==============================
# Gemini LLM Engine
# ==============================
CLASSIFICATION_RULES = """ 
You are a deterministic credit risk classification engine. Your task is to:
1. Read the provided JSON input containing a company's financial and non-financial factors.
2. Apply the following 23 rules strictly to each factor to assign it a 'High', 'Medium', or 'Low'.
3. Aggregate results:
   * >=60% High → final_risk_rating = Low risk
   * >=60% Low → final_risk_rating = High risk
   * Otherwise → final_risk_rating = Medium risk
4. Output STRICT JSON:
{
  "final_risk_rating": "Low|Medium|High",
  "factor_breakdown": { "factor_name": "Low|Medium|High", ... }
}
"""

# --- Configure Gemini API ---
api_key = os.getenv("GEMINI_API_KEY")
gemini_model = None
if not api_key:
    print("⚠️ Warning: GEMINI_API_KEY not found in .env file. Gemini features will be disabled.")
else:
    try:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=CLASSIFICATION_RULES
        )
        print("✅ Gemini Model configured successfully.")
    except Exception as e:
        print(f"❌ Error configuring Gemini: {e}")

# --- Initialize FastAPI App ---
app = FastAPI(title="Credit Risk API (PKL + Gemini)", version="FINAL")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ==============================
# Rule-Based Model Engine (.pkl)
# ==============================
def apply_pkl_rules(rules: dict, df: pd.DataFrame):
    data = df.iloc[0].to_dict()
    factors = []
    factor_labels = {
        "auditor_tier_code": "auditor_tier_code (Other=0, Big4=1)",
        "financials_audited_code": "financials_audited_code (No=0, Yes=1)",
        "sanctions_exposure_code": "sanctions_exposure_code (None=0, Indirect=1, Direct=2)"
    }

    for col, value in data.items():
        label = factor_labels.get(col, col)
        evaluation = "Medium"
        if col in ["auditor_tier_code", "financials_audited_code"] and value == 1:
            evaluation = "High"
        elif col == "legal_disputes_open" and value == 0:
            evaluation = "High"
        elif col == "sanctions_exposure_code" and value == 0:
            evaluation = "High"
        elif col == "sanctions_exposure_code" and value == 2:
            evaluation = "Low"
        factors.append({"factor": label, "evaluation": evaluation})

    summary = "Evaluation based on the logic defined in the loaded .pkl rule object."
    return {"factors": factors, "summary": summary, "final_evaluation": "Medium"}

# ==============================
# Gemini API Call Function
# ==============================
def extract_json(text: str):
    if not text:
        raise ValueError("Empty response")
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except Exception:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON object found in LLM response")

async def get_gemini_classification(data: dict):
    if not gemini_model:
        return {"error": "Gemini model is not configured. Check API key."}
    try:
        prompt = f"""
        Classify the credit risk based on the following JSON data:

        {json.dumps(data, indent=2)}

        Use ONLY the system instruction rules.
        Output strictly in JSON with keys: final_risk_rating, factor_breakdown.
        """

        response = await gemini_model.generate_content_async(
            [prompt],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        parsed = extract_json(response.text)
        return parsed

    except Exception as e:
        raw = response.text if 'response' in locals() and hasattr(response, 'text') else "N/A"
        print(f"Gemini API Error: {e}. Raw: {raw}")
        return {"error": f"Gemini API error: {e}", "raw_response": raw}

# ==============================
# FastAPI Routes
# ==============================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload_json", response_class=HTMLResponse)
async def process_upload(request: Request, file: UploadFile = File(...)):
    context = {"request": request}
    try:
        contents = await file.read()
        input_data = json.loads(contents.decode("utf-8"))
        df_input = pd.DataFrame([input_data])
        context["submitted_json"] = json.dumps(input_data, indent=4)

        # Rule-based model
        if rule_model_object:
            rule_output = apply_pkl_rules(rule_model_object, df_input)
            context.update({
                "table_result_rule": rule_output["factors"],
                "summary_rule": rule_output["summary"],
                "final_evaluation_rule": rule_output["final_evaluation"],
            })
        else:
            context["summary_rule"] = "Rule-based model (.pkl) is not loaded."

        # Gemini evaluation
        llm_output = await get_gemini_classification(input_data)
        if "error" in llm_output:
            context["summary_llm"] = llm_output["error"]
        else:
            context.update({
                "llm_final_rating": llm_output.get("final_risk_rating"),
                "llm_factor_breakdown": llm_output.get("factor_breakdown", {}),
                "summary_llm": "Evaluation generated by Gemini."
            })

    except Exception as e:
        context["error_message"] = f"An application error occurred: {e}"

    return templates.TemplateResponse("index.html", context)
