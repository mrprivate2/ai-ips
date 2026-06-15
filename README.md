# 🛡 AI-IPS — AI Powered Intrusion Prevention System

![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Security](https://img.shields.io/badge/domain-cybersecurity-red)
![Status](https://img.shields.io/badge/status-active-success)

---

## 📌 Overview

**AI-IPS** is a real-time Intrusion Prevention System that uses **machine learning and behavioral analysis** to detect and automatically block malicious network activity.

It is designed as a lightweight, modular cybersecurity platform for:

- Network monitoring
- Threat detection
- Security research
- Educational use

---

## 🧠 Detection Pipeline

```
Packet Capture → Feature Extraction (9-dim) → Behavior Analysis → AI Detection → Risk Scoring → Firewall Block → Logging (JSONL)
```

---

## 📁 Project Structure

```
ai-ips/
├── src/                          # Core engine source code
│   ├── engine/
│   │   └── network_engine.py     # Main entry point — orchestrates all components
│   ├── network/
│   │   └── sniffer.py            # Packet capture & 9-feature vector extraction
│   ├── core/
│   │   └── behavior_engine.py    # Rule-based behavioral analysis (port scan, SYN flood, etc.)
│   ├── detection/
│   │   └── hybrid_detector.py    # Supervised + anomaly ML detection
│   ├── ips/
│   │   └── firewall.py           # macOS PF / Linux iptables firewall management
│   ├── security/
│   │   └── blacklist_manager.py  # IP blacklist with TTL and subnet blocking
│   ├── monitoring/
│   │   └── security_logger.py    # JSONL event logging
│   ├── training/
│   │   ├── dataset_builder.py    # Live sample collection (9-feature format)
│   │   ├── auto_trainer.py       # Model retraining pipeline
│   │   ├── training_scheduler.py # Automatic retraining triggers
│   │   └── train_anomaly_model.py# Anomaly model training
│   ├── explainability/
│   │   ├── decision_explainer.py # Human-readable attack explanations
│   │   └── feature_importance.py # Feature contribution analysis
│   ├── sync/
│   │   └── global_threat_sync.py # Firebase-based global threat sharing
│   ├── server/
│   │   └── api_server.py         # FastAPI event ingestion server
│   ├── cli/
│   │   ├── cli.py                # Typer CLI (setup, start, monitor, dashboard, retrain, status)
│   │   └── monitor.py            # Terminal-based SOC monitor
│   ├── utils/
│   │   ├── config_loader.py      # YAML config utility
│   │   └── config_validator.py   # Config validation with clear error messages
│   ├── models/
│   │   ├── __init__.py           # Model loaders
│   │   └── saved/                # Trained model files (.pkl)
│   ├── install/
│   │   └── installer.py          # System dependency installer
│   └── forensics/
│       └── pcap_logger.py        # Packet capture logging
│
├── dashboard/                    # Streamlit SOC dashboard
│   ├── app.py                    # Main dashboard entry point
│   ├── demo_generator.py         # Demo data generator (JSONL format)
│   ├── simulator.py              # API traffic simulator (9-feature vectors)
│   ├── pages/
│   │   ├── 01_overview.py        # Threat level, traffic rate, attack map
│   │   ├── 02_live_feed.py       # Real-time event feed with filtering
│   │   ├── 03_intelligence.py    # Global threat intelligence map
│   │   ├── 04_analytics.py       # Attack trends and anomaly spikes
│   │   └── 05_ai_training.py     # Dataset growth and model status
│   └── utils/
│       ├── packet_rate.py        # Network traffic rate visualization
│       ├── threat_map.py         # Global attack map builder
│       ├── leaderboard.py        # Top attacker ranking
│       ├── threat_gauge.py       # Threat level gauge widget
│       └── training_monitor.py   # Training data loader
│
├── configs/
│   ├── app_config.json           # Network, whitelist, logging config
│   └── model_config.json         # Model paths, weights, detection thresholds
│
├── logs/
│   ├── security_events.jsonl     # Security events (JSONL format)
│   ├── live_training_data.csv    # Collected training samples
│   ├── blacklist.txt             # Blocked IP list
│   └── pcap/                     # Packet captures
│
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup with CLI entry point
├── Dockerfile                    # Docker containerization
├── run.sh                        # Quick start script
└── README.md
```

---

## ⚙ Key Features

### 🔎 Real-Time Packet Capture
- Live packet capture using Scapy
- TCP / UDP / ICMP inspection
- 9-dimensional feature vector extraction (normalized packet length, port, TTL, protocol, flags, inter-arrival time, burst, port risk, external flag)

📁 `src/network/sniffer.py`

---

### 🧠 Hybrid AI Detection
- **Supervised ML** — RandomForest classifier for known attack patterns
- **Unsupervised anomaly detection** — Isolation Forest for zero-day threats
- **Hybrid scoring** — weighted combination of both models

📁 `src/detection/hybrid_detector.py`

---

### 🧩 Behavioral Engine
Rule-based detection for:
- Port scans (multiple ports accessed rapidly)
- SYN floods (high SYN rate without handshake)
- Traffic bursts (abnormal packet rate)
- Stealth attacks (extremely short inter-arrival times)

📁 `src/core/behavior_engine.py`

---

### 🔥 Automatic Firewall Blocking
- Real-time IP blocking via macOS PF or Linux iptables
- Configurable TTL for auto-unblock
- Automatic subnet detection for aggressive blockers

📁 `src/ips/firewall.py`

---

### 📊 SOC Dashboard (Streamlit)
- **Overview** — Threat level gauge, traffic rate, attack map, top attackers
- **Live Feed** — Real-time event table with IP search and filtering
- **Intelligence** — Global threat map with geolocation
- **Analytics** — Attack trends, severity distribution, anomaly spikes
- **AI Training** — Dataset growth, label distribution, feature correlation

```bash
ai-ips dashboard
# Opens at http://localhost:8501
```

---

### 📈 Self-Learning System
- Collects live traffic samples in real-time
- Automatic retraining triggered by sample count (+200 new samples) or time (6h)
- Dataset stored as CSV with 9-feature vectors and labels

📁 `src/training/`

---

### 🌐 Global Threat Sync
- Firebase Realtime Database integration
- Push detected attacks to shared global threat feed
- Auto-block IPs flagged by other nodes
- Graceful offline mode when Firebase is unavailable

📁 `src/sync/global_threat_sync.py`

---

### 🧪 Explainability
- Human-readable attack explanations
- Feature importance analysis per detection

📁 `src/explainability/`

---

## 🔧 Configuration

### `configs/app_config.json`
```json
{
  "network_interface": "en0",
  "whitelist": ["127.", "192.168.", "10.", "172."],
  "debug": true,
  "block_ttl": 120,
  "log_file": "logs/security_events.jsonl",
  "blacklist_file": "logs/blacklist.txt"
}
```

### `configs/model_config.json`
```json
{
  "supervised_model_path": "src/models/saved/supervised_model.pkl",
  "unsupervised_model_path": "src/models/saved/unsupervised_model.pkl",
  "scaler_path": "src/models/saved/scaler.pkl",
  "weight_supervised": 0.5,
  "weight_anomaly": 0.5,
  "warning_threshold": 0.45,
  "block_threshold": 0.75,
  "anomaly_threshold": 0.75
}
```

> **Note:** The engine validates both config files on startup and exits with a clear error message if any required keys are missing.

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `IPS_API_KEY` | API authentication key for `api_server.py` | `change-me-in-production` |
| `FIREBASE_DATABASE_URL` | Firebase Realtime Database URL for global sync | *(offline mode)* |

---

## ⚙ Installation

```bash
git clone https://github.com/mrprivate2/ai-ips.git
cd ai-ips
pip install -r requirements.txt
pip install -e .
```

---

## 🚀 Usage

### Quick Start with `run.sh`
```bash
./run.sh setup      # First-time setup
./run.sh start      # Start IPS engine (requires sudo)
./run.sh dashboard  # Launch SOC dashboard
./run.sh monitor    # Terminal threat monitor
./run.sh status     # Show system status
```

### CLI Commands
```bash
ai-ips setup
```

### 2. Start IPS Engine (requires root)
```bash
sudo ai-ips start
```

### 3. Launch SOC Dashboard
```bash
ai-ips dashboard
```

### 4. Terminal Monitor
```bash
ai-ips monitor
```

### 5. Retrain AI Model
```bash
ai-ips retrain
```

### 6. System Status
```bash
ai-ips status
```

---

## 📊 Example Output

```
🚫 [BLOCKED] 185.220.101.12 — PORT_SCAN (Risk: 0.90)
   Reason: Multiple ports accessed rapidly | Accessing high-risk/uncommon port
⚠️ [WARNING] 45.83.64.2 — TRAFFIC_ANOMALY (Risk: 0.45)
```

---

## 🐳 Docker

```bash
docker build -t ai-ips .
docker run -p 8501:8501 ai-ips
```

The Dockerfile uses:
- **`python:3.11-slim`** base image for smaller footprint
- **Layer caching** — dependencies installed before source copy for faster rebuilds
- **`--server.headless true`** — prevents browser open attempts in containers
- **`firebase_key.json` excluded** via `.dockerignore` to prevent credential leaks
- Creates required directories (`logs/`, `src/models/saved/`) on build

---

## 🔐 Security

- Config validation on startup with clear error messages
- API key authentication via environment variables
- Firebase credentials excluded from git (`.gitignore`)
- No hardcoded secrets in source code

AI-IPS focuses on **defensive** cybersecurity — monitoring, detection, and prevention. No offensive capabilities included.

---

## ⚠ Disclaimer

For educational and authorized environments only. Ensure you have proper authorization before monitoring network traffic.

---

## 🛠 Future Work

- Distributed sensor network
- Centralized monitoring server
- Advanced threat intelligence feeds
- Improved anomaly detection models
- Rate limiting on API server

---

## 📋 Recent Improvements

This section documents significant cleanup and fixes applied to the codebase:

### Bug Fixes
- **Dashboard JSON/JSONL format mismatch** — All 4 dashboard pages now correctly read from `security_events.jsonl` (the format the engine writes)
- **Feature vector size mismatch** — Simulator now generates 9 features matching the sniffer (was 41)
- **Duplicate comment cleanup** in demo generator

### Security Fixes
- **Hardcoded API key removed** — `api_server.py` now reads `IPS_API_KEY` from environment variable
- **Hardcoded Firebase URL removed** — `global_threat_sync.py` now reads `FIREBASE_DATABASE_URL` from environment variable
- **Firebase credentials excluded** from git via `.gitignore` and `.dockerignore`

### Dead Code Cleanup
Removed 10 unused modules and 2 empty directories:
- `src/network/feature_mapper.py`, `src/network/packet_capture.py`
- `src/sensor/agent.py` (+ empty directory)
- `src/threat_intel/threat_engine.py`, `src/threat_intel/ip_reputation.py` (+ empty directory)
- `src/training/evolution_engine.py` (duplicate of `training_scheduler.py`)
- `src/utils/common_helpers.py` (empty)
- `configs/ips_config.json` (never loaded)
- `dashboard/utils/packet_monitor.py`, `dashboard/utils/attack_map.py` (duplicates)

### Infrastructure
- **Config validation on startup** — Missing keys produce clear error messages with fix instructions
- **Dependency sync** — `requirements.txt` and `setup.py` now list identical dependencies with version pins
- **Dockerfile improvements** — Slim image, layer caching, headless mode, credential exclusion
- **`__init__.py` files** added to `dashboard/`, `dashboard/utils/`, `dashboard/pages/` for proper package imports
- **CWD-independent imports** — Dashboard pages use `sys.path` setup to work from any directory

---

## 👨‍💻 Author

**Sawan Yaduvanshi**
Cybersecurity & Software Engineering

---

## ⭐ Support

If you find this project useful:
- ⭐ Star the repository
- 🍴 Fork it
- 🛠 Contribute improvements
