import os
import json
import re
from datetime import datetime
import uuid

LOGS_DIR = "src/logs"
os.makedirs(LOGS_DIR, exist_ok=True)

def save_log(participant, llm, prompt, status, data_payload, duration_sec=None):
    """Salva um registro da execução em um arquivo JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    safe_participant_name = re.sub(r'[^a-zA-Z0-9]', '_', participant)
    
    filename = f"{timestamp}_{safe_participant_name}_{unique_id}.json"
    filepath = os.path.join(LOGS_DIR, filename)

    log_entry = {
        "log_id": f"{timestamp}_{unique_id}",
        "participant_name": participant,
        "llm_provider": llm,
        "duration_seconds": duration_sec, # <-- CAMPO ADICIONADO
        "user_prompt": prompt,
        "status": status,
        "payload": data_payload,
        # "token_usage": (
        #     result.token_usage.model_dump() 
        #     if hasattr(result, 'token_usage') and result.token_usage 
        #     else None
        # )
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"--- CRITICAL: FALHA AO SALVAR O LOG ---")
        print(f"--- Erro: {e} ---")
# --- FIM DA CONFIGURAÇÃO DE LOGS ---