import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils import preprocess_dataframe
from chart import format_column_label

def render_main_page_and_sidebar():
    st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stApp { max-width: 1200px; margin: 0 auto; }
        .chat-message { padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; flex-direction: row; align-items: flex-start; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); animation: fadeIn 0.3s ease-in-out; }
        .chat-message.user { background: linear-gradient(135deg, #f0f7ff 0%, #e6f3ff 100%); border-left: 4px solid #4CAF50; }
        .chat-message.bot { background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-left: 4px solid #2196F3; }
        .chat-message .avatar { width: 40px; height: 40px; border-radius: 50%; margin-right: 1rem; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
        .chat-message.user .avatar { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: #fff; }
        .chat-message.bot .avatar { background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: #fff; }
        .chat-message .message { flex: 1; line-height: 1.6; }
        .feature-card { flex: 1 1 220px; min-width: 220px; max-width: 300px; background: #f8f9fa; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin: 0.5rem; }
        .feature-card-icon { font-size: 2.2rem; margin-bottom: 0.5rem; display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    """, unsafe_allow_html=True)

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'df' not in st.session_state:
        st.session_state['df'] = None

    st.markdown('<div class="subtitle">AI-Powered Data Analysis & Visualization Platform</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drag and drop file here", type=["xlsx", "xls"], label_visibility="collapsed")
    st.markdown('<div style="color:#888;font-size:0.95em;margin-top:0.5em;">Limit 200MB per file • .XLSX, .XLS</div>', unsafe_allow_html=True)

    processed_df = None
    if uploaded_file:
        try:
            if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
                processed_df = preprocess_dataframe(df)
                st.session_state['df'] = processed_df
                mem_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
                stats = {
                    "rows": len(df),
                    "cols": len(df.columns),
                    "missing": int(df.isnull().sum().sum()),
                    "mem": f"{mem_usage:.2f} MB",
                    "filename": uploaded_file.name,
                    "size": f"{uploaded_file.size/1024:.2f} KB"
                }
                st.success("✅ File uploaded successfully!")
                st.info(f"*Filename:* {stats['filename']}")
                st.info(f"*Size:* {stats['size']}")
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Total Rows", f"{stats['rows']:,}")
                with col2: st.metric("Total Columns", stats['cols'])
                with col3: st.metric("Missing Values", f"{stats['missing']:,}")
                with col4: st.metric("Memory Usage", stats['mem'])

                tabs = st.tabs(["💬 NeoStatsBot", "📊 Data Analysis", "🎨 Visualizations"])
                with tabs[0]:
                    _show_chat()
                with tabs[1]:
                    _show_data_analysis(processed_df)
                with tabs[2]:
                    _show_visualizations(processed_df)
        except Exception as exc:
            st.error(f"Error reading file: {exc}")
    else:
        _show_landing()
    return processed_df

def _show_chat():
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem; background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 2rem; border-radius: 1rem; color: white;'>
        <h2 style='color: white; margin-bottom: 0.5rem;'>NeoStatsBot Assistant</h2>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.1rem;'>Your AI-powered data analysis companion</p>
    </div>
    """, unsafe_allow_html=True)
    for msg in st.session_state['chat_history']:
        if msg["role"] == "user":
            st.markdown(f"""<div class="chat-message user"><div class="avatar">👤</div><div class="message">{msg["content"]}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="chat-message bot"><div class="avatar">🤖</div><div class="message">{msg["content"]}</div></div>""", unsafe_allow_html=True)

def _show_data_analysis(df):
    st.markdown("""<div style='display: flex; align-items: center; gap: 0.5rem; font-size: 1.3rem; margin-bottom: 1.5rem;'><span>📊</span> <b>Data Explorer</b></div>""", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, height=350)
    st.markdown("""<div style='display: flex; align-items: center; gap: 0.5rem; font-size: 1.3rem; margin: 2.5rem 0 1.5rem 0;'><span>📈</span> <b>Analytics</b></div>""", unsafe_allow_html=True)
    st.subheader("Summary Statistics")
    st.write(df.describe(include='all').T)
    st.subheader("Trends & Correlations")
    analytics_query = st.text_input("Ask for analytics (e.g., 'Show trends', 'Find outliers', 'Correlation between sales and profit'):", key="analytics_query")
    if analytics_query:
        # TODO: Implement analytics logic
        st.info("Analytics feature coming soon.")
    st.markdown("""<div style='display: flex; align-items: center; gap: 0.5rem; font-size: 1.3rem; margin: 2.5rem 0 1.5rem 0;'><span>🔍</span> <b>Data Quality</b></div>""", unsafe_allow_html=True)
    show_data_quality_report(df)

def _show_visualizations(df):
    st.markdown("""<div style='display: flex; align-items: center; gap: 0.5rem; font-size: 1.3rem; margin-bottom: 1.5rem;'><span>🎨</span> <b>Visualizations</b></div><div style='color:#666; margin-bottom:1.5rem;'>Select a chart type and columns to visualize your data. Instantly generate beautiful, interactive charts!</div>""", unsafe_allow_html=True)
    chart_types = ["bar", "line", "histogram", "scatter", "pie", "box"]
    chart_type = st.selectbox("Chart Type", chart_types, index=0)
    all_cols = df.columns.tolist()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    x_col = st.selectbox("X-axis column", all_cols, index=0)
    y_col = None
    if chart_type not in ["histogram", "pie"]:
        y_col = st.selectbox("Y-axis column", num_cols, index=0 if num_cols else None)
    elif chart_type == "pie":
        y_col = st.selectbox("Value column (for pie)", num_cols, index=0 if num_cols else None)
    fig = None
    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col)
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col)
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col)
        elif chart_type == "box":
            fig = px.box(df, x=x_col, y=y_col)
        if fig:
            fig.update_layout(
                xaxis_title=format_column_label(x_col),
                yaxis_title=format_column_label(y_col) if y_col else "",
                margin=dict(l=20, r=20, t=40, b=20),
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render chart: {e}. Ensure selected columns are appropriate for the chart type.")

def _show_landing():
    st.markdown("""
    <div style='text-align: center; margin: 3rem 0 2rem 0;'>
        <img src='https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png' width='80' alt='NeoStatsBot' style='margin-bottom: 1rem;'>
        <h1 style='color: #222; font-size: 2.8rem; margin-bottom: 0.5rem;'>Welcome to <span style='color: #4CAF50;'>NeoStats Chatbot</span>!</h1>
        <h3 style='color: #666; font-weight: 400; margin-bottom: 1.5rem;'>AI-Powered Data Analysis & Visualization Platform</h3>
        <p style='font-size: 1.2rem; color: #444; max-width: 600px; margin: 0 auto 2rem auto;'>Effortlessly analyze, visualize, and chat with your Excel data. Upload your file and let NeoStatsBot uncover insights, trends, and actionable recommendations in seconds.</p>
    </div>
    """, unsafe_allow_html=True)
    # Feature cards, setup instructions, etc. (unchanged)

def user_question_input():
    st.markdown("💬 **Ask Your Question**", unsafe_allow_html=True)
    return st.text_input("What's your question about the data?", placeholder="Type your question here...")

def display_response_and_chart(answer, chart_info, df):
    st.markdown(answer)
    if not chart_info.get("type"):
        return
    st.subheader("📊 Data Visualization")
    chart_type_override = st.selectbox(
        "Override chart type (optional):",
        options=["Auto (AI suggestion)", "bar", "line", "hist", "scatter", "pie", "box"],
        index=0
    )
    selected_type = chart_info["type"] if chart_type_override == "Auto (AI suggestion)" else chart_type_override
    MAX_PLOT_ROWS = 5000
    plot_df = df.head(MAX_PLOT_ROWS) if len(df) > MAX_PLOT_ROWS else df
    all_cols = plot_df.columns.tolist()
    num_cols = plot_df.select_dtypes(include=['number']).columns.tolist()
    default_x = chart_info.get("x") if chart_info.get("x") in all_cols else (all_cols[0] if all_cols else None)
    default_y = chart_info.get("y") if chart_info.get("y") in num_cols else (num_cols[0] if num_cols else None)
    x_axis = st.selectbox("Select X-axis column:", all_cols, index=all_cols.index(default_x) if default_x else 0)
    y_axis = None
    if selected_type not in ["hist", "pie"]:
        y_axis = st.selectbox("Select Y-axis column:", num_cols, index=num_cols.index(default_y) if default_y in num_cols else (0 if num_cols else None))
    elif selected_type == "pie":
        y_axis = st.selectbox("Select Value column (for pie chart):", num_cols, index=num_cols.index(default_y) if default_y in num_cols else (0 if num_cols else None))
    try:
        fig = None
        if selected_type == "bar":
            fig = px.bar(plot_df, x=x_axis, y=y_axis)
        elif selected_type == "line":
            fig = px.line(plot_df, x=x_axis, y=y_axis)
        elif selected_type == "hist":
            fig = px.histogram(plot_df, x=x_axis)
        elif selected_type == "scatter":
            fig = px.scatter(plot_df, x=x_axis, y=y_axis)
        elif selected_type == "pie":
            fig = px.pie(plot_df, names=x_axis, values=y_axis)
        elif selected_type == "box":
            fig = px.box(plot_df, x=x_axis, y=y_axis)
        if fig:
            fig.update_layout(
                xaxis_title=format_column_label(x_axis),
                yaxis_title=format_column_label(y_axis) if y_axis else "",
                margin=dict(l=20, r=20, t=40, b=20),
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render chart: {e}. Ensure selected columns are appropriate for the chart type.")

def show_data_quality_report(df):
    st.subheader("📋 Data Quality Report")
    issues = []
    missing_cols = df.columns[df.isnull().any()].tolist()
    if missing_cols:
        issues.append(f"*Missing Values:* {len(missing_cols)} columns have missing values: {', '.join(missing_cols)}")
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues.append(f"*Duplicate Rows:* {duplicates} duplicate rows found")
    object_cols = df.select_dtypes(include=['object']).columns
    for col in object_cols:
        try:
            if df[col].str.isnumeric().any():
                issues.append(f"*Data Type Issue:* Column '{col}' contains numeric values but is stored as text")
        except Exception:
            pass
    if issues:
        for issue in issues:
            st.warning(issue)
    else:
        st.success("✅ No major data quality issues detected!")