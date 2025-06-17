from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
import re
import csv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLICKHOUSE_URL = "http://localhost:8123"
CLICKHOUSE_USER = "admin"
CLICKHOUSE_PASSWORD = "admin123"
VIEW_NAME = "clickhouse_detected_anomalies"
TABLE_NAME = "obd_clean_data"

# ------------------ Utility Functions ------------------

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

# ------------------ Prompt Builder ------------------

def build_prompt(user_id: str, user_input: str) -> str:
    now = datetime.now()
    user_input_lower = user_input.lower().strip()

    # Time Filter Resolution
    if "last 2 years" in user_input_lower:
        start = now - timedelta(days=730)
    elif "last year" in user_input_lower:
        start = now - timedelta(days=365)
    elif "last month" in user_input_lower:
        start = now - timedelta(days=30)
    elif "last week" in user_input_lower or "past 7 days" in user_input_lower:
        start = now - timedelta(days=7)
    elif "yesterday" in user_input_lower:
        start = now - timedelta(days=1)
    elif match := re.search(r"since (\d{4})", user_input_lower):
        start = datetime(int(match.group(1)), 1, 1)
    else:
        start = datetime(2000, 1, 1)

    date_filter = f"timestamp >= '{start.strftime('%Y-%m-%d')} 00:00:00'"

    # Collect Data
    df_issues = run_clickhouse_query(f"""
        SELECT detected_fault, COUNT(*) AS count
        FROM {VIEW_NAME}
        WHERE user_id = '{user_id}' AND detected_fault IS NOT NULL AND {date_filter}
        GROUP BY detected_fault
        ORDER BY count DESC
        FORMAT CSVWithNames
    """)

    df_last = run_clickhouse_query(f"""
        SELECT detected_fault, MAX(timestamp) AS last_seen
        FROM {VIEW_NAME}
        WHERE user_id = '{user_id}' AND detected_fault IS NOT NULL
        GROUP BY detected_fault
        FORMAT CSVWithNames
    """)

    df_period = run_clickhouse_query(f"""
        SELECT detected_fault,
               MIN(timestamp) AS first_seen,
               MAX(timestamp) AS last_seen
        FROM {VIEW_NAME}
        WHERE user_id = '{user_id}' AND detected_fault IS NOT NULL
        GROUP BY detected_fault
        FORMAT CSVWithNames
    """)

    suggestions_map = {
        "Overheating": "🔧 Check radiator, thermostat, coolant levels, or water pump.",
        "Throttle Lag": "🛠️ Check throttle body, throttle sensor, intake manifold.",
        "Fuel Trim Drift": "💡 Inspect fuel injectors, air filter, or O2 sensors.",
        "Low Voltage": "🔋 Check battery, alternator, ground wiring.",
        "Vacuum Leak": "🧪 Inspect intake hoses, gaskets, PCV valve.",
        "RPM Fluctuation": "⚙️ Check idle control valve or crankshaft position sensor."
    }

    # Keyword Triggers
    prompt = "You are a smart vehicle assistant.\n\n"
    prompt += f"User asked: '{user_input}'\n\n"

    if "issue" in user_input_lower or "fault" in user_input_lower:
        if df_issues.empty:
            prompt += "No faults detected in the selected period."
        else:
            prompt += "📊 Detected Issues:\n"
            for _, row in df_issues.iterrows():
                fault = row['detected_fault']
                prompt += f"- {fault}: {row['count']} times\n"

    if "last" in user_input_lower or "occur" in user_input_lower:
        if not df_last.empty:
            prompt += "\n🕒 Last Occurrences:\n"
            for _, row in df_last.iterrows():
                prompt += f"- {row['detected_fault']}: {row['last_seen']}\n"

    if "since" in user_input_lower or "how long" in user_input_lower:
        if not df_period.empty:
            prompt += "\n📅 Fault Duration:\n"
            for _, row in df_period.iterrows():
                prompt += f"- {row['detected_fault']}: {row['first_seen']} to {row['last_seen']}\n"

    if "check" in user_input_lower or "replace" in user_input_lower or "fix" in user_input_lower:
        if not df_issues.empty:
            prompt += "\n🔧 Suggested Checks/Replacements:\n"
            for _, row in df_issues.iterrows():
                fault = row['detected_fault']
                if fault in suggestions_map:
                    prompt += f"- {fault}: {suggestions_map[fault]}\n"

    if prompt.strip() == "You are a smart vehicle assistant.\n\nUser asked: '{user_input}'\n\n":
        prompt += "⚠️ Please ask about specific faults, duration, or what to check."

    return prompt

# ------------------ CSV Upload Endpoint ------------------

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    content = await file.read()
    csv_text = content.decode("utf-8").replace('\r', '')
    df = pd.read_csv(StringIO(csv_text))

    user_id = "11111111-1111-1111-1111-111111111111"

    input_io = StringIO(csv_text)
    reader = csv.reader(input_io)
    header = next(reader)

    output_io = StringIO()
    writer = csv.writer(output_io, lineterminator="\n")

    for row in reader:
        if len(row) != 28:
            continue
        try:
            dt = datetime.strptime(row[27].strip(), "%Y-%m-%d")
        except ValueError:
            try:
                dt = datetime.strptime(row[27].strip(), "%m/%d/%Y")
            except ValueError:
                timestamp = "2024-01-01 00:00:00"
            else:
                timestamp = dt.strftime("%Y-%m-%d 00:00:00")
        else:
            timestamp = dt.strftime("%Y-%m-%d 00:00:00")

        writer.writerow([user_id, timestamp] + row[:27])

    final_csv = output_io.getvalue().encode("utf-8")

    try:
        insert_query = f"INSERT INTO {TABLE_NAME} FORMAT CSV"
        response = httpx.post(
            f"{CLICKHOUSE_URL}/?query={insert_query}",
            content=final_csv,
            auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD),
            headers={"Content-Type": "text/csv"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"ClickHouse error: {response.text}")
        return {"message": f"✅ Uploaded {len(df)} records with user_id {user_id}", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ------------------ Chat Endpoint ------------------

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("message")
    user_id = body.get("user_id")

    if not user_input or not user_id:
        raise HTTPException(status_code=400, detail="Both 'message' and 'user_id' are required.")

    try:
        prompt = build_prompt(user_id, user_input)
        response = get_answer_from_ollama(prompt)
        return {"response": response.strip()}
    except Exception as e:
        return {"response": f"❌ Failed to generate response: {str(e)}"}
