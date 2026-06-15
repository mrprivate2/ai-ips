FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install the package (enables ai-ips CLI)
RUN pip install --no-cache-dir -e .

# Create required directories
RUN mkdir -p logs logs/pcap src/models/saved

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.headless", "true", "--server.port", "8501"]