FROM python:3.10-slim-bookworm

WORKDIR /app

# Instalar dependências do sistema para o Ollama
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*\
    curl -fsSL https://ollama.com/install.sh | sh\
    ollama serve \
    ollama/ollama:latest

# Instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY knowledge/ ./knowledge

# Expõe as portas do Streamlit e do Ollama
EXPOSE 8501
EXPOSE 11434

# Inicia Ollama antes do Streamlit
CMD ollama serve & sleep 5 && \
    streamlit run src/app.py --server.address=0.0.0.0 --server.headless=true
