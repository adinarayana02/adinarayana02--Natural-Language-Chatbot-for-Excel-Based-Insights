# gemini_api.py - Gemini LLM integration

import google.generativeai as genai
import pandas as pd
import os

_query_cache = {}

def configure_gemini_api(api_key):
    genai.configure(api_key=api_key)

def _get_dataframe_hash(df):
    sig = str(df.shape) + str(list(df.columns)) + df.head(5).to_csv(index=False)
    return hash(sig)

def query_gemini_model(user_question, data_frame):
    cache_key = (user_question, _get_dataframe_hash(data_frame))
    if cache_key in _query_cache:
        return _query_cache[cache_key]
    sample_data = data_frame.head(500).to_dict(orient="records")
    col_summaries = []
    for col in data_frame.columns:
        dtype = data_frame[col].dtype
        uniq = data_frame[col].nunique(dropna=True)
        try:
            ex = data_frame[col].dropna().unique()[:3]
        except Exception:
            ex = []
        col_summaries.append(f"- {col} ({dtype}, {uniq} distinct): e.g., {list(ex)}")
    full_desc = "\n".join(col_summaries)
    prompt = f'''
You are a data analysis assistant designed to interpret Excel/CSV datasets and answer user questions concisely.

=== DATA SNAPSHOT ===
Here's a sample of the first 10 rows from the dataset:
{sample_data}

Column Details:
{full_desc}

=== USER'S INQUIRY ===
"{user_question}"

=== YOUR TASK ===
1. Provide a brief, direct answer in clear English.
2. If a chart would be helpful for the user's question, respond strictly in the following format (no extra text, no markdown):

CHART: bar|line|hist|scatter|pie|box
X: column_name_for_x_axis
Y: column_name_for_y_axis

Only include the CHART section if a visualization is truly relevant. Do not add any conversational text around it.
'''
    try:
        llm_model = genai.GenerativeModel("gemini-2.0-flash")
        ai_response = llm_model.generate_content(prompt)
        if not ai_response.text or not ai_response.text.strip():
            raise ValueError("Received an empty or whitespace-only response from Gemini.")
        _query_cache[cache_key] = ai_response.text
        return ai_response.text
    except Exception as e:
        print(f"DEBUG: Error querying Gemini: {e}")
        return f"Sorry, couldn't process that request right now. (Error: {e})"