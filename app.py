import streamlit as st
import os

from utils import preprocess_dataframe, get_column_data_types
from user_interface import (
    render_main_page_and_sidebar,
    user_question_input,
    display_response_and_chart,
)
from llm_integration import configure_gemini_api, query_gemini_model
from chart import parse_llm_chart_suggestion

st.set_page_config(page_title="NeoStats Chatbot", layout="centered")
st.title("📊 NeoStats Chatbot")

uploaded_clean_df = render_main_page_and_sidebar()

if uploaded_clean_df is not None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY environment variable not found. Please set it to proceed.")
        # TODO: Add a link to setup instructions
    else:
        configure_gemini_api(api_key=api_key)
        user_query = user_question_input()
        if user_query:
            # Could add a spinner here for better UX
            llm_response = query_gemini_model(user_query, uploaded_clean_df)
            answer, chart_info = parse_llm_chart_suggestion(llm_response)
            display_response_and_chart(answer, chart_info, uploaded_clean_df)