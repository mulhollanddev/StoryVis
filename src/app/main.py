# src/app/main.py
# -----------------
# Ponto de entrada da API (FastAPI) para o sistema StoryVis.

import sys
import os
import unicodedata  # Para sanitização de input
import re           # Para regex de segurança
import tempfile     # Para criar arquivos temporários seguros
import shutil       # Para manipulação de arquivos
from typing import Literal

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from dotenv import load_dotenv

load_dotenv()

# Adiciona o diretório raiz do projeto ao sys.path
# Permite importações de 'app.models' e 'app.services'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importações dos módulos do projeto
from app.models import ChartOutput
from app.services.crew_runner import run_storyvis_crew

# Inicializa o aplicativo FastAPI
app = FastAPI(
    title="StoryVis API",
    description="API para gerar visualizações de dados interativas usando um sistema multiagente CrewAI.",
    version="1.0.0"
)

# -----------------------------------------------------------
# Constantes e Funções de Segurança
# -----------------------------------------------------------

MAX_PROMPT_LENGTH = 1000 # Limite de caracteres para o prompt
ALLOWED_LLMS = Literal["gemini", "openai", "deepseek"] # LLMs permitidos (baseado no crew.py)
ALLOWED_EXTENSIONS = {".csv", ".xls", ".xlsx"} # Tipos de arquivo permitidos

# Mapeia caracteres de controle invisíveis para None (remoção)
control_chars = {c: None for c in range(sys.maxunicode + 1)
                 if unicodedata.category(chr(c)).startswith('C')}

def sanitize_input(text: str) -> str:
    """Remove caracteres de controle invisíveis e espaços extras."""
    return text.translate(control_chars).strip()

# Padrões regex para detecção de prompt injection
INJECTION_PATTERNS = [
    re.compile(r"ignore .* previous instructions", re.IGNORECASE),
    re.compile(r"act as if|you are now", re.IGNORECASE),
    re.compile(r"forget everything", re.IGNORECASE),
    re.compile(r"important instruction:|new goal:|your instructions are", re.IGNORECASE),
]

def detect_injection(text: str) -> bool:
    """Verifica se o texto contém padrões suspeitos de prompt injection."""
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    return False

# -----------------------------------------------------------
# Endpoint Principal da API
# -----------------------------------------------------------

@app.post(
    "/gerar-grafico",
    response_model=ChartOutput,
    summary="Gera um gráfico com base em um prompt e um arquivo de dados (opcional)",
    description="Inicia o processo multiagente, validando e sanitizando a entrada e o arquivo."
)
async def gerar_grafico_endpoint(
    llm_choice: ALLOWED_LLMS = Form(..., description="O LLM a ser usado (ex: 'gemini')"),
    user_prompt: str = Form(..., description=f"O prompt do usuário (máx. {MAX_PROMPT_LENGTH} caracteres)."),
    file: UploadFile | None = File(None, description="Arquivo de dados (CSV, XLS, XLSX).")
):
    """
    Recebe o prompt, escolha de LLM e um arquivo (opcional).
    Valida, sanitiza, salva o arquivo temporariamente e executa a crew.
    """
    
    temp_file_path: str | None = None
    temp_dir: str | None = None

    try:
        # 1. Validação de Comprimento do Prompt
        if len(user_prompt) > MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=413, # Payload Too Large
                detail=f"O prompt excede o limite de {MAX_PROMPT_LENGTH} caracteres."
            )

        # 2. Sanitização do Prompt
        sanitized_prompt = sanitize_input(user_prompt)
        if not sanitized_prompt:
            raise HTTPException(status_code=400, detail="Prompt inválido ou vazio após sanitização.")

        # 3. Detecção de Injeção no Prompt
        if detect_injection(sanitized_prompt):
            # Logar a tentativa de injeção
            print(f"WARN: Potencial Prompt Injection detectado: '{user_prompt}'")
            raise HTTPException(status_code=400, detail="Entrada suspeita detectada.")

        # 4. Processamento do Arquivo (se existir)
        if file:
            # Validação da extensão do arquivo
            filename = file.filename or ""
            extension = os.path.splitext(filename)[1].lower()
            if extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de arquivo não permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
                )

            # Salva o arquivo em um local temporário e seguro
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, filename)
            
            try:
                with open(temp_file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Falha ao salvar o arquivo: {e}")
            finally:
                file.file.close()


        # 5. Execução da Crew
        # O 'llm_choice' já é validado pelo 'ALLOWED_LLMS' (Literal)
        chart_final: ChartOutput = run_storyvis_crew(
            user_prompt=sanitized_prompt,
            llm_choice=llm_choice,
            file_path=temp_file_path # Passa o caminho (ou None)
        )
        return chart_final

    except HTTPException:
        # Re-levanta exceções HTTP (validação)
        raise
    except Exception as e:
        # Captura erros da execução da crew (ex: API do LLM falhou)
        print(f"Erro durante a execução da CrewAI: {e}")
        error_detail = f"Falha na geração do gráfico. Erro interno: {str(e)}"
        
        # Tenta extrair detalhes de erros de API
        if "APIError" in str(e) or "litellm" in str(e):
             error_detail = f"Falha na comunicação com o LLM: {str(e)}"

        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
    finally:
        # 6. Limpeza (CRUCIAL)
        # Garante que o diretório e o arquivo temporário sejam
        # removidos, mesmo se a crew falhar.
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# -----------------------------------------------------------
# Endpoint de Teste (Health Check)
# -----------------------------------------------------------

@app.get("/")
def health_check():
    """Verifica se a API está online."""
    return {"status": "ok", "service": "StoryVis API"}