# src/app/utils.py
# -----------------
# Contém funções auxiliares e de utilidade para o app.

import os
import json
import re
import uuid
from datetime import datetime

# Define o diretório de logs
LOGS_DIR = "src/logs"
os.makedirs(LOGS_DIR, exist_ok=True)


def save_log(participant, llm, prompt, status, data_payload, duration_sec=None):
    """Salva um registro da execução em um arquivo JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    # Limpa o nome do participante para usar no nome do arquivo
    safe_participant_name = re.sub(r'[^a-zA-Z0-9]', '_', participant)
    
    filename = f"{timestamp}_{safe_participant_name}_{unique_id}.json"
    filepath = os.path.join(LOGS_DIR, filename)

    log_entry = {
        "log_id": f"{timestamp}_{unique_id}",
        "participant_name": participant,
        "llm_provider": llm,
        "duration_seconds": duration_sec, 
        "user_prompt": prompt,
        "status": status,
        "payload": data_payload 
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=4, ensure_ascii=False)
    except Exception as e:
        # Se o log falhar, imprime no console para não quebrar a UI
        print(f"--- CRITICAL: FALHA AO SALVAR O LOG ---")
        print(f"--- Erro: {e} ---")
        print(f"--- Dados do Log que falharam: {log_entry} ---")