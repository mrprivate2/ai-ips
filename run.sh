Here are the exact minimal commands to run your AI-IPS (clean + ready for demo) 👇

⸻

🚀 1. Go to Project Folder

cd ai-ips


⸻

🧪 2. Activate Virtual Environment

source venv/bin/activate


⸻

🛡 3. Start IPS Engine (MAIN)

sudo ai-ips start


⸻

📊 4. Open Monitor (New Terminal)

cd ai-ips
source venv/bin/activate
ai-ips monitor


⸻

🌐 5. Open Dashboard (Optional)

cd ai-ips
source venv/bin/activate
ai-ips dashboard

Open in browser:

http://localhost:8501


⸻

⚔️ 6. Test Attack (from Kali / another machine)

nmap -sS -T5 -Pn <your-ip>

Example:

nmap -sS -T5 -Pn 172.20.8.31


⸻

🛑 7. Stop IPS

Press:

CTRL + C


⸻

✅ Fast Demo Flow (for teacher)

Just run:

sudo ai-ips start

Then:

ai-ips monitor

Then run attack → show:

[BLOCKED] IP — PORT_SCAN / AI_ANOMALY


⸻