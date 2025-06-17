🚗 OBD SmartScan - Vehicle Diagnostic and Fault Detection System

OBD SmartScan is a full-stack web-based platform that allows users to upload their vehicle's OBD-II diagnostic data, analyze it using intelligent anomaly detection, and receive clear insights about their vehicle's health.

🌟 Features

- 🔐 **User Login** – Secure login and authentication system
- 📤 **CSV Upload** – Upload OBD-II datasets for analysis
- 📊 **Fault Detection** – AI-based anomaly detection using ClickHouse SQL logic
- 🤖 **Smart Assistant** – Integrated AI chatbot for vehicle-related queries
- 📈 **Visual Dashboard** – Real-time graphs via Metabase embedded in the dashboard
- 🐳 **Dockerized** – Fully containerized with FastAPI, ClickHouse, and React

🧱 Tech Stack

- **Frontend**: React 
- **Backend**: FastAPI
- **Database**: ClickHouse (with custom SQL fault detection logic)
- **AI Engine**: Ollama + Llama3 for the chatbot
- **Data Visualization**: Metabase (React embedded)
- **Deployment**: Docker + Docker Compose

🚀 How to Run

```bash
# Start the whole system
cd obd_v2
docker compose up --build


# Start backend manually
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000


# Start frontend
cd metabase-react-embed
npm install
npm run dev
