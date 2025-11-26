import os
import time
import uuid
from datetime import datetime
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_LOG")
NAMESPACE_LOGS = "app-logs" 
DIMENSION = 1024 

def get_dummy_vector():
    return [0.01] * DIMENSION

def salvar_log_pinecone(
    usuario, 
    input_usuario, 
    output_ia, 
    status="Sucesso", 
    execution_time=0.0, 
    terminal_log="",
    # --- NOVOS PARÂMETROS ESTATÍSTICOS ---
    dataset_rows=0,
    dataset_cols=0,
    data_source="Desconhecido", # 'Demo' ou 'Upload'
    action_type="Create",       # 'Create' ou 'Append'
    est_input_tokens=0,         # Estimativa
    est_output_tokens=0         # Estimativa
):
    """
    Salva logs estatísticos avançados para BI.
    """
    if not PINECONE_API_KEY or not INDEX_NAME:
        return False

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)

        log_id = f"log_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # Tratamento de logs longos
        trace_limpo = str(terminal_log)
        if len(trace_limpo) > 4000:
            trace_limpo = trace_limpo[:2000] + "\n...[CORTADO]...\n" + trace_limpo[-2000:]

        metadata = {
            # --- BÁSICOS ---
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usuario": str(usuario),
            "status": status,
            "latency_seconds": float(execution_time),
            
            # --- CONTEXTO ---
            "input_prompt": str(input_usuario),
            "output_resumo": str(output_ia)[:1000],
            "crew_trace": trace_limpo,
            
            # --- ESTATÍSTICAS DE DADOS (BI) ---
            "data_rows": int(dataset_rows),
            "data_cols": int(dataset_cols),
            "data_source": str(data_source),
            "action_type": str(action_type),
            
            # --- ECONOMIA (TOKENS) ---
            # Pinecone aceita Int ou Float, ideal para somar depois
            "tokens_in_est": int(est_input_tokens),
            "tokens_out_est": int(est_output_tokens),
            "code_lines": len(str(output_ia).split('\n')),
            
            "tipo": "log_sistema_v2"
        }

        vector_valido = get_dummy_vector()

        index.upsert(
            vectors=[(log_id, vector_valido, metadata)],
            namespace=NAMESPACE_LOGS
        )
        return True

    except Exception as e:
        print(f"❌ Erro ao salvar log no Pinecone: {e}")
        return False

def ler_ultimos_logs(limit=10):
    """
    Busca os logs usando o mesmo vetor dummy como referência.
    """
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        
        # Usa o mesmo vetor de 0.01 para buscar os vizinhos (logs)
        vector_consulta = get_dummy_vector()
        
        results = index.query(
            vector=vector_consulta,
            top_k=limit,
            include_metadata=True,
            namespace=NAMESPACE_LOGS
        )
        
        logs = []
        for match in results.get('matches', []):
            if match.get('metadata'):
                logs.append(match['metadata'])
        
        # Ordena por timestamp (mais recente primeiro) se possível
        # (O Pinecone retorna por similaridade, mas como todos são iguais, a ordem pode variar)
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        return logs
    except Exception as e:
        print(f"Erro ao ler logs: {e}")
        return []