
def format_column_label(raw_label):
    if not raw_label:
        return ""
    return raw_label.replace("_", " ").title()

def parse_llm_chart_suggestion(llm_response_text):
    lines = [line.strip() for line in llm_response_text.strip().splitlines()]
    chart = {"type": None, "x": None, "y": None}
    idx = -1
    for i, line in enumerate(lines):
        if line.upper().startswith("CHART:"):
            idx = i
            break
    if idx != -1:
        try:
            chart["type"] = lines[idx].split(":", 1)[1].strip().lower()
            if idx + 1 < len(lines) and lines[idx + 1].upper().startswith("X:"):
                chart["x"] = lines[idx + 1].split(":", 1)[1].strip()
            if idx + 2 < len(lines) and lines[idx + 2].upper().startswith("Y:"):
                chart["y"] = lines[idx + 2].split(":", 1)[1].strip()
        except Exception as e:
            print(f"DEBUG: Error parsing chart info: {e}")
            chart = {"type": None, "x": None, "y": None}
        return "\n".join(lines[:idx]).strip(), chart
    return llm_response_text.strip(), chart