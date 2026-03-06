# AI-IPS Cyber Defense Platform

AI-powered intrusion prevention system with a real-time SOC dashboard.

## Features

• AI attack detection  
• Zero-day anomaly detection  
• Threat intelligence  
• Self-learning models  
• SOC monitoring dashboard  
• Global cyber attack visualization  

---

# Installation

```bash
git clone https://github.com/mrprivate2/ai-ips
cd ai-ips
pip install -e .
ai-ips install
```

---

# Run AI-IPS

Start protection engine:

```bash
ai-ips start
```

Launch SOC dashboard:

```bash
ai-ips dashboard
```

Monitor threats in terminal:

```bash
ai-ips monitor
```

Generate demo attacks:

```bash
ai-ips simulate
```

---

# Docker

```bash
docker build -t ai-ips .
docker run -p 8501:8501 ai-ips
```