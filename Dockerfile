# Usa uma imagem Python oficial e leve
FROM python:3.10-slim-bookworm

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Define variáveis de ambiente do Python para otimização
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copia APENAS o arquivo de requisitos primeiro
COPY requirements.txt .

# Instala as dependências do Python
# Usar --no-cache-dir mantém a imagem leve
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte do aplicativo (src/)
# e os arquivos de conhecimento (knowledge/)
COPY src/ ./src
COPY knowledge/ ./knowledge

# Expõe a porta padrão do Streamlit (8501)
EXPOSE 8501

# Comando para rodar a aplicação Streamlit
# --server.address=0.0.0.0 é OBRIGATÓRIO para rodar no Docker
# --server.headless=true impede o Streamlit de tentar abrir um navegador
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.headless=true"]