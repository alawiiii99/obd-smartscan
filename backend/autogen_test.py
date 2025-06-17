from autogen import AssistantAgent
import httpx
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
import re

CLICKHOUSE_URL = "http://localhost:8123"
CLICKHOUSE_USER = "admin"
CLICKHOUSE_PASSWORD = "admin123"
VIEW_NAME = "clickhouse_detected_anomalies"

def run_clickhouse_query(sql: str) -> pd.DataFrame:
    try:
        response = httpx.post(
            f"{CLICKHOUSE_URL}/?query={sql.strip().replace(chr(10), ' ')}",
            auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD),
        )
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        print("❌ ClickHouse error:", e)
        return pd.DataFrame()

def get_answer_from_ollama(prompt: str) -> str:
    try:
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=60
        )
        return response.json().get("response", "⚠️ No response from Ollama.")
    except Exception as e:
        return f"❌ Ollama error: {e}"

def extract_time_filter(message: str) -> str:
    now = datetime.now()
    message = message.lower()

    if "last 2 years" in message:
        start = now - timedelta(days=730)
    elif "last year" in message:
        start = now - timedelta(days=365)
    elif "last month" in message:
        start = now - timedelta(days=30)
    elif "last week" in message or "past 7 days" in message:
        start = now - timedelta(days=7)
    elif "yesterday" in message:
        start = now - timedelta(days=1)
    elif match := re.search(r"since (\d{4})", message):
        start = datetime(int(match.group(1)), 1, 1)
    else:
        start = now - timedelta(days=14)  # default

    return f"timestamp >= '{start.strftime('%Y-%m-%d')} 00:00:00'"

def build_prompt(user_id: str, user_input: str) -> str:
    date_filter = extract_time_filter(user_input)

    sql_issues = f"""
        SELECT detected_fault, COUNT(*) AS count
        FROM {VIEW_NAME}
        WHERE user_id = '{user_id}' AND detected_fault IS NOT NULL AND {date_filter}
        GROUP BY detected_fault
        ORDER BY count DESC
        FORMAT CSVWithNames
    """
    df_issues = run_clickhouse_query(sql_issues)

    sql_last = f"""
        SELECT detected_fault, MAX(timestamp) AS last_seen
        FROM {VIEW_NAME}
        WHERE user_id = '{user_id}' AND detected_fault IS NOT NULL
        GROUP BY detected_fault
        FORMAT CSVWithNames
    """
    df_last = run_clickhouse_query(sql_last)

    sql_period = f"""
        SELECT detected_fault,
               MIN(timestamp) AS first_seen,
               MAX(timestamp) AS last_seen
        FROM {VIEW_NAME}
        WHERE user_id = '{user_id}' AND detected_fault IS NOT NULL
        GROUP BY detected_fault
        FORMAT CSVWithNames
    """
    df_period = run_clickhouse_query(sql_period)

    context = f"**📊 Vehicle Fault Summary Based on `{date_filter}`**\n\n"

    if not df_issues.empty:
        context += "🛠️ **Detected Issues:**\n"
        for _, row in df_issues.iterrows():
            context += f"- {row['detected_fault']}: {row['count']} times\n"
    else:
        context += "- No detected issues found in this period.\n"

    if not df_last.empty:
        context += "\n🕒 **Last Occurrence per Fault:**\n"
        for _, row in df_last.iterrows():
            context += f"- {row['detected_fault']}: {row['last_seen']}\n"

    if not df_period.empty:
        context += "\n📅 **Fault Time Periods:**\n"
        for _, row in df_period.iterrows():
            context += f"- {row['detected_fault']}: from {row['first_seen']} to {row['last_seen']}\n"

    prompt = f"""
You are a smart vehicle diagnostics assistant. Use the following data context pulled from ClickHouse anomalies to answer the user's query.

{context}

**User's Question:** {user_input}

Respond with a clear diagnostic explanation in professional language using headings and bullet points.
"""
    return prompt

# === Custom Ollama Agent ===

class OllamaAssistantAgent(AssistantAgent):
    def generate_reply(self, messages, **kwargs):
        prompt = messages[-1]["content"]
        return get_answer_from_ollama(prompt)

agent = OllamaAssistantAgent(name="DiagnosticsAgent")

if __name__ == "__main__":
    user_id = input("Enter user_id: ")
    user_input = input("Ask your question: ")
    prompt = build_prompt(user_id, user_input)
    response = agent.generate_reply([{"role": "user", "content": prompt}])
    print("\n--- DiagnosticsAgent Response ---\n")
    print(response)
