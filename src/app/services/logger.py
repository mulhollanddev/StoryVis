import os
import time
import uuid
from datetime import datetime
from pinecone import Pinecone
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_LOG")
NAMESPACE_LOGS = "app-logs" 

# Dimensão do seu índice (conforme seu erro anterior)
DIMENSION = 1024 

def get_dummy_vector():
    """
    Retorna um vetor válido (não-zero) para servir de placeholder.
    Preenchemos com 0.01 para não ser rejeitado pelo Pinecone.
    """
    return [0.01] * DIMENSION

def salvar_log_pinecone(
    usuario, 
    input_usuario, 
    output_ia,         # Código Python gerado
    output_narrativa,  # Texto da Narrativa (Gramática dos Gráficos)
    status="Sucesso", 
    execution_time=0.0, 
    terminal_log="",
    dataset_rows=0,
    dataset_cols=0,
    data_source="Desconhecido",
    action_type="Create",
    est_input_tokens=0,
    est_output_tokens=0
):
    """
    Salva logs estatísticos avançados para BI no Pinecone.
    """
    # Verificação de segurança se as chaves existem
    if not PINECONE_API_KEY or not INDEX_NAME:
        return False

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)

        # 1. Cria ID único para o log
        log_id = f"log_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # 2. Tratamento de Strings Longas (Corta para não estourar limite de metadata)
        trace_limpo = str(terminal_log)
        if len(trace_limpo) > 4000:
            trace_limpo = trace_limpo[:2000] + "\n...[CORTADO]...\n" + trace_limpo[-2000:]

        # 3. Monta o Metadata (Onde os dados vivem)
        metadata = {
            # --- BÁSICOS ---
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usuario": str(usuario),
            "status": status,
            "latency_seconds": float(execution_time),
            
            # --- CONTEXTO DA IA ---
            "input_prompt": str(input_usuario),
            "output_resumo": str(output_ia)[:1500],       # Código (cortado)
            "output_narrativa": str(output_narrativa)[:3000], # Narrativa (cortada)
            "crew_trace": trace_limpo,
            
            # --- ESTATÍSTICAS DE DADOS (BI) ---
            "data_rows": int(dataset_rows),
            "data_cols": int(dataset_cols),
            "data_source": str(data_source),
            "action_type": str(action_type),
            
            # --- ECONOMIA (TOKENS) ---
            "tokens_in_est": int(est_input_tokens),
            "tokens_out_est": int(est_output_tokens),
            "code_lines": len(str(output_ia).split('\n')),
            
            "tipo": "log_sistema_v3"
        }

        # 4. Upsert usando vetor dummy
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
    Busca os logs mais recentes usando o vetor dummy como âncora.
    """
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        
        # Usa o mesmo vetor de 0.01 para buscar
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
        
        # Tenta ordenar por data (string), reverso
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        return logs
    except Exception as e:
        print(f"Erro ao ler logs: {e}")
        return []
    
def salvar_feedback_pinecone(usuario, estrelas, comentario):
    """
    Salva o feedback explícito do usuário (1 a 5 estrelas + texto).
    """
    if not PINECONE_API_KEY or not INDEX_NAME:
        return False

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)

        log_id = f"feed_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        metadata = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usuario": str(usuario),
            "estrelas": int(estrelas),
            "comentario": str(comentario)[:1000], # Limita tamanho
            "tipo": "feedback_usuario" # <--- Tipo diferente para filtrar depois
        }

        # Vetor dummy
        vector_valido = get_dummy_vector()

        index.upsert(
            vectors=[(log_id, vector_valido, metadata)],
            namespace=NAMESPACE_LOGS
        )
        return True

    except Exception as e:
        print(f"❌ Erro ao salvar feedback: {e}")
        return False